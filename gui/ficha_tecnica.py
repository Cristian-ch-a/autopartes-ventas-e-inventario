import os
import sys
from typing import Dict, Any, Optional, Tuple
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QFormLayout, QMessageBox, QScrollArea,
    QSizePolicy, QFrame, QSpacerItem, QGridLayout
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QSize

# --- CONFIGURACIÓN DE RUTA ---
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_PATH, "assets", "imagenes_productos")
os.makedirs(ASSETS_DIR, exist_ok=True)

# -------------------------------------------------------------
#                   UTILIDADES GENERALES
# -------------------------------------------------------------

def _coalesce_medida(medidas: Dict[str, Any], *keys: str) -> str:
    """Busca un valor en `medidas` probando varias claves (insensible a mayúsculas)."""
    if not isinstance(medidas, dict):
        return "N/A"
    
    low_map = {
        str(k).lower().replace("á", "a").replace("í", "i").replace("ó", "o").replace("é", "e").replace("ú", "u"): v
        for k, v in medidas.items()
    }
    
    for k in keys:
        key_norm = str(k).lower().replace("á", "a").replace("í", "i").replace("ó", "o").replace("é", "e").replace("ú", "u")
        if key_norm in low_map and str(low_map[key_norm]).strip() not in ("", None, "N/A"):
            return str(low_map[key_norm])
            
    return "N/A"

def _resolve_image_path(producto: Dict[str, Any]) -> str:
    """Obtiene ruta absoluta de la imagen."""
    ruta = producto.get("imagen_path") or producto.get("imagen") or ""
    if not ruta:
        return ""
    if os.path.isabs(ruta) and os.path.exists(ruta):
        return ruta
    candidate = os.path.join(ASSETS_DIR, os.path.basename(ruta))
    if os.path.exists(candidate):
        return candidate
    return ""

def _create_label_value_pair(label: str, value: str) -> Tuple[QLabel, QLabel]:
    """Crea un par de QLabel con estilo uniforme para la ficha técnica."""
    
    # 1. Etiqueta (Key)
    lbl_key = QLabel(f"<b>{label}:</b>")
    lbl_key.setStyleSheet("color: #6c757d; font-size: 10pt;")
    
    # 2. Valor (Value)
    lbl_value = QLabel(value)
    lbl_value.setWordWrap(True)
    lbl_value.setStyleSheet("color: #34495e;")
    
    return lbl_key, lbl_value

# ============================================================== #
# 🖥️ CLASE PRINCIPAL: FichaTecnicaWindow
# ============================================================== #

