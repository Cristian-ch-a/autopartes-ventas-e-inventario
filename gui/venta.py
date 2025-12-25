# gui/venta.py
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QMessageBox, QSpinBox,
    QGroupBox, QFormLayout, QHeaderView, QSpacerItem, QSizePolicy, 
    QFrame, QStyle, QAbstractItemView
)
from PyQt5.QtGui import QFont, QIcon, QColor, QBrush, QCursor
from PyQt5.QtCore import Qt, QLocale, QSize
from controllers.producto_controller import ProductoController
from controllers.venta_controller import VentaController

class RegistrarVentaWindow(QWidget):
    """
    Ventana de Punto de Venta (POS) Profesional.
    Versión corregida: Sin errores de CSS 'Unknown property cursor'.
    """
    
    def __init__(self, usuario_id):
        super().__init__()
        # Guardamos el ID tal cual llega (puede ser str o int)
        self.usuario_id_raw = usuario_id 
        self.producto_seleccionado = None
        
        # Configuración de Ventana
        self.setWindowTitle(f"🛒 Punto de Venta Profesional - Usuario: {self.usuario_id_raw}")
        self.setGeometry(100, 100, 1100, 800) 
        
        # Inicialización
        self._set_styles()
        self._init_ui()
        self.cargar_historial() 

    def _set_styles(self):
        """
        Define la hoja de estilos (CSS/QSS) para una apariencia Premium.
        CORRECCIÓN: Se eliminó 'cursor: pointer' para evitar errores en consola.
        """
        self.setStyleSheet("""
            /* --- FONDO Y FUENTE GLOBAL --- */
            QWidget {
                background-color: #f0f2f5;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                color: #333333;
            }

            /* --- TARJETAS (GROUPBOX) --- */
            QGroupBox {
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                border-radius: 10px;
                margin-top: 25px; /* Espacio para el título */
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                left: 15px;
                color: #0056b3; /* Azul Corporativo */
                font-weight: bold;
                font-size: 12pt;
                background-color: #f0f2f5; 
            }

            /* --- INPUTS --- */
            QLineEdit, QSpinBox {
                padding: 10px;
                border: 1px solid #ced4da;
                border-radius: 6px;
                background-color: #ffffff;
                font-size: 14px;
            }
            QLineEdit:focus, QSpinBox:focus {
                border: 2px solid #80bdff;
                background-color: #fafdff;
            }

            /* --- BOTONES ESTÁNDAR --- */
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #0056b3;
                /* cursor: pointer;  <-- ELIMINADO POR CAUSAR ERROR EN CONSOLA */
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            
            /* --- BOTÓN DE VENTA (Acción Principal) --- */
            #BtnVender {
                background-color: #28a745;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
            }
            #BtnVender:hover {
                background-color: #218838;
            }
            #BtnVender:disabled {
                background-color: #94d3a2;
                color: #e9ecef;
            }

            /* --- TABLA DE HISTORIAL --- */
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                gridline-color: #f1f1f1;
                selection-background-color: #e8f0fe;
                selection-color: #1967d2;
                outline: 0;
            }
            QHeaderView::section {
                background-color: #343a40;
                color: #ffffff;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
            
            /* --- LABELS DE DATOS --- */
            QLabel {
                color: #495057;
            }
        """)

    def _init_ui(self):
        """Construye la estructura de la interfaz."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        # 1. Título Superior
        header_layout = QHBoxLayout()
        lbl_titulo = QLabel("Panel de Facturación")
        lbl_titulo.setStyleSheet("font-size: 18pt; font-weight: bold; color: #212529; border: none;")
        header_layout.addWidget(lbl_titulo)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # 2. Panel Superior
        top_panel = QHBoxLayout()
        top_panel.setSpacing(20)
        top_panel.addWidget(self._create_search_box(), 60)
        top_panel.addWidget(self._create_summary_box(), 40)
        main_layout.addLayout(top_panel)
        
        # 3. Separador visual
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #dcdcdc; margin-top: 10px; margin-bottom: 10px;")
        main_layout.addWidget(line)

        # 4. Panel Inferior
        main_layout.addWidget(self._create_history_box())

    def _create_search_box(self) -> QGroupBox:
        """Crea la tarjeta de búsqueda."""
        box = QGroupBox("1. Búsqueda y Detalles")
        layout = QVBoxLayout(box)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 25, 20, 20)
        
        # --- Buscador ---
        h_search = QHBoxLayout()
        
        self.input_codigo = QLineEdit()
        self.input_codigo.setPlaceholderText("🔍 Escanear o escribir código (ej: GSP-123)")
        self.input_codigo.setMinimumHeight(40)
        self.input_codigo.returnPressed.connect(self.buscar_producto)
        
        btn_buscar = QPushButton("Buscar")
        btn_buscar.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload)) 
        btn_buscar.setMinimumHeight(40)
        # CORRECCIÓN: Usamos Python para poner la manito en lugar de CSS
        btn_buscar.setCursor(QCursor(Qt.PointingHandCursor)) 
        btn_buscar.clicked.connect(self.buscar_producto)
        
        h_search.addWidget(self.input_codigo)
        h_search.addWidget(btn_buscar)
        layout.addLayout(h_search)
        
        # --- Detalles del Producto ---
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: #f8f9fa; border-radius: 6px; border: 1px solid #e9ecef;")
        info_layout = QVBoxLayout(info_frame)
        
        self.lbl_nombre = QLabel("---")
        self.lbl_nombre.setStyleSheet("font-size: 14pt; font-weight: bold; color: #343a40;")
        self.lbl_nombre.setWordWrap(True)
        
        details_layout = QHBoxLayout()
        self.lbl_stock = QLabel("Stock: 0")
        self.lbl_stock.setStyleSheet("color: #6c757d; font-size: 11pt;")
        
        self.lbl_precio = QLabel("Precio: 0.00 Bs")
        self.lbl_precio.setStyleSheet("color: #007bff; font-weight: bold; font-size: 12pt;")
        
        details_layout.addWidget(self.lbl_stock)
        details_layout.addStretch()
        details_layout.addWidget(self.lbl_precio)
        
        info_layout.addWidget(QLabel("Producto Seleccionado:"))
        info_layout.addWidget(self.lbl_nombre)
        info_layout.addLayout(details_layout)
        
        layout.addWidget(info_frame)
        
        # --- Selector de Cantidad ---
        f_cant = QHBoxLayout()
        lbl_cant = QLabel("Cantidad a Vender:")
        lbl_cant.setStyleSheet("font-weight: bold;")
        
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setRange(1, 9999)
        self.spin_cantidad.setFixedWidth(100)
        self.spin_cantidad.setMinimumHeight(35)
        self.spin_cantidad.setAlignment(Qt.AlignCenter)
        self.spin_cantidad.valueChanged.connect(self._update_ui_totals)
        
        f_cant.addWidget(lbl_cant)
        f_cant.addWidget(self.spin_cantidad)
        f_cant.addStretch() 
        
        layout.addLayout(f_cant)
        layout.addStretch() 
        return box

    def _create_summary_box(self) -> QGroupBox:
        """Crea la tarjeta de resumen financiero."""
        box = QGroupBox("2. Finalizar Transacción")
        layout = QVBoxLayout(box)
        layout.setContentsMargins(20, 25, 20, 20)
        layout.setSpacing(10)
        
        lbl_info = QLabel("Resumen de Pago")
        lbl_info.setAlignment(Qt.AlignCenter)
        lbl_info.setStyleSheet("color: #adb5bd; font-size: 10pt; text-transform: uppercase; letter-spacing: 1px;")
        layout.addWidget(lbl_info)
        
        layout.addStretch()
        
        lbl_total_titulo = QLabel("TOTAL A PAGAR")
        lbl_total_titulo.setAlignment(Qt.AlignCenter)
        lbl_total_titulo.setStyleSheet("font-weight: bold; color: #495057;")
        layout.addWidget(lbl_total_titulo)
        
        self.lbl_total_pagar = QLabel("0.00 Bs")
        self.lbl_total_pagar.setAlignment(Qt.AlignCenter)
        self.lbl_total_pagar.setStyleSheet("""
            font-size: 36pt; 
            font-weight: bold; 
            color: #28a745; 
            margin: 10px 0;
        """)
        layout.addWidget(self.lbl_total_pagar)
        
        layout.addStretch()
        
        btn_vender = QPushButton(" CONFIRMAR VENTA")
        btn_vender.setObjectName("BtnVender")
        btn_vender.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
        btn_vender.setIconSize(QSize(24, 24))
        # CORRECCIÓN: Cursor de mano via Python
        btn_vender.setCursor(QCursor(Qt.PointingHandCursor))
        btn_vender.setMinimumHeight(60) 
        btn_vender.clicked.connect(self.procesar_venta)
        
        layout.addWidget(btn_vender)
        return box

    def _create_history_box(self) -> QGroupBox:
        """Crea la tabla de historial."""
        box = QGroupBox("3. Historial de Ventas Recientes")
        layout = QVBoxLayout(box)
        layout.setContentsMargins(10, 25, 10, 10)
        
        self.tabla = QTableWidget(0, 6)
        headers = ["ID Trans.", "Código", "Producto", "Cant.", "P. Unitario", "Total"]
        self.tabla.setHorizontalHeaderLabels(headers)
        
        # Configuración Pro
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setStretchLastSection(True) 
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setShowGrid(False)
        self.tabla.verticalHeader().setVisible(False)
        
        layout.addWidget(self.tabla)
        return box

    # --- Lógica del Negocio ---

    def buscar_producto(self):
        code = self.input_codigo.text().strip()
        if not code: return
        
        self.setCursor(Qt.WaitCursor)
        prod = ProductoController.obtener_por_codigo(code)
        self.setCursor(Qt.ArrowCursor)

        if not prod:
            QMessageBox.warning(self, "Producto No Encontrado", f"El código <b>{code}</b> no existe en el inventario.")
            self.producto_seleccionado = None
            self._reset_product_ui()
            self.input_codigo.selectAll()
            return

        self.producto_seleccionado = prod
        stock = prod['stock']
        
        self.spin_cantidad.setMaximum(stock if stock > 0 else 0)
        self.spin_cantidad.setValue(1)
        self.spin_cantidad.setEnabled(stock > 0)
        
        self.lbl_nombre.setText(prod['nombre'])
        
        color_stock = "green" if stock > 5 else "orange" if stock > 0 else "red"
        self.lbl_stock.setText(f"Stock Disponible: <b style='color:{color_stock}; font-size:12pt;'>{stock}</b>")
        
        self.lbl_precio.setText(f"Precio Unit.: {prod['precio']:.2f} Bs")
        
        self._update_ui_totals()
        
        if stock > 0:
            self.spin_cantidad.setFocus()
            self.spin_cantidad.selectAll()

    def _update_ui_totals(self):
        if not self.producto_seleccionado: 
            self.lbl_total_pagar.setText("0.00 Bs")
            return
            
        cant = self.spin_cantidad.value()
        precio = float(self.producto_seleccionado['precio'])
        total = cant * precio
        
        self.lbl_total_pagar.setText(f"{total:,.2f} Bs")

    def _reset_product_ui(self):
        self.lbl_nombre.setText("---")
        self.lbl_stock.setText("Stock: 0")
        self.lbl_precio.setText("Precio: 0.00 Bs")
        self.lbl_total_pagar.setText("0.00 Bs")
        self.spin_cantidad.setValue(1)
        self.spin_cantidad.setEnabled(False)

    def procesar_venta(self):
        if not self.producto_seleccionado:
            return QMessageBox.warning(self, "Atención", "Por favor, busque y seleccione un producto antes de cobrar.")
        
        # --- SOLUCIÓN DEL ERROR DE ID ---
        usuario_final = None
        try:
            usuario_final = int(self.usuario_id_raw)
        except (ValueError, TypeError):
            print(f"⚠️ AVISO SISTEMA: El usuario '{self.usuario_id_raw}' es texto. Usando ID 1 por defecto.")
            usuario_final = 1 # ID por defecto (Admin)
        
        confirm = QMessageBox.question(
            self, "Confirmar Venta",
            f"¿Registrar venta de {self.spin_cantidad.value()} unidad(es) de\n"
            f"{self.producto_seleccionado['nombre']}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
        )
        
        if confirm != QMessageBox.Yes:
            return

        resultado = VentaController.registrar_venta(
            codigo_producto=self.producto_seleccionado['codigo'],
            cantidad=self.spin_cantidad.value(),
            precio_unitario=float(self.producto_seleccionado['precio']),
            vendido_por=usuario_final
        )

        if resultado["status"]:
            msg = QMessageBox(self)
            msg.setWindowTitle("Venta Exitosa")
            msg.setText(f"✅ Venta registrada correctamente.\n\nTotal Cobrado: {resultado['total']:.2f} Bs")
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
            
            self.cargar_historial()
            
            self.input_codigo.clear()
            self.input_codigo.setFocus()
            self.producto_seleccionado = None
            self._reset_product_ui()
        else:
            QMessageBox.critical(self, "Error de Transacción", f"❌ No se pudo registrar:\n{resultado['message']}")

    def cargar_historial(self):
        ventas = VentaController.obtener_historial()
        self.tabla.setRowCount(len(ventas))
        
        for i, v in enumerate(ventas):
            item_id = QTableWidgetItem(str(v['id']))
            item_id.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(i, 0, item_id)
            
            self.tabla.setItem(i, 1, QTableWidgetItem(str(v.get('codigo_producto',''))))
            
            self.tabla.setItem(i, 2, QTableWidgetItem(v.get('nombre_producto','Producto Eliminado')))
            
            item_cant = QTableWidgetItem(str(v['cantidad']))
            item_cant.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(i, 3, item_cant)
            
            item_pu = QTableWidgetItem(f"{v['precio_unitario']:.2f}")
            item_pu.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla.setItem(i, 4, item_pu)
            
            item_total = QTableWidgetItem(f"{v['total']:.2f}")
            item_total.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_total.setFont(QFont("Segoe UI", 9, QFont.Bold))
            self.tabla.setItem(i, 5, item_total)