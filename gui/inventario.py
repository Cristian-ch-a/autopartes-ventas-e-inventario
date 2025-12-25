import os
import shutil
from typing import Dict, Any, Optional, Tuple, List
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QDialog, QFormLayout, QLineEdit,
    QSpinBox, QMessageBox, QFileDialog, QComboBox, QHeaderView,
    QFrame, QDoubleSpinBox, QAbstractItemView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from controllers.producto_controller import ProductoController
from gui.ficha_tecnica import FichaTecnicaWindow  # Asumiendo que existe
from gui.form_modificar_producto import ModificarProductoForm  # Importar la forma modificada

# --- CONSTANTES Y UTILIDADES ---
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_PATH, "assets", "imagenes_productos")
os.makedirs(ASSETS_DIR, exist_ok=True)

# Definición de campos dinámicos para medidas (Debe coincidir con add_prod.py)
MEDIDAS_POR_CATEGORIA = {
    "Palier": ["A", "B", "C", "H", "L", "ABS"],
    "Amortiguador": ["Largo Extendido", "Largo Comprimido", "Rosca", "Tipo"],
    "Bieleta": ["Largo", "Rosca", "Tipo"],
    "Terminal": ["Rosca", "Largo", "Cono"],
    "Filtro": ["Diámetro", "Altura", "Rosca"],
    "Otro": []
}


def clear_layout(layout):
    """Limpia recursivamente un QLayout, eliminando widgets y sublayouts de forma segura."""
    while layout.count():
        item = layout.takeAt(0)
        if item is None:
            continue
        widget = item.widget()
        sublayout = item.layout()
        if widget:
            widget.setParent(None)
            widget.deleteLater()
        elif sublayout:
            clear_layout(sublayout)