class FichaTecnicaWindow(QWidget):
    """Ventana Ficha Técnica con diseño estético y modular."""

    def __init__(self, producto: Dict[str, Any]):
        super().__init__()
        self.producto = producto.copy()
        self.producto["medidas"] = self.producto.get("medidas") or {}
        
        self.setWindowTitle(f"Ficha Técnica - {self.producto.get('codigo', 'N/A')}")
        self.setGeometry(420, 80, 1000, 900) # Tamaño Aumentado para mayor presencia
        self.setWindowFlags(self.windowFlags() | Qt.Window) # Asegura que sea una ventana independiente
        self._set_styles()
        self._init_ui()

    # ---------------------------
    # Estilos CSS avanzados (QSS)
    # ---------------------------
    def _set_styles(self):
        """Aplica estilos QSS unificados para una apariencia Material/Plana y profesional."""
        self.setStyleSheet("""
            QWidget { 
                background-color: #f8f9fa; /* Fondo muy claro */
                font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
            }
            QGroupBox {
                border: 1px solid #e9ecef; /* Borde muy sutil */
                border-radius: 8px;
                margin-top: 15px;
                background-color: white; /* Contenido en blanco */
            }
            QGroupBox::title { 
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                color: #495057;
                font-size: 11pt;
                font-weight: bold;
            }
        """)
    
    # ---------------------------
    # Interfaz principal (Modular)
    # ---------------------------
    def _init_ui(self):
        """Organiza los módulos principales de la ficha técnica."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        scroll_layout = QVBoxLayout(container)
        scroll_layout.setSpacing(20) # Espaciado aumentado
        scroll_layout.setContentsMargins(30, 30, 30, 30) # Márgenes aumentados
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        scroll_layout.addWidget(self._create_top_banner())
        
        content_row = QHBoxLayout()
        content_row.setSpacing(20)
        
        # Columna Izquierda: Imagen (ocupa 2 partes)
        content_row.addWidget(self._create_image_card(), 2) 
        
        # Columna Derecha: Datos Generales, Descripción y Extras (ocupa 3 partes)
        right_column = QVBoxLayout()
        right_column.setSpacing(20)
        right_column.addWidget(self._create_general_info_card())
        right_column.addWidget(self._create_description_card())
        content_row.addLayout(right_column, 3)
        
        scroll_layout.addLayout(content_row)

        # Medidas Técnicas (Ancho completo)
        scroll_layout.addWidget(self._create_medidas_card())
        
        scroll_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        scroll_layout.addWidget(self._create_pdf_export_button(), alignment=Qt.AlignCenter)
        

    # ---------------------------
    # Módulo 1: Banner Superior
    # ---------------------------
    def _create_top_banner(self) -> QWidget:
        """Crea el banner superior con código, nombre grande y botón PDF rápido."""
        banner = QWidget()
        banner.setStyleSheet("background-color: #d1ecf1; border-radius: 12px; padding: 20px;")
        h = QHBoxLayout(banner)

        v = QVBoxLayout()
        
        codigo_lbl = QLabel(self.producto.get("codigo", "SIN-CÓDIGO"))
        codigo_lbl.setFont(QFont("Segoe UI", 28, QFont.Bold))
        codigo_lbl.setStyleSheet("color: #0c5460;")
        v.addWidget(codigo_lbl)

        nombre_lbl = QLabel(self.producto.get("nombre", "Producto sin nombre"))
        nombre_lbl.setFont(QFont("Segoe UI", 14))
        nombre_lbl.setStyleSheet("color: #4a698a;")
        v.addWidget(nombre_lbl)
        h.addLayout(v, 4)

        quick_pdf = QPushButton("📄 Exportar Rápido")
        quick_pdf.setFixedHeight(60)
        quick_pdf.setFixedWidth(280)
        quick_pdf.clicked.connect(self.exportar_pdf)
        quick_pdf.setStyleSheet("""
            QPushButton { 
                background-color: #007bff; color: white; border-radius: 6px; 
                font-size: 11pt; font-weight: 500;
            }
            QPushButton:hover { background-color: #0056b3; }
        """)
        
        h.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        h.addWidget(quick_pdf, 1)
        
        return banner

    # ---------------------------
    # Módulo 2: Card Imagen
    # ---------------------------
    def _create_image_card(self) -> QGroupBox:
        """Crea la tarjeta para mostrar la imagen principal del producto."""
        box = QGroupBox("Fotografía")
        v = QVBoxLayout(box)
        v.setContentsMargins(20, 30, 20, 20)

        img_lbl = QLabel()
        img_lbl.setAlignment(Qt.AlignCenter)
        img_lbl.setMinimumHeight(350)
        # Estilo mejorado para el área de imagen
        img_lbl.setStyleSheet("background-color: #f7f9fc; border-radius: 6px; border: 2px dashed #e9ecef;")
        img_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        ruta = _resolve_image_path(self.producto)
        if ruta and os.path.exists(ruta):
            pix = QPixmap(ruta)
            # Escalar proporcionalmente a un tamaño mayor
            scaled_pix = pix.scaled(1000, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation) 
            img_lbl.setPixmap(scaled_pix)
        else:
            img_lbl.setText("🚫 Imagen no disponible")
            img_lbl.setFont(QFont("Segoe UI", 16))
            img_lbl.setStyleSheet("color: #adb5bd;")

        v.addWidget(img_lbl)
        return box

    # ---------------------------
    # Módulo 3: Card Datos Generales
    # ---------------------------
    def _create_general_info_card(self) -> QGroupBox:
        """Crea la tarjeta con los datos básicos en formato QFormLayout, con mejor presentación."""
        box = QGroupBox("Detalles Clave del Inventario")
        f = QFormLayout(box)
        f.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        f.setFormAlignment(Qt.AlignLeft)
        f.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        f.setHorizontalSpacing(30)
        f.setVerticalSpacing(10)
        f.setContentsMargins(20, 20, 20, 20)
        
        get = lambda k: self.producto.get(k, "N/A")

        campos = [
            ("Categoría:", get("categoria")),
            ("Tipo Repuesto:", get("tipo_repuesto") if get("tipo_repuesto") and get("tipo_repuesto") != get("categoria") else "General"),
            ("Cód. Original:", get("cod_original")),
        ]
        
        # Campos de valores importantes (Stock y Precio)
        info_critica = [
            ("Stock Actual:", f"<span style='color: #007bff; font-weight: bold;'>{get('stock') if isinstance(get('stock'), int) and get('stock') > 0 else 0}</span> unidades"),
            ("Precio Unitario:", f"<span style='color: #27ae60; font-weight: bold;'>{float(get('precio') or 0):.2f} Bs</span>")
        ]

        for etiqueta, valor in campos:
            lbl_key, lbl_value = _create_label_value_pair(etiqueta, str(valor))
            f.addRow(lbl_key, lbl_value)

        # Separador estético para datos críticos
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("margin: 5px 0; background-color: #f0f0f0;")
        f.addRow(line)
        
        for etiqueta, valor_html in info_critica:
            lbl_key = QLabel(f"<b style='color: #34495e;'>{etiqueta}</b>")
            lbl_value = QLabel(valor_html)
            lbl_value.setWordWrap(True)
            f.addRow(lbl_key, lbl_value)

        return box

    # ---------------------------
    # Módulo 4: Card Descripción
    # ---------------------------
    def _create_description_card(self) -> QGroupBox:
        """Crea la tarjeta para la descripción y otros datos menos comunes."""
        box = QGroupBox("Aplicación y Observaciones")
        v = QVBoxLayout(box)
        v.setContentsMargins(20, 20, 20, 20)
        v.setSpacing(15)

        descripcion = self.producto.get("descripcion") or self.producto.get("aplicacion") or "Sin descripción detallada o aplicación registrada."
        
        d_lbl = QLabel(descripcion)
        d_lbl.setWordWrap(True)
        d_lbl.setStyleSheet("font-style: italic; color: #555; line-height: 1.5;")
        v.addWidget(d_lbl)
        
        # --- Datos Extras ---
        extras = {k: v for k, v in self.producto.items() if k not in self.producto.keys() or k not in ["codigo", "nombre", "imagen_path", "imagen", "medidas", "descripcion", "aplicacion", "categoria", "tipo_repuesto", "cod_original", "stock", "precio", "medidas_dict"]}

        if extras:
            frame_extras = QFrame()
            frame_extras.setStyleSheet("border: 1px solid #e9ecef; border-radius: 6px; padding: 15px; margin-top: 15px; background-color: #f7f9fc;")
            v_extras = QFormLayout(frame_extras)
            v_extras.setContentsMargins(0, 0, 0, 0)
            
            e_title = QLabel("Datos Técnicos Adicionales:")
            e_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
            e_title.setStyleSheet("color: #7f8c8d; margin-bottom: 5px;")
            v_extras.addRow(e_title)
            
            for k, val in sorted(extras.items()):
                r = QLabel(str(val))
                r.setWordWrap(True)
                v_extras.addRow(f"<b>{k.replace('_', ' ').title()}:</b>", r)
            v.addWidget(frame_extras)

        return box

    # ---------------------------
    # Módulo 5: Card Medidas (Mejorado para Armonía Visual)
    # ---------------------------
    def _create_medidas_card(self) -> QGroupBox:
        """Crea la tarjeta de medidas con un formato de cuadrícula limpio y profesional."""
        
        box = QGroupBox("Especificaciones Técnicas (Medidas)")
        # Estilos específicos para este GroupBox
        box.setStyleSheet("""
            QGroupBox { border: 2px solid #ffcc80; } /* Borde Naranja Suave y más grueso */
            QGroupBox::title { color: #d35400; font-size: 12pt; } 
        """)
        
        g = QGridLayout(box)
        g.setSpacing(15) # Espaciado entre elementos
        g.setContentsMargins(25, 30, 25, 25)

        medidas = self.producto.get("medidas") or {}
        
        # Mapeo de búsqueda por cada etiqueta
        valores_mapeados = {
            "A": _coalesce_medida(medidas, "A", "a", "numero dientes", "número dientes", "diámetro", "diametro"),
            "B": _coalesce_medida(medidas, "B", "b", "dientes copa", "dientes", "n_dientes"),
            "C": _coalesce_medida(medidas, "C", "c", "diámetro", "diametro", "sello"),
            "ABS": _coalesce_medida(medidas, "ABS", "abs", "n_abs", "número abs", "numero abs"),
            "H": _coalesce_medida(medidas, "H", "h", "bastago", "bástago", "largo bastago"),
            "L": _coalesce_medida(medidas, "L", "l", "largo", "largo comprimido", "largo_comprimido"),
        }
        
        row, col = 0, 0
        columnas_por_fila = 3 # Tres pares de Etiqueta + Valor por fila

        medidas_encontradas = [(e, v) for e, v in valores_mapeados.items() if v != "N/A"]

        for etiqueta, valor in medidas_encontradas:
            
            # Etiqueta (Ej: 'A:')
            lbl_key = QLabel(f"<b>{etiqueta}:</b>")
            lbl_key.setStyleSheet("color: #7f8c8d; font-size: 10pt;")
            # Alineación a la derecha para empujar la etiqueta hacia el valor
            g.addWidget(lbl_key, row, col * 2, alignment=Qt.AlignRight | Qt.AlignVCenter) 
            
            # Valor (El cuadro de datos)
            lbl_value = QLabel(str(valor))
            lbl_value.setMinimumWidth(90) 
            lbl_value.setFont(QFont("Segoe UI", 11, QFont.Bold))
            lbl_value.setStyleSheet("""
                background-color: #f7f9fa; /* Fondo muy claro */
                color: #34495e; 
                border: 1px solid #ced4da; /* Borde suave */
                border-radius: 4px;
                padding: 6px 10px;
                min-height: 25px;
            """)
            lbl_value.setAlignment(Qt.AlignCenter)
            
            g.addWidget(lbl_value, row, col * 2 + 1, alignment=Qt.AlignLeft | Qt.AlignVCenter)

            # Control de Flujo de la Cuadrícula
            col += 1
            if col >= columnas_por_fila:
                col = 0
                row += 1
                
        # Manejo si no hay medidas
        if not medidas_encontradas:
            g.addWidget(QLabel("No hay medidas específicas registradas."), 0, 0, 1, columnas_por_fila * 2, alignment=Qt.AlignCenter)
        
        # Ajuste de estiramiento: las columnas pares (etiquetas) se estiran un poco, las impares (valores) tienen ancho fijo.
        for i in range(columnas_por_fila):
            g.setColumnStretch(i * 2, 1)    # Etiquetas
            g.setColumnMinimumWidth(i * 2 + 1, 100) # Valores (para uniformidad)

        return box

    # ---------------------------
    # Módulo 6: Botón de Exportación
    # ---------------------------
    def _create_pdf_export_button(self) -> QPushButton:
        """Crea el botón de exportación a PDF para el pie de página."""
        btn = QPushButton("💾 Generar Ficha Técnica PDF")
        btn.setMinimumSize(350, 50)
        btn.setMaximumSize(500, 50)
        btn.setStyleSheet("""
            QPushButton { 
                background-color: #28a745; /* Verde Bootstrap */
                color: white; 
                border-radius: 8px;
                font-size: 13pt;
                font-weight: 500;
                margin-top: 20px;
            }
            QPushButton:hover { background-color: #1e7e34; }
        """)
        btn.clicked.connect(self.exportar_pdf)
        return btn

    # ---------------------------
    # Funcionalidad de Exportación
    # ---------------------------
    def exportar_pdf(self):
        """Llama a la utilidad externa para generar el PDF."""
        try:
            # Aquí debe ir la llamada a tu generador real de PDF
            # from utils.pdf_generator import generar_ficha_pdf
            # generar_ficha_pdf(self.producto)
            
            QMessageBox.information(
                self, 
                "PDF en proceso", 
                "El módulo de generación de PDF se está ejecutando...\n(Simulación: Ficha guardada)"
            )
        except Exception as e:
             QMessageBox.critical(self, "Error al exportar PDF", f"❌ Ocurrió un error al generar el PDF: {e}")

# FIN DEL ARCHIVO