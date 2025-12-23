# gui/dashboard.py
# ----------------------------------------------------------
# Dashboard Principal - Autopartes RAFO
# Diseño Profesional: Estilo moderno, optimizado y robusto.
# ----------------------------------------------------------

import os
import traceback
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QMessageBox, QFrame, QSizePolicy, QGraphicsDropShadowEffect, QSpacerItem
)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor

class DashboardWindow(QMainWindow):
    """
    Ventana principal del sistema. 
    Actúa como contenedor dinámico para los módulos (Inventario, Ventas, Reportes).
    """

    def __init__(self):
        super().__init__()

        # --- DATOS DE SESIÓN ---
        # Estos valores se sobrescriben si el Login los inyecta correctamente.
        # Por defecto usamos ID 1 (Admin) para evitar fallos si se prueba directo.
        self.usuario_id = 1  
        self.usuario_actual_nombre = "Administrador"
        self.usuario_rol = "Gerencia"

        # --- CONFIGURACIÓN DE VENTANA ---
        self.setWindowTitle("Sistema de Gestión - Autopartes RAFO")
        self.resize(1280, 850) # Resolución HD cómoda
        self.setMinimumSize(1024, 768)
        
        # --- ESTADO INTERNO ---
        self.current_module_widget = None # Widget que se está viendo actualmente
        self.active_button = None # Botón del menú que está seleccionado
        self._module_refs = {} # Cache para no recargar módulos ya abiertos

        # --- INICIALIZACIÓN ---
        self._apply_window_icon()
        self._setup_ui()
        self._apply_styles()
        
        # Mostrar pantalla de bienvenida
        self._show_welcome_screen() 
        
        # Mensaje en barra de estado
        self.statusBar().showMessage(f"Sesión iniciada correctamente. Usuario: {self.usuario_actual_nombre}", 8000)

    # ======================================================
    # 1. GESTIÓN DE RECURSOS (Rutas e Iconos)
    # ======================================================
    def _get_base_dir(self):
        """Retorna la ruta raíz del proyecto."""
        return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def _resource(self, rel_path):
        """Construye ruta absoluta a assets."""
        return os.path.join(self._get_base_dir(), rel_path)

    def _icon(self, filename):
        """Carga icono desde assets/iconos de forma segura."""
        ruta = self._resource(os.path.join("assets", "iconos", filename))
        return QIcon(ruta) if os.path.exists(ruta) else QIcon()

    def _apply_window_icon(self):
        logo = self._resource("assets/logo.ico")
        if os.path.exists(logo):
            self.setWindowIcon(QIcon(logo))

    # ======================================================
    # 2. CONSTRUCCIÓN DE LA INTERFAZ (Layouts)
    # ======================================================
    def _setup_ui(self):
        """Arma el esqueleto de la ventana: Sidebar Izquierda + Contenido Derecho."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout Principal Horizontal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # A. BARRA LATERAL (SIDEBAR)
        self.sidebar = self._create_sidebar()
        main_layout.addWidget(self.sidebar)

        # B. ÁREA DE CONTENIDO
        self.content_area = QWidget()
        self.content_area.setObjectName("ContentArea")
        
        # Layout del contenido
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(25, 25, 25, 25) # Márgenes internos
        
        # Agregamos el área de contenido al layout principal (expandible)
        main_layout.addWidget(self.content_area, 1) 

    def _create_sidebar(self):
        """Crea el panel lateral con logo, menú y pie de página."""
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(270) # Ancho fijo

        # Layout Vertical del Sidebar
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. HEADER (Logo)
        header = self._create_sidebar_header()
        layout.addWidget(header)

        # 2. MENÚ (Botones)
        menu_container = QWidget()
        menu_layout = QVBoxLayout(menu_container)
        menu_layout.setContentsMargins(15, 20, 15, 20)
        menu_layout.setSpacing(8)

        # Etiqueta de sección
        lbl_nav = QLabel("NAVEGACIÓN PRINCIPAL")
        lbl_nav.setObjectName("MenuLabel")
        menu_layout.addWidget(lbl_nav)
        menu_layout.addSpacing(5)

        # Creación de Botones
        self.btn_inventory = self._create_nav_btn(" Inventario", "inventario.png", self.open_inventory)
        self.btn_sale = self._create_nav_btn(" Registrar Venta", "venta.png", self.open_sale_register)
        self.btn_report = self._create_nav_btn(" Reporte Ventas", "reporte_ventas.png", self.open_sales_report)
        
        menu_layout.addWidget(self.btn_inventory)
        menu_layout.addWidget(self.btn_sale)
        menu_layout.addWidget(self.btn_report)
        
        # Empuja todo hacia arriba
        menu_layout.addStretch()
        
        layout.addWidget(menu_container, 1)

        # 3. FOOTER (Usuario)
        footer = self._create_sidebar_footer()
        layout.addWidget(footer)

        return sidebar

    def _create_sidebar_header(self):
        """Encabezado con Logo y Nombre."""
        container = QFrame()
        container.setObjectName("SidebarHeader")
        container.setFixedHeight(80)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(20, 0, 0, 0)
        
        # Logo Imagen
        lbl_img = QLabel()
        logo_path = self._resource("assets/logo.ico")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            lbl_img.setPixmap(pix)
        
        # Texto
        v_layout = QVBoxLayout()
        v_layout.setAlignment(Qt.AlignVCenter)
        v_layout.setSpacing(0)
        
        lbl_brand = QLabel("AUTOPARTES")
        lbl_brand.setStyleSheet("font-size: 10px; font-weight: bold; color: #888; letter-spacing: 1px;")
        
        lbl_name = QLabel("RAFO")
        lbl_name.setStyleSheet("font-size: 20px; font-weight: 900; color: #333;")
        
        v_layout.addWidget(lbl_brand)
        v_layout.addWidget(lbl_name)

        layout.addWidget(lbl_img)
        layout.addLayout(v_layout)
        layout.addStretch()
        
        return container

    def _create_sidebar_footer(self):
        """Pie de página con información del usuario activo."""
        container = QFrame()
        container.setObjectName("SidebarFooter")
        container.setFixedHeight(90)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(20, 15, 20, 20)
        
        # Icono de usuario (Avatar genérico)
        avatar = QLabel("👤")
        avatar.setStyleSheet("font-size: 24px; background: #e9ecef; border-radius: 18px; padding: 5px;")
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignCenter)

        # Info Texto
        v_layout = QVBoxLayout()
        v_layout.setSpacing(2)
        
        self.lbl_user_name = QLabel(self.usuario_actual_nombre)
        self.lbl_user_name.setStyleSheet("font-weight: bold; color: #333; font-size: 13px;")
        
        self.lbl_user_role = QLabel(self.usuario_rol)
        self.lbl_user_role.setStyleSheet("color: #777; font-size: 11px;")

        v_layout.addWidget(self.lbl_user_name)
        v_layout.addWidget(self.lbl_user_role)

        layout.addWidget(avatar)
        layout.addSpacing(10)
        layout.addLayout(v_layout)
        
        return container

    def _create_nav_btn(self, text, icon_name, slot):
        """Fábrica de botones de navegación."""
        btn = QPushButton(text)
        # Intentamos cargar icono, si no existe no rompe nada
        icon = self._icon(icon_name)
        if not icon.isNull():
            btn.setIcon(icon)
            btn.setIconSize(QSize(20, 20))
            
        btn.setCursor(Qt.PointingHandCursor)
        btn.setObjectName("NavButton")
        btn.setCheckable(True) # Importante para el estado "checked" visual
        
        # Conexión inteligente: Maneja el click visual y la lógica
        btn.clicked.connect(lambda: self._handle_nav_click(btn, slot))
        
        return btn

    def _handle_nav_click(self, btn, slot):
        """Maneja la lógica visual de selección y ejecuta la función."""
        # 1. Desmarcar todos los botones
        self.btn_inventory.setChecked(False)
        self.btn_sale.setChecked(False)
        self.btn_report.setChecked(False)
        
        # 2. Marcar el actual
        btn.setChecked(True)
        self.active_button = btn
        
        # 3. Ejecutar la función del módulo
        slot()

    # ======================================================
    # 3. GESTIÓN DE CONTENIDO (Módulos)
    # ======================================================
    def _set_content_widget(self, widget):
        """Reemplaza el widget central dinámicamente sin destruir el anterior."""
        # Ocultar widget actual
        if self.current_module_widget:
            self.current_module_widget.hide()
            self.content_layout.removeWidget(self.current_module_widget)
        
        # Mostrar nuevo widget
        self.content_layout.addWidget(widget)
        widget.show()
        self.current_module_widget = widget

    def _show_welcome_screen(self):
        """Pantalla inicial elegante cuando no hay módulo seleccionado."""
        placeholder = QWidget()
        layout = QVBoxLayout(placeholder)
        layout.setAlignment(Qt.AlignCenter)

        # Icono grande
        lbl_icon = QLabel("🚀")
        lbl_icon.setStyleSheet("font-size: 60px;")
        lbl_icon.setAlignment(Qt.AlignCenter)

        lbl_welcome = QLabel(f"¡Bienvenido, {self.usuario_actual_nombre}!")
        lbl_welcome.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50; margin-top: 10px;")
        lbl_welcome.setAlignment(Qt.AlignCenter)
        
        lbl_desc = QLabel("Selecciona una opción del menú izquierdo para comenzar a trabajar.")
        lbl_desc.setStyleSheet("font-size: 16px; color: #7f8c8d; margin-top: 5px;")
        lbl_desc.setAlignment(Qt.AlignCenter)

        layout.addWidget(lbl_icon)
        layout.addWidget(lbl_welcome)
        layout.addWidget(lbl_desc)
        
        self._set_content_widget(placeholder)

    # --- CARGADORES DE MÓDULOS (Lógica de Negocio) ---

    def open_inventory(self):
        try:
            from gui.inventario import InventarioWindow
            if "Inventario" not in self._module_refs:
                self._module_refs["Inventario"] = InventarioWindow()
            self._set_content_widget(self._module_refs["Inventario"])
        except Exception as e:
            self._show_error("Inventario", e)

    def open_sale_register(self):
        """
        Abre el módulo de ventas pasando el ID del usuario.
        """
        try:
            from gui.venta import RegistrarVentaWindow
            
            # --- CORRECCIÓN VITAL: Pasamos el ID numérico ---
            # Usamos una clave única por usuario para refrescar si se cambia de usuario
            key = f"Venta_User_{self.usuario_id}"
            
            if key not in self._module_refs:
                self._module_refs[key] = RegistrarVentaWindow(self.usuario_id)
            
            self._set_content_widget(self._module_refs[key])
            
        except ImportError:
             self._show_error("Venta", "No se encuentra el archivo 'gui/venta.py' o la clase 'RegistrarVentaWindow'.")
        except Exception as e:
            self._show_error("Venta", e)

    def open_sales_report(self):
        try:
            from gui.reporte_ventas import ReporteVentasWindow
            if "ReporteVentas" not in self._module_refs:
                self._module_refs["ReporteVentas"] = ReporteVentasWindow()
            self._set_content_widget(self._module_refs["ReporteVentas"])
        except Exception as e:
            self._show_error("Reportes", e)

    def _show_error(self, modulo, error):
        msg = QMessageBox(self)
        msg.setWindowTitle("Error de Módulo")
        msg.setText(f"No se pudo cargar el módulo: {modulo}")
        msg.setDetailedText(str(traceback.format_exc()))
        msg.setIcon(QMessageBox.Critical)
        msg.exec_()

    # ======================================================
    # 4. HOJA DE ESTILOS (CSS/QSS Moderno)
    # ======================================================
    def _apply_styles(self):
        self.setStyleSheet("""
            /* FONDO GENERAL */
            QMainWindow {
                background-color: #f4f7f6;
            }
            
            /* BARRA LATERAL */
            QWidget#Sidebar {
                background-color: #ffffff;
                border-right: 1px solid #e0e0e0;
            }
            
            QFrame#SidebarHeader {
                border-bottom: 1px solid #f0f0f0;
            }
            
            QFrame#SidebarFooter {
                border-top: 1px solid #f0f0f0;
                background-color: #fafafa;
            }

            /* ETIQUETAS DE MENÚ */
            QLabel#MenuLabel {
                color: #a0a0a0;
                font-size: 11px;
                font-weight: bold;
                padding-left: 10px;
                letter-spacing: 0.5px;
            }

            /* BOTONES DE NAVEGACIÓN */
            QPushButton#NavButton {
                background-color: transparent;
                color: #555;
                text-align: left;
                padding: 12px 20px;
                border-radius: 8px;
                font-size: 14px;
                border: none;
                margin-bottom: 2px;
            }
            
            QPushButton#NavButton:hover {
                background-color: #f5f7fa;
                color: #333;
            }

            /* ESTADO ACTIVO (SELECCIONADO) */
            QPushButton#NavButton:checked {
                background-color: #e6f0ff; /* Azul muy suave */
                color: #0069d9; /* Azul corporativo */
                font-weight: bold;
                border-right: 4px solid #0069d9; /* Indicador derecho */
            }

            /* ÁREA DE CONTENIDO */
            QWidget#ContentArea {
                background-color: #f4f7f6;
            }
            
            /* SCROLLBARS (Opcional, para que se vean bien en Windows) */
            QScrollBar:vertical {
                border: none;
                background: #f1f1f1;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #c1c1c1;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
            }
        """)

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # Fuente Global
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec_())