# ============================================================== #
# 📦 Ventana principal de Inventario (InventarioWindow)
# ============================================================== #
class InventarioWindow(QWidget):
    """Ventana principal que muestra el listado de inventario y gestiona las acciones CRUD."""

    COLUMNAS_TABLA = ["Código", "Nombre", "Categoría", "Stock", "Precio (Bs)"]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Gestión de Inventario")
        self.setGeometry(100, 100, 1200, 700)
        self._set_styles()
        self._init_ui()
        self._conectar_eventos()
        self.cargar_productos()

    # ------------------ Configuración de Estilos ------------------
    def _set_styles(self):
        """Aplica estilos CSS profesionales a la ventana principal."""
        self.setStyleSheet("""
            QWidget {
                background-color: #e9ecef; 
                font-family: 'Roboto', 'Segoe UI';
                font-size: 11pt;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                gridline-color: #f1f3f5;
            }
            QHeaderView::section {
                background-color: #343a40;
                color: white;
                padding: 8px;
                border: none;
                font-weight: 600;
            }
            QPushButton {
                font-weight: 600;
                border-radius: 6px;
                padding: 8px 16px;
                min-height: 32px;
            }
            #btnAdd { background-color: #28a745; color: white; }
            #btnAdd:hover { background-color: #218838; }
            #btnEdit, #btnView { background-color: #007bff; color: white; }
            #btnEdit:hover, #btnView:hover { background-color: #0056b3; }
            #btnDelete { background-color: #dc3545; color: white; }
            #btnDelete:hover { background-color: #c82333; }
        """)

    # ------------------ Inicialización de UI ------------------
    def _init_ui(self):
        """Inicializa y organiza los componentes visuales."""
        main_layout = QVBoxLayout(self)

        # 🔹 Título principal
        title = QLabel("📦 Inventario de Autopartes")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Roboto", 20, QFont.Bold))
        title.setStyleSheet("margin: 20px 0 10px 0; color: #343a40;")
        main_layout.addWidget(title)

        # 🔹 Línea divisoria
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)

        # 🔹 Tabla de productos
        self.table = QTableWidget(0, len(self.COLUMNAS_TABLA))
        self.table.setHorizontalHeaderLabels(self.COLUMNAS_TABLA)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        # Uso explícito de QAbstractItemView para mayor claridad
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.table)

        # 🔹 Contenedor de botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.setContentsMargins(0, 15, 0, 10)

        # Botones de acción
        self.btn_add = QPushButton("➕ Añadir")
        self.btn_edit = QPushButton("✏️ Modificar")
        self.btn_delete = QPushButton("🗑️ Eliminar")
        self.btn_ver = QPushButton("🔍 Ficha Técnica")

        self.btn_add.setObjectName("btnAdd")
        self.btn_edit.setObjectName("btnEdit")
        self.btn_delete.setObjectName("btnDelete")
        self.btn_ver.setObjectName("btnView")

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_ver)
        btn_layout.addStretch()

        main_layout.addLayout(btn_layout)

    # ------------------ Conexión de Eventos ------------------
    def _conectar_eventos(self):
        """Conecta los botones a sus métodos handlers."""
        self.btn_add.clicked.connect(self._handle_abrir_formulario_insertar)
        self.btn_edit.clicked.connect(self._handle_modificar_producto)
        self.btn_delete.clicked.connect(self._handle_eliminar_producto)
        self.btn_ver.clicked.connect(self._handle_ver_ficha_seleccionada)

    # ------------------ Lógica de Datos ------------------
    def cargar_productos(self):
        """Llama al controlador para obtener y mostrar todos los productos en la tabla."""
        try:
            self.table.setRowCount(0)
            productos = ProductoController.obtener_todos() or []
            for fila in productos:
                self._insertar_fila(fila)
        except Exception as e:
            QMessageBox.critical(self, "Error de DB", f"Error al cargar productos:\n{e}")

    def _insertar_fila(self, datos_fila: Tuple[Any, ...]):
        """Inserta una única fila de producto en la tabla."""
        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)

        # Mapeo a las 5 columnas visibles (si no hay suficientes columnas en datos_fila, se usan valores vacíos)
        for col in range(len(self.COLUMNAS_TABLA)):
            val = datos_fila[col] if col < len(datos_fila) else ""
            item = QTableWidgetItem(str(val))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, col, item)

    def _obtener_codigo_seleccionado(self) -> Optional[str]:
        """Obtiene el código del producto seleccionado en la tabla."""
        fila = self.table.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Selección", "Debe seleccionar un producto de la lista.")
            return None
        item = self.table.item(fila, 0)
        if not item:
            QMessageBox.warning(self, "Selección", "Fila seleccionada inválida.")
            return None
        return item.text()

    # ------------------ Handlers de Acción ------------------
    def _handle_abrir_formulario_insertar(self):
        """Maneja el click en 'Añadir Producto'."""
        dialog = FormularioProducto(self)
        if dialog.exec_() == QDialog.Accepted:
            self._insertar_producto_en_db(dialog.obtener_datos())

    def _insertar_producto_en_db(self, datos: Dict[str, Any]):
        """
        Llama al controlador para insertar el producto.
        Corrige el mapeo de claves de la UI ('aplicacion', 'medidas', 'imagen') a
        los parámetros esperados por el controlador ('descripcion', 'medidas_dict', 'imagen_path').
        """
        if not datos.get("codigo") or not datos.get("nombre"):
            QMessageBox.warning(self, "Atención", "Código y nombre son obligatorios.")
            return

        # Hacer una copia local para no mutar un dict que pudiera ser usado fuera
        payload = dict(datos)

        # 1. Mapeo de 'aplicacion' (UI) a 'descripcion' (Controller/DB)
        if "aplicacion" in payload:
            payload["descripcion"] = payload.pop("aplicacion")

        # 2. Mapeo de 'medidas' (UI) a 'medidas_dict' (Controller)
        if "medidas" in payload:
            payload["medidas_dict"] = payload.pop("medidas")

        # 3. Mapeo de 'imagen' (UI) a 'imagen_path' (Controller)
        if "imagen" in payload:
            payload["imagen_path"] = payload.pop("imagen")

        try:
            ProductoController.insertar(**payload)
            self.cargar_productos()
            QMessageBox.information(self, "Éxito", "✅ Producto agregado correctamente.")
            return
        except Exception as e:
            QMessageBox.critical(self, "Error de Inserción", f"❌ No se pudo agregar el producto:\n{e}")

    def _handle_modificar_producto(self):
        """Maneja el click en 'Modificar Producto'."""
        codigo = self._obtener_codigo_seleccionado()
        if not codigo:
            return

        producto = ProductoController.obtener_por_codigo(codigo)

        if not producto:
            QMessageBox.critical(self, "Error", "No se encontró el producto en la base de datos.")
            return

        # Usamos la forma de modificación dedicada (asumiendo que ModificarProductoForm ya usa 'descripcion')
        ventana = ModificarProductoForm(self, producto)

        if ventana.exec_() == QDialog.Accepted:
            self.cargar_productos()

    def _handle_eliminar_producto(self):
        """Maneja el click en 'Eliminar Producto'."""
        codigo = self._obtener_codigo_seleccionado()
        if not codigo:
            return

        confirm = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Seguro que deseas eliminar el producto con código <b>{codigo}</b>?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                if ProductoController.eliminar(codigo):
                    self.cargar_productos()
                    QMessageBox.information(self, "Eliminado", "🗑️ Producto eliminado correctamente.")
                else:
                    QMessageBox.warning(self, "Error", "El producto no existe o no pudo ser eliminado.")
            except Exception as e:
                QMessageBox.critical(self, "Error de Eliminación", f"No se pudo eliminar el producto:\n{e}")

    def _handle_ver_ficha_seleccionada(self):
        """Maneja el click en 'Ver Ficha Técnica'."""
        codigo = self._obtener_codigo_seleccionado()
        if not codigo:
            return

        producto = ProductoController.obtener_por_codigo(codigo)

        if not producto:
            QMessageBox.warning(self, "Error", "No se encontró la ficha técnica del producto.")
            return

        # Abrir ficha técnica
        self.ficha_window = FichaTecnicaWindow(producto)
        self.ficha_window.show()


