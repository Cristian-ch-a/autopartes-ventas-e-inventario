import os
import shutil
from typing import Dict, Any, List, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QComboBox, QLineEdit,
    QLabel, QPushButton, QHBoxLayout, QMessageBox, QSpinBox,
    QDoubleSpinBox, QFrame, QGridLayout # Añadidos para mejorar UI
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from controllers.producto_controller import ProductoController # Asegúrate de que este controlador exista

# --- CONSTANTES DE CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "imagenes_productos")
os.makedirs(ASSETS_DIR, exist_ok=True)

# Centralización de las medidas (debe coincidir con inventario.py)
MEDIDAS_POR_CATEGORIA = {
    "Palier": ["A", "B", "C", "H", "L", "ABS"],
    "Amortiguador": ["Largo Extendido", "Largo Comprimido", "Rosca", "Tipo"],
    "Filtro": ["Diámetro", "Altura", "Rosca"],
    "Otro": []
}

# --- CLASE PRINCIPAL ---
class AddProductWindow(QWidget):
    """
    Ventana de formulario para la inserción de un nuevo producto.
    Implementa la lógica dinámica para los campos de medidas según la categoría.
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("➕ Añadir Nuevo Producto")
        self.setGeometry(450, 200, 650, 750)
        self.imagen_path: Optional[str] = None # Ruta absoluta de la imagen seleccionada
        self._set_styles()
        self._init_ui()

    # ------------------ Configuración y Estilos ------------------
    def _set_styles(self):
        """Aplica estilos CSS para una interfaz más amigable y profesional."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI';
                font-size: 11pt;
            }
            QLabel {
                padding-top: 5px;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 5px;
            }
            QPushButton#btnGuardar {
                background-color: #007bff;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
                margin-top: 15px;
            }
            QPushButton#btnGuardar:hover {
                background-color: #0056b3;
            }
        """)

    # ------------------ Inicialización de UI ------------------
    def _init_ui(self):
        """Inicializa y organiza todos los widgets del formulario."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        title = QLabel("Detalles del Nuevo Producto")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.layout.addWidget(title, alignment=Qt.AlignCenter)
        
        separator = QFrame(); separator.setFrameShape(QFrame.HLine)
        self.layout.addWidget(separator)

        # Formulario principal
        form = QFormLayout()
        form.setSpacing(12)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        # 1. Campos Estándar
        self.txt_codigo = QLineEdit()
        self.txt_nombre = QLineEdit()
        self.cmb_categoria = QComboBox() # Renombramos cmb_tipo a cmb_categoria
        self.cmb_categoria.addItems(list(MEDIDAS_POR_CATEGORIA.keys()))
        
        # 🟢 CAMBIO CLAVE: Renombrar 'aplicacion' a 'descripcion'
        self.txt_descripcion = QLineEdit() 
        
        self.txt_cod_original = QLineEdit()
        self.txt_stock = QSpinBox(); self.txt_stock.setMaximum(999999); self.txt_stock.setMinimum(0)
        
        # 🟢 MEJORA: Uso de QDoubleSpinBox para manejar el precio (floats)
        self.txt_precio = QDoubleSpinBox()
        self.txt_precio.setMaximum(999999.99)
        self.txt_precio.setDecimals(2)
        self.txt_precio.setPrefix("Bs ")

        # Botón de Imagen
        btn_imagen = QPushButton("📷 Seleccionar Imagen")
        btn_imagen.clicked.connect(self._seleccionar_imagen)

        # Añadir al FormLayout
        form.addRow("Código:", self.txt_codigo)
        form.addRow("Nombre:", self.txt_nombre)
        form.addRow("Categoría:", self.cmb_categoria)
        form.addRow("Descripción:", self.txt_descripcion) # Etiqueta corregida
        form.addRow("Cód. Original:", self.txt_cod_original)
        form.addRow("Stock:", self.txt_stock)
        form.addRow("Precio:", self.txt_precio)
        form.addRow("Imagen:", btn_imagen)
        
        self.layout.addLayout(form)
        
        # 2. Campos Dinámicos para Medidas
        medidas_title = QLabel("📏 Especificaciones Técnicas (Medidas):")
        medidas_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        medidas_title.setStyleSheet("margin-top: 15px; color: #495057;")
        self.layout.addWidget(medidas_title)

        self.medidas_box = QVBoxLayout()
        self.medidas_inputs: Dict[str, QLineEdit] = {}
        self.layout.addLayout(self.medidas_box)

        # 3. Botón Guardar
        btn_guardar = QPushButton("Guardar Producto")
        btn_guardar.setObjectName("btnGuardar")
        btn_guardar.clicked.connect(self._guardar_producto)
        self.layout.addWidget(btn_guardar)

        # Conexión dinámica
        self.cmb_categoria.currentTextChanged.connect(self._actualizar_campos_dinamicos)
        self._actualizar_campos_dinamicos(self.cmb_categoria.currentText()) # Inicializar

    # ------------------ Lógica Dinámica y Eventos ------------------
    def _actualizar_campos_dinamicos(self, categoria: str):
        """
        Limpia los campos dinámicos y los recrea basados en la categoría seleccionada.
        """
        # Limpiar campos anteriores (función helper para seguridad)
        while self.medidas_box.count():
            item = self.medidas_box.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    item.layout().takeAt(0).widget().deleteLater()

        self.medidas_inputs.clear()
        
        # Usamos QFormLayout dentro para que las medidas se alineen correctamente
        medidas_form_layout = QFormLayout()
        medidas_form_layout.setSpacing(8)
        
        campos_medidas = MEDIDAS_POR_CATEGORIA.get(categoria, [])

        for m in campos_medidas:
            inp = QLineEdit()
            inp.setPlaceholderText("Ingrese valor o deje vacío")
            
            # Almacenar en el diccionario de inputs
            self.medidas_inputs[m] = inp
            
            # Añadir al sub-layout
            medidas_form_layout.addRow(QLabel(f"{m}:"), inp)
            
        self.medidas_box.addLayout(medidas_form_layout)
        self.medidas_box.addStretch() # Añadir estiramiento para empujar los campos hacia arriba

    def _seleccionar_imagen(self):
        """Permite al usuario seleccionar una imagen para el producto."""
        from PyQt5.QtWidgets import QFileDialog # Import local por si acaso
        
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar imagen", "", "Imágenes (*.png *.jpg *.jpeg)")
        if path:
            self.imagen_path = path
            QMessageBox.information(self, "Imagen seleccionada", f"Se cargará: {os.path.basename(path)}")

    def _guardar_producto(self):
        """
        Recolecta los datos, realiza validaciones y llama al controlador para la inserción.
        """
        codigo = self.txt_codigo.text().strip()
        nombre = self.txt_nombre.text().strip()
        
        # Validaciones mínimas
        if not codigo or not nombre:
            QMessageBox.warning(self, "Atención", "Código y Nombre son obligatorios.")
            return

        # 1. Procesar Medidas
        medidas_dict = {
            k: v.text().strip() 
            for k, v in self.medidas_inputs.items() 
            if v.text().strip()
        }
        
        # 2. Manejo y Copia de Imagen (si fue seleccionada)
        imagen_relativa: Optional[str] = None
        if self.imagen_path:
            nombre_archivo = os.path.basename(self.imagen_path)
            destino = os.path.join(ASSETS_DIR, nombre_archivo)
            try:
                # Copiar solo si el archivo de origen no está ya en el destino
                if os.path.abspath(self.imagen_path) != os.path.abspath(destino):
                    shutil.copy2(self.imagen_path, destino)
                imagen_relativa = nombre_archivo
            except Exception as e:
                QMessageBox.warning(self, "Advertencia", f"No se pudo copiar la imagen: {e}")
                imagen_relativa = None

        # 3. Estructura de Datos (CLAVE: usar 'descripcion' y 'medidas_dict')
        try:
            ProductoController.insertar(
                codigo=codigo,
                nombre=nombre,
                # Usamos la misma categoría para tipo_repuesto y categoria si tu DB lo requiere
                tipo_repuesto=self.cmb_categoria.currentText(),
                categoria=self.cmb_categoria.currentText(),
                
                # 🟢 CORRECCIÓN CLAVE: Usamos 'descripcion' en lugar de 'aplicacion'
                descripcion=self.txt_descripcion.text().strip(), 
                
                cod_original=self.txt_cod_original.text().strip(),
                # CLAVE: Usar 'medidas_dict' para ser coherente con el controlador
                medidas_dict=medidas_dict,
                
                stock=self.txt_stock.value(),
                # 🟢 MEJORA: Usar el valor nativo del QDoubleSpinBox (ya es float)
                precio=self.txt_precio.value(),
                
                imagen_path=imagen_relativa
            )
            QMessageBox.information(self, "Éxito", "✅ Producto añadido correctamente.")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error de Inserción", f"❌ No se pudo guardar el producto:\n{e}")