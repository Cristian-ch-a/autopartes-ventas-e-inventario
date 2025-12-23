# gui/venta.py
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QMessageBox, QSpinBox,
    QGroupBox, QFormLayout, QHeaderView, QSpacerItem, QSizePolicy, QFrame
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QLocale
from controllers.producto_controller import ProductoController
from controllers.venta_controller import VentaController

class RegistrarVentaWindow(QWidget):
    def __init__(self, usuario_id):
        super().__init__()
        # Guardamos el ID tal cual llega (puede ser str o int)
        self.usuario_id_raw = usuario_id 
        self.producto_seleccionado = None
        
        self.setWindowTitle(f"🛒 Punto de Venta - Usuario: {self.usuario_id_raw}")
        self.setGeometry(200, 100, 1000, 750) 
        self._set_styles()
        self._init_ui()
        self.cargar_historial() 

    def _set_styles(self):
        # (Tus estilos originales estaban bien, los resumo aquí para ahorrar espacio)
        self.setStyleSheet("""
            QWidget { background-color: #f8f9fa; font-family: 'Segoe UI'; }
            QGroupBox { background-color: white; border-radius: 8px; border: 1px solid #ddd; margin-top: 15px; }
            QGroupBox::title { color: #555; font-weight: bold; padding: 0 5px; }
            QLineEdit, QSpinBox { padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
            QPushButton { background-color: #007bff; color: white; padding: 10px; border-radius: 5px; font-weight: bold; }
            QPushButton:hover { background-color: #0056b3; }
            #BtnVender { background-color: #28a745; font-size: 11pt; }
            #BtnVender:hover { background-color: #1e7e34; }
            QTableWidget { border: 1px solid #ccc; }
        """)

    def _init_ui(self):
        main = QVBoxLayout(self)
        
        # Panel Superior
        top_panel = QHBoxLayout()
        top_panel.addWidget(self._create_search_box(), 3)
        top_panel.addWidget(self._create_summary_box(), 2)
        main.addLayout(top_panel)
        
        # Panel Inferior
        main.addWidget(self._create_history_box())

    def _create_search_box(self):
        box = QGroupBox("1. Selección de Producto")
        layout = QVBoxLayout(box)
        layout.setSpacing(15)
        
        # Buscador
        h = QHBoxLayout()
        self.input_codigo = QLineEdit()
        self.input_codigo.setPlaceholderText("Ingrese Código (ej: GSP-123)")
        self.input_codigo.returnPressed.connect(self.buscar_producto)
        btn = QPushButton("🔍 Buscar")
        btn.clicked.connect(self.buscar_producto)
        h.addWidget(self.input_codigo); h.addWidget(btn)
        layout.addLayout(h)
        
        # Detalles
        self.lbl_nombre = QLabel("Producto: ---")
        self.lbl_stock = QLabel("Stock: 0")
        self.lbl_precio = QLabel("Precio: 0.00 Bs")
        layout.addWidget(self.lbl_nombre)
        layout.addWidget(self.lbl_stock)
        layout.addWidget(self.lbl_precio)
        
        # Cantidad
        f = QFormLayout()
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setRange(1, 9999)
        self.spin_cantidad.valueChanged.connect(self._update_ui_totals)
        f.addRow("Cantidad:", self.spin_cantidad)
        layout.addLayout(f)
        layout.addStretch()
        return box

    def _create_summary_box(self):
        box = QGroupBox("2. Finalizar Venta")
        layout = QVBoxLayout(box)
        
        self.lbl_total_pagar = QLabel("<h1>0.00 Bs</h1>")
        self.lbl_total_pagar.setAlignment(Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(QLabel("Total a Pagar:"), 0, Qt.AlignCenter)
        layout.addWidget(self.lbl_total_pagar)
        layout.addStretch()
        
        btn_vender = QPushButton("💰 COBRAR Y REGISTRAR")
        btn_vender.setObjectName("BtnVender")
        btn_vender.setMinimumHeight(50)
        btn_vender.clicked.connect(self.procesar_venta)
        layout.addWidget(btn_vender)
        return box

    def _create_history_box(self):
        box = QGroupBox("3. Últimas Ventas")
        layout = QVBoxLayout(box)
        self.tabla = QTableWidget(0, 6)
        self.tabla.setHorizontalHeaderLabels(["ID", "Cód", "Producto", "Cant", "P.Unit", "Total"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla)
        return box

    # --- Lógica ---

    def buscar_producto(self):
        code = self.input_codigo.text().strip()
        if not code: return
        
        prod = ProductoController.obtener_por_codigo(code)
        if not prod:
            QMessageBox.warning(self, "No encontrado", "Código no existe.")
            self.producto_seleccionado = None
            return

        self.producto_seleccionado = prod
        stock = prod['stock']
        self.spin_cantidad.setMaximum(stock if stock > 0 else 0)
        self.spin_cantidad.setValue(1)
        
        # Actualizar UI
        self.lbl_nombre.setText(f"<b>Producto:</b> {prod['nombre']}")
        self.lbl_stock.setText(f"<b>Stock:</b> {stock}")
        self.lbl_precio.setText(f"<b>Precio:</b> {prod['precio']} Bs")
        self._update_ui_totals()

    def _update_ui_totals(self):
        if not self.producto_seleccionado: return
        cant = self.spin_cantidad.value()
        precio = float(self.producto_seleccionado['precio'])
        total = cant * precio
        self.lbl_total_pagar.setText(f"<h1>{total:.2f} Bs</h1>")

    def procesar_venta(self):
        if not self.producto_seleccionado:
            return QMessageBox.warning(self, "Error", "Busque un producto primero.")
        
        # --- SOLUCIÓN DEL ERROR ---
        # 1. Intentamos convertir el usuario a ID numérico
        usuario_final = None
        try:
            usuario_final = int(self.usuario_id_raw)
        except (ValueError, TypeError):
            print(f"⚠️ AVISO: El usuario '{self.usuario_id_raw}' es texto. Usando ID 1 por defecto.")
            usuario_final = 1 # ID por defecto (Admin)
        
        # 2. Llamada segura al controlador
        resultado = VentaController.registrar_venta(
            codigo_producto=self.producto_seleccionado['codigo'],
            cantidad=self.spin_cantidad.value(),
            precio_unitario=float(self.producto_seleccionado['precio']),
            vendido_por=usuario_final
        )

        if resultado["status"]:
            QMessageBox.information(self, "Éxito", f"✅ Venta OK.\nTotal: {resultado['total']} Bs")
            self.cargar_historial()
            self.input_codigo.clear()
            self.input_codigo.setFocus()
            self.producto_seleccionado = None
            self.lbl_total_pagar.setText("<h1>0.00 Bs</h1>")
        else:
            QMessageBox.critical(self, "Error", resultado["message"])

    def cargar_historial(self):
        ventas = VentaController.obtener_historial()
        self.tabla.setRowCount(len(ventas))
        for i, v in enumerate(ventas):
            self.tabla.setItem(i, 0, QTableWidgetItem(str(v['id'])))
            self.tabla.setItem(i, 1, QTableWidgetItem(str(v.get('codigo_producto',''))))
            self.tabla.setItem(i, 2, QTableWidgetItem(v.get('nombre_producto','')))
            self.tabla.setItem(i, 3, QTableWidgetItem(str(v['cantidad'])))
            self.tabla.setItem(i, 4, QTableWidgetItem(f"{v['precio_unitario']:.2f}"))
            self.tabla.setItem(i, 5, QTableWidgetItem(f"{v['total']:.2f}"))