# ============================================================== #
# 🧾 Formulario para añadir Producto (FormularioProducto)
# ============================================================== #
class FormularioProducto(QDialog):
    """
    Formulario de diálogo usado para la inserción de nuevos productos.
    Recolecta todos los datos, incluyendo campos dinámicos y manejo de imágenes.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Añadir Nuevo Producto")
        self.setMinimumWidth(550)
        self.imagen_path: Optional[str] = None
        self._set_styles()
        self._init_ui()
        self._conectar_eventos()
        # Inicializar medidas según la categoría por defecto
        self._actualizar_medidas(self.cmb_categoria.currentText())

    def _set_styles(self):
        """Estilos del diálogo."""
        self.setStyleSheet("""
            QDialog { background-color: #f8f9fa; }
            QLabel { font-size: 11pt; padding-top: 5px; }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                padding: 8px; border: 1px solid #ced4da; border-radius: 5px;
            }
            QPushButton#btnGuardarForm {
                background-color: #28a745; color: white; font-weight: bold;
                padding: 10px; border-radius: 8px; margin-top: 15px;
            }
            QPushButton#btnGuardarForm:hover { background-color: #218838; }
        """)

    def _init_ui(self):
        """Inicializa y organiza los widgets."""
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        # 1. Campos Estándar
        self.txt_codigo = QLineEdit()
        self.txt_nombre = QLineEdit()
        self.cmb_categoria = QComboBox()
        self.cmb_categoria.addItems(list(MEDIDAS_POR_CATEGORIA.keys()))

        # 🟢 Usamos 'descripcion' en la UI
        self.txt_descripcion = QLineEdit()

        self.txt_cod_original = QLineEdit()
        self.txt_stock = QSpinBox()
        self.txt_stock.setMaximum(999999)
        self.txt_stock.setMinimum(0)
        self.txt_precio = QDoubleSpinBox()
        self.txt_precio.setMaximum(999999.99)
        self.txt_precio.setDecimals(2)
        # Usamos sufijo en lugar de prefix para que la edición sea más clara; si prefieres prefix, cámbialo.
        self.txt_precio.setSuffix(" Bs")

        self.btn_imagen = QPushButton("📷 Seleccionar Imagen")

        # Placeholders más claros
        self.txt_codigo.setPlaceholderText("Código (obligatorio)")
        self.txt_nombre.setPlaceholderText("Nombre (obligatorio)")
        self.txt_descripcion.setPlaceholderText("Descripción / Aplicación")
        self.txt_cod_original.setPlaceholderText("Código del fabricante (opcional)")

        form_layout.addRow("Código *:", self.txt_codigo)
        form_layout.addRow("Nombre *:", self.txt_nombre)
        form_layout.addRow("Categoría:", self.cmb_categoria)
        form_layout.addRow("Descripción:", self.txt_descripcion)
        form_layout.addRow("Código Original:", self.txt_cod_original)
        form_layout.addRow("Stock:", self.txt_stock)
        form_layout.addRow("Precio (Bs):", self.txt_precio)
        form_layout.addRow(self.btn_imagen)

        main_layout.addLayout(form_layout)

        # 2. Contenedor de medidas dinámicas
        medidas_label = QLabel("Detalle de Medidas:")
        medidas_label.setStyleSheet("font-weight: bold; margin-top: 10px; color: #495057;")
        main_layout.addWidget(medidas_label)

        self.medidas_container_layout = QVBoxLayout()
        self.medidas_widgets: Dict[str, QLineEdit] = {}
        main_layout.addLayout(self.medidas_container_layout)

        # 3. Botón Guardar
        self.btn_guardar = QPushButton("💾 Guardar Producto")
        self.btn_guardar.setObjectName("btnGuardarForm")
        main_layout.addWidget(self.btn_guardar)

    def _conectar_eventos(self):
        """Conecta eventos específicos del diálogo."""
        self.cmb_categoria.currentTextChanged.connect(self._actualizar_medidas)
        self.btn_imagen.clicked.connect(self._seleccionar_imagen)
        self.btn_guardar.clicked.connect(self._on_guardar_clicked)

    # ------------------ Lógica Dinámica ------------------
    def _actualizar_medidas(self, categoria: str):
        """Actualiza dinámicamente los campos de entrada de medidas."""
        clear_layout(self.medidas_container_layout)
        self.medidas_widgets.clear()

        campos = MEDIDAS_POR_CATEGORIA.get(categoria, [])
        form_medidas = QFormLayout()

        for campo in campos:
            etiqueta = QLabel(campo + ":")
            entrada = QLineEdit()
            entrada.setPlaceholderText(f"Ingrese {campo}")
            self.medidas_widgets[campo] = entrada
            form_medidas.addRow(etiqueta, entrada)

        self.medidas_container_layout.addLayout(form_medidas)
        self.medidas_container_layout.addStretch()

    def _seleccionar_imagen(self):
        """Abre el diálogo para seleccionar la imagen del producto."""
        file, _ = QFileDialog.getOpenFileName(self, "Seleccionar Imagen", "", "Imágenes (*.png *.jpg *.jpeg)")
        if file:
            self.imagen_path = file
            QMessageBox.information(self, "Imagen seleccionada", f"Se cargará: {os.path.basename(file)}")

    def _on_guardar_clicked(self):
        """Valida los campos críticos antes de cerrar el diálogo."""
        if not self.txt_codigo.text().strip() or not self.txt_nombre.text().strip():
            QMessageBox.warning(self, "Atención", "Código y Nombre son obligatorios.")
            return

        self.accept()

    # ------------------ Retorno de Datos ------------------
    def obtener_datos(self) -> Dict[str, Any]:
        """
        Recolecta todos los datos del formulario.
        Devuelve claves UI que luego serán mapeadas por InventarioWindow a las esperadas por el controlador.
        """
        imagen_relativa: Optional[str] = None
        if self.imagen_path:
            nombre_archivo = os.path.basename(self.imagen_path)
            destino = os.path.join(ASSETS_DIR, nombre_archivo)

            try:
                # Copia profesional: solo si las rutas son diferentes
                if os.path.abspath(self.imagen_path) != os.path.abspath(destino):
                    shutil.copy2(self.imagen_path, destino)
                imagen_relativa = nombre_archivo
            except Exception as e:
                QMessageBox.warning(self, "Advertencia", f"No se pudo copiar la imagen: {e}")
                imagen_relativa = None

        medidas = {
            campo: widget.text().strip()
            for campo, widget in self.medidas_widgets.items()
            if widget.text().strip()
        }

        return {
            "codigo": self.txt_codigo.text().strip(),
            "nombre": self.txt_nombre.text().strip(),
            # Mantengo ambas claves por compatibilidad: algunos módulos podrían usar 'tipo_repuesto'
            "tipo_repuesto": self.cmb_categoria.currentText(),
            "categoria": self.cmb_categoria.currentText(),

            # Aquí se llama 'aplicacion' por compatibilidad con la lógica en InventarioWindow
            "aplicacion": self.txt_descripcion.text().strip(),

            "cod_original": self.txt_cod_original.text().strip(),

            # 'medidas' será remapeado a 'medidas_dict' por InventarioWindow
            "medidas": medidas,

            "stock": int(self.txt_stock.value()),
            "precio": float(self.txt_precio.value()),
            "imagen": imagen_relativa
        }
