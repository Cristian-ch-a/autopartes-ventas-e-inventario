# gui/reporte_ventas.py
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QFileDialog, QDateEdit,
    QGroupBox, QHeaderView, QFrame, QStyle, QMessageBox,
    QGraphicsDropShadowEffect, QAbstractItemView
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QIcon, QColor, QCursor

from controllers.reporte_controller import ReporteVentasController
from utils.pdf_reporte import PDFReportes

class ReporteVentasWindow(QWidget):
    """
    Dashboard de Reportes de Ventas.
    Versión Final Limpia: Sin errores de consola 'Unknown property cursor'.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("📈 Reporte Financiero y de Ventas")
        self.resize(1100, 750)
        self.datos_actuales = []
        self.kpis_actuales = {}

        self._set_styles()
        self._init_ui()
        
        # Cargar datos del mes actual por defecto al abrir
        self._cargar_mes_actual()

    def _set_styles(self):
        """
        Define estilos QSS profesionales.
        CORRECCIÓN: Se eliminó 'cursor: pointer' para limpiar la consola.
        """
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f7f6;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #333;
            }
            /* TARJETAS KPI */
            QFrame.kpi_card {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
            /* FILTROS */
            QGroupBox {
                background-color: white;
                border: 1px solid #dcdcdc;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
            }
            QDateEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 5px;
                min-width: 120px;
            }
            
            /* BOTONES */
            QPushButton {
                background-color: #007bff;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 10pt;
                border: none;
            }
            QPushButton:hover { 
                background-color: #0056b3; 
                /* Se eliminó cursor: pointer de aquí para evitar el error */
            }
            QPushButton#btn_pdf { background-color: #dc3545; }
            QPushButton#btn_pdf:hover { background-color: #bd2130; }

            /* TABLA */
            QTableWidget {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
                gridline-color: #f0f0f0;
            }
            QHeaderView::section {
                background-color: #343a40;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
        """)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 1. Título
        lbl_titulo = QLabel("Reporte General de Ventas")
        lbl_titulo.setStyleSheet("font-size: 20pt; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(lbl_titulo)

        # 2. Área de KPIs (Tarjetas Superiores)
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(20)

        self.card_ingresos = self._create_kpi_card("Ingresos Totales", "0.00 Bs", "💰")
        self.card_transacciones = self._create_kpi_card("Transacciones", "0", "🧾")
        self.card_productos = self._create_kpi_card("Prod. Vendidos", "0", "📦")

        kpi_layout.addWidget(self.card_ingresos)
        kpi_layout.addWidget(self.card_transacciones)
        kpi_layout.addWidget(self.card_productos)
        main_layout.addLayout(kpi_layout)

        # 3. Filtros y Acciones
        filter_group = QGroupBox("Filtros de Búsqueda")
        filter_layout = QHBoxLayout(filter_group)
        
        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_fin = QDateEdit()
        self.fecha_fin.setCalendarPopup(True)
        self.fecha_fin.setDate(QDate.currentDate()) # Hasta hoy

        btn_buscar = QPushButton(" Generar Reporte")
        btn_buscar.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        btn_buscar.setCursor(QCursor(Qt.PointingHandCursor)) # Cursor puesto por código Python
        btn_buscar.clicked.connect(self.buscar)

        btn_pdf = QPushButton(" Exportar a PDF")
        btn_pdf.setObjectName("btn_pdf")
        btn_pdf.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        btn_pdf.setCursor(QCursor(Qt.PointingHandCursor)) # Cursor puesto por código Python
        btn_pdf.clicked.connect(self.exportar_pdf)

        filter_layout.addWidget(QLabel("📅 Desde:"))
        filter_layout.addWidget(self.fecha_inicio)
        filter_layout.addWidget(QLabel("📅 Hasta:"))
        filter_layout.addWidget(self.fecha_fin)
        filter_layout.addSpacing(10)
        filter_layout.addWidget(btn_buscar)
        filter_layout.addStretch()
        filter_layout.addWidget(btn_pdf)

        main_layout.addWidget(filter_group)

        # 4. Tabla de Resultados
        self.tabla = QTableWidget(0, 7)
        headers = ["ID", "Fecha/Hora", "Código", "Producto", "Cant.", "P. Unit", "Total"]
        self.tabla.setHorizontalHeaderLabels(headers)
        
        # Configuración Tabla Pro
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents) # ID chico
        self.tabla.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents) # Cant chico
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.verticalHeader().setVisible(False)
        
        main_layout.addWidget(self.tabla)

    def _create_kpi_card(self, title, value, icon):
        """Crea una tarjeta visual para mostrar métricas."""
        frame = QFrame()
        frame.setProperty("class", "kpi_card") # Para CSS
        frame.setStyleSheet(".kpi_card { background-color: white; border-radius: 10px; border: 1px solid #ccc; }")
        
        # Sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        frame.setGraphicsEffect(shadow)

        layout = QVBoxLayout(frame)
        
        # Icono y Título
        top_row = QHBoxLayout()
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 24pt;")
        lbl_title = QLabel(title.upper())
        lbl_title.setStyleSheet("color: #7f8c8d; font-weight: bold; font-size: 10pt;")
        
        top_row.addWidget(lbl_icon)
        top_row.addSpacing(10)
        top_row.addWidget(lbl_title)
        top_row.addStretch()
        
        # Valor
        lbl_value = QLabel(value)
        lbl_value.setAlignment(Qt.AlignRight)
        lbl_value.setStyleSheet("font-size: 24pt; font-weight: bold; color: #2c3e50;")
        
        # Guardamos referencia para actualizar después
        frame.lbl_value_ref = lbl_value 
        
        layout.addLayout(top_row)
        layout.addWidget(lbl_value)
        
        return frame

    def _cargar_mes_actual(self):
        """Configura las fechas al mes actual y busca."""
        hoy = QDate.currentDate()
        inicio_mes = QDate(hoy.year(), hoy.month(), 1)
        self.fecha_inicio.setDate(inicio_mes)
        self.buscar()

    def buscar(self):
        """Ejecuta la búsqueda y actualiza tabla y tarjetas."""
        f_inicio = self.fecha_inicio.date().toString("yyyy-MM-dd")
        f_fin = self.fecha_fin.date().toString("yyyy-MM-dd")

        self.setCursor(Qt.WaitCursor)
        
        # 1. Obtener Datos Tabla
        self.datos_actuales = ReporteVentasController.ventas_por_fecha(f_inicio, f_fin)
        
        # 2. Obtener KPIs (Resumen)
        self.kpis_actuales = ReporteVentasController.obtener_kpis(f_inicio, f_fin)

        self._llenar_tabla()
        self._actualizar_kpis()
        
        self.setCursor(Qt.ArrowCursor)

        if not self.datos_actuales:
            QMessageBox.information(self, "Sin Resultados", "No se encontraron ventas en el rango seleccionado.")

    def _llenar_tabla(self):
        self.tabla.setRowCount(0)
        for d in self.datos_actuales:
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)

            # Alineación y formato
            self._set_cell(row, 0, str(d["id"]), Qt.AlignCenter)
            self._set_cell(row, 1, d["fecha_venta"])
            self._set_cell(row, 2, d["codigo_producto"])
            self._set_cell(row, 3, d["nombre_producto"])
            self._set_cell(row, 4, str(d["cantidad"]), Qt.AlignCenter)
            self._set_cell(row, 5, f"{d['precio_unitario']:.2f}", Qt.AlignRight)
            self._set_cell(row, 6, f"{d['total']:.2f}", Qt.AlignRight, bold=True)

    def _set_cell(self, row, col, text, align=Qt.AlignLeft, bold=False):
        item = QTableWidgetItem(text)
        item.setTextAlignment(align | Qt.AlignVCenter)
        if bold:
            font = QFont()
            font.setBold(True)
            item.setFont(font)
        self.tabla.setItem(row, col, item)

    def _actualizar_kpis(self):
        """Actualiza los números de las tarjetas."""
        ingresos = self.kpis_actuales.get('ingresos', 0.0)
        trans = self.kpis_actuales.get('transacciones', 0)
        prods = self.kpis_actuales.get('productos', 0)

        # Animación simple (actualización texto)
        self.card_ingresos.lbl_value_ref.setText(f"{ingresos:,.2f} Bs")
        self.card_transacciones.lbl_value_ref.setText(str(trans))
        self.card_productos.lbl_value_ref.setText(str(prods))

    def exportar_pdf(self):
        if not self.datos_actuales:
            return QMessageBox.warning(self, "Error", "No hay datos para exportar. Realice una búsqueda primero.")

        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar Reporte PDF", f"Reporte_Ventas_{QDate.currentDate().toString('yyyyMMdd')}", "PDF (*.pdf)")
        
        if not ruta:
            return

        # Columnas a exportar (Clave Diccionario, Título PDF)
        cols_export = [
            ("id", "ID"),
            ("fecha_venta", "Fecha"),
            ("codigo_producto", "Código"),
            ("nombre_producto", "Producto"),
            ("cantidad", "Cant."),
            ("precio_unitario", "P.Unit"),
            ("total", "Total")
        ]

        exito = PDFReportes.generar_pdf_reporte(
            "Reporte Detallado de Ventas",
            self.datos_actuales,
            cols_export,
            ruta,
            resumen=self.kpis_actuales # Pasamos los KPIs para que salgan en el PDF
        )

        if exito:
            QMessageBox.information(self, "Éxito", f"Reporte guardado correctamente en:\n{ruta}")
            try:
                os.startfile(ruta)
            except:
                pass
        else:
            QMessageBox.critical(self, "Error", "No se pudo generar el PDF. Verifique si el archivo está abierto.")