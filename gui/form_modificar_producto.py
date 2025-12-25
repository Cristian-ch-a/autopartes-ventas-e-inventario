import os
import json
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QMessageBox, QFileDialog, QSpinBox, QWidget, QFormLayout,
    QDoubleSpinBox # Uso de QDoubleSpinBox para manejar precios de forma nativa
)
from PyQt5.QtGui import QPixmap, QValidator
from controllers.producto_controller import ProductoController
from typing import Dict, Any, Optional

# --- Constantes y Configuración de Rutas ---

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "imagenes_productos")

# Definición de campos dinámicos para medidas (puede ser centralizado en un archivo de configuración si es grande)
MEDIDAS_POR_CATEGORIA = {
    "Palier": ["A", "B", "C", "H", "L", "ABS"],
    "Amortiguador": ["Largo Extendido", "Largo Comprimido", "Rosca", "Tipo"],
    "Filtro": ["Diámetro", "Altura", "Rosca"],
    "Otro": []
}

# --- Clase Principal de la Forma ---

class ModificarProductoForm(QDialog):
    """
    Formulario para la modificación de productos existentes.
    Gestiona la carga de datos, la interfaz dinámica de medidas y la interacción con el controlador.
    """
    
    def __init__(self, parent: QWidget, producto: Dict[str, Any]):
        """Inicializa la forma con los datos del producto a modificar."""
        super().__init__(parent)
        self.setWindowTitle("Modificar Producto")
        self.setMinimumWidth(600)
        
        # Almacenamiento seguro de datos iniciales
        self.producto = producto
        self.codigo_original = producto.get("codigo")
        
        # Ruta de la imagen actual
        self.imagen_path_actual = producto.get("imagen_path") or producto.get("imagen")
        self.nueva_imagen_seleccionada = False
        
        # Inicialización de la Interfaz
        self._crear_widgets()
        self._organizar_layout()
        self._conectar_eventos()
        
        # Carga de datos
        self._cargar_datos_producto()

    # ------------------ Métodos de Creación y Organización de UI ------------------

    def _crear_widgets(self):
        """Inicializa todos los widgets del formulario."""
        
        # Campos de texto y entrada estándar
        self.codigo = QLineEdit()
        self.nombre = QLineEdit()
        
        # Categoria (ComboBox)
        self.categoria = QComboBox()
        self.categoria.addItems(list(MEDIDAS_POR_CATEGORIA.keys()))
        
        # CAMBIO CLAVE: Renombrado de aplicacion a descripcion
        self.descripcion = QLineEdit() 
        
        self.cod_original = QLineEdit()
        
        # Stock (SpinBox)
        self.stock = QSpinBox()
        self.stock.setMaximum(999999)
        self.stock.setMinimum(0)
        
        # Precio (DoubleSpinBox para manejo profesional de floats)
        self.precio = QDoubleSpinBox()
        self.precio.setMaximum(999999.99)
        self.precio.setMinimum(0.00)
        self.precio.setPrefix("Bs. ")
        self.precio.setDecimals(2)
        
        # Contenedor de medidas dinámicas
        self.medidas_widgets: Dict[str, QLineEdit] = {}
        self.medidas_container = QVBoxLayout()
        
        # Imagen Preview
        self.lbl_imagen = QLabel("Sin imagen")
        self.lbl_imagen.setFixedSize(120, 120)
        self.lbl_imagen.setAlignment(Qt.AlignCenter)
        self.lbl_imagen.setStyleSheet("border: 1px solid #ccc;")
        self.btn_img = QPushButton("Cambiar imagen")
        
        # Botones de Acción
        self.btn_guardar = QPushButton("Guardar Cambios")
        self.btn_cancel = QPushButton("Cancelar")

    def _organizar_layout(self):
        """Organiza los widgets en el layout principal."""
        
        main_layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Organización de campos estándar
        form_layout.addRow("Código:", self.codigo)
        form_layout.addRow("Nombre:", self.nombre)
        form_layout.addRow("Categoría:", self.categoria)
        form_layout.addRow("Descripción:", self.descripcion) # Etiqueta y campo renombrados
        form_layout.addRow("Cód. Original:", self.cod_original)
        form_layout.addRow("Stock:", self.stock)
        form_layout.addRow("Precio:", self.precio)
        
        # Organización de campos dinámicos de medidas
        form_layout.addRow("Medidas (Detalle):", QWidget()) 
        form_layout.addRow(self.medidas_container)

        # Organización de la imagen
        img_row = QHBoxLayout()
        img_row.addWidget(self.lbl_imagen)
        img_row.addWidget(self.btn_img)
        img_row.addStretch() # Empuja el botón al borde
        form_layout.addRow("Imagen:", img_row)

        main_layout.addLayout(form_layout)

        # Organización de botones
        btns_layout = QHBoxLayout()
        btns_layout.addWidget(self.btn_guardar)
        btns_layout.addWidget(self.btn_cancel)
        main_layout.addLayout(btns_layout)

        self.setLayout(main_layout)

    def _conectar_eventos(self):
        """Conecta las señales de los widgets a sus respectivos slots (métodos)."""
        self.categoria.currentTextChanged.connect(self._actualizar_medidas)
        self.btn_img.clicked.connect(self._seleccionar_imagen)
        self.btn_guardar.clicked.connect(self._guardar)
        self.btn_cancel.clicked.connect(self.reject)
    
    # ------------------ Métodos de Carga de Datos y Lógica ------------------

    def _cargar_datos_producto(self):
        """Carga los datos del producto existente en los campos de la interfaz."""
        p = self.producto
        
        self.codigo.setText(p.get("codigo", ""))
        self.nombre.setText(p.get("nombre", ""))
        self.categoria.setCurrentText(p.get("categoria", "") or list(MEDIDAS_POR_CATEGORIA.keys())[0])
        
        # CAMBIO CLAVE: Cargar el valor de 'descripcion' al widget renombrado
        self.descripcion.setText(p.get("descripcion", "")) 
        
        self.cod_original.setText(p.get("cod_original", ""))
        self.stock.setValue(int(p.get("stock", 0)))
        
        # Usar el DoubleSpinBox para el precio
        self.precio.setValue(float(p.get("precio", 0.0)))

        # 1. Cargar la estructura dinámica de medidas
        self._actualizar_medidas(self.categoria.currentText()) 
        
        # 2. Rellenar los campos de medidas con los datos existentes
        medidas_dict = p.get("medidas") or {}
        # El controlador ya debería retornar el dict limpio, pero añadimos manejo si viene como string
        if isinstance(medidas_dict, str):
            try:
                medidas_dict = json.loads(medidas_dict)
            except Exception:
                medidas_dict = {}

        for k, v in medidas_dict.items():
            if k in self.medidas_widgets:
                self.medidas_widgets[k].setText(str(v))

        # 3. Cargar la imagen
        self._cargar_imagen_preview(self.imagen_path_actual)
        
    def _cargar_imagen_preview(self, path: Optional[str]):
        """Muestra la imagen del producto en el QLabel si existe."""
        
        if not path:
            self.lbl_imagen.setText("Sin imagen")
            return
            
        # Determinar la ruta absoluta si es solo el nombre de archivo
        if not os.path.isabs(path):
            abs_img_path = os.path.join(ASSETS_DIR, os.path.basename(path))
        else:
            abs_img_path = path

        if os.path.exists(abs_img_path):
            pix = QPixmap(abs_img_path).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_imagen.setPixmap(pix)
            self.imagen_path_actual = abs_img_path
        else:
            self.lbl_imagen.setText("Imagen no encontrada")
            self.imagen_path_actual = None

    def _actualizar_medidas(self, categoria: str):
        """
        Lógica dinámica para mostrar los campos de medidas relevantes
        según la categoría seleccionada.
        """
        # Limpiar widgets existentes del contenedor
        for i in reversed(range(self.medidas_container.count())):
            widget_item = self.medidas_container.takeAt(i)
            if widget_item.widget():
                widget_item.widget().deleteLater()
            
        self.medidas_widgets = {}

        campos = MEDIDAS_POR_CATEGORIA.get(categoria, [])
        form_medidas = QFormLayout() # Usamos un QFormLayout interno para mejor alineación
        
        for campo in campos:
            inp = QLineEdit()
            inp.setPlaceholderText("Valor numérico o deje vacío")
            self.medidas_widgets[campo] = inp
            form_medidas.addRow(QLabel(campo + ":"), inp)
            
        self.medidas_container.addLayout(form_medidas)

    def _seleccionar_imagen(self):
        """Abre un diálogo para seleccionar una nueva imagen."""
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar imagen", "", "Imágenes (*.png *.jpg *.jpeg)")
        if path:
            self.imagen_path_actual = path
            self._cargar_imagen_preview(path)
            self.nueva_imagen_seleccionada = True

    def _obtener_datos_de_formulario(self) -> Dict[str, Any]:
        """Recolecta y prepara los datos del formulario para enviarlos al controlador."""
        
        # 1. Recolección de medidas dinámicas
        medidas = {
            k: v.text().strip() 
            for k, v in self.medidas_widgets.items() 
            if v.text().strip()
        }
        
        # 2. Determinación del nombre de la imagen a guardar
        imagen_nombre = None
        if self.imagen_path_actual and self.nueva_imagen_seleccionada:
            # Si se seleccionó una nueva imagen, guardamos su nombre de archivo.
            imagen_nombre = os.path.basename(self.imagen_path_actual)
        elif self.imagen_path_actual:
             # Si no se cambió, pero ya tenía una, conservamos el nombre de archivo existente.
             imagen_nombre = os.path.basename(self.imagen_path_actual)
            
        # 3. Creación del diccionario de datos
        data = {
            "nombre": self.nombre.text().strip(),
            "categoria": self.categoria.currentText(),
            "descripcion": self.descripcion.text().strip(), # CLAVE: Envía como 'descripcion'
            "cod_original": self.cod_original.text().strip(),
            "stock": self.stock.value(),
            "precio": self.precio.value(), # Usar el valor float del QDoubleSpinBox
            "medidas": medidas,
            "imagen": imagen_nombre
        }
        
        return data

    def _guardar(self):
        """
        Valida los datos y llama al controlador para actualizar el producto.
        """
        nuevo_codigo = self.codigo.text().strip()
        
        if not nuevo_codigo:
            QMessageBox.warning(self, "Error de Validación", "El Código no puede estar vacío.")
            return

        try:
            data = self._obtener_datos_de_formulario()
            
            # Si el código fue cambiado, lo incluimos en los datos a actualizar
            if nuevo_codigo != self.codigo_original:
                data["codigo"] = nuevo_codigo
                
            # Llamada al controlador
            exito = ProductoController.actualizar(self.codigo_original, **data)
            
            if exito:
                QMessageBox.information(self, "Éxito", "Producto actualizado correctamente.")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "No se encontró el producto para actualizar.")

        except ValueError as ve:
            QMessageBox.warning(self, "Error de Formato", f"Error en los datos: {ve}")
        except Exception as e:
            # El controlador lanza excepciones de IntegrityError si el nuevo código ya existe
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el producto: {e}")