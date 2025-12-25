import os
import sqlite3
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QMessageBox, QToolButton, QApplication, 
    QFrame, QGraphicsDropShadowEffect, QDesktopWidget
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor, QCursor

# Importación segura de la base de datos
try:
    from database.db import get_connection, log_db
except ImportError:
    def get_connection(): return sqlite3.connect("data/inventario.db")
    def log_db(msg): print(msg)

class LoginWindow(QWidget):
    """
    Ventana de inicio de sesión Centrada y Profesional.
    """
    
    # --- Constantes de Diseño ---
    WINDOW_TITLE = "Acceso al Sistema - Autopartes"
    COLOR_PRIMARY = "#0056b3"       
    COLOR_HOVER = "#004494"         
    COLOR_BG = "#f4f6f9"            
    COLOR_CARD = "#ffffff"          
    COLOR_TEXT = "#333333"          
    COLOR_BORDER = "#ced4da"        
    COLOR_FOCUS = "#80bdff"         

    def __init__(self):
        super().__init__()
        self.user_data = None 
        self._configure_window()
        self._init_ui()
        self._setup_animation()

    def _configure_window(self):
        """Configura la ventana para que sea fija y centrada."""
        self.setWindowTitle(self.WINDOW_TITLE)
        
        # 1. Definimos un tamaño fijo elegante
        self.setFixedSize(500, 680) 
        
        # 2. Estilo de fondo
        self.setStyleSheet(f"background-color: {self.COLOR_BG};")
        
        # 3. Icono
        icon_path = self.resource_path("assets/logo.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        # 4. CENTRAR LA VENTANA EN LA PANTALLA
        self._center_on_screen()

    def _center_on_screen(self):
        """Calcula la geometría de la pantalla y centra la ventana."""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def resource_path(self, relative_path: str) -> str:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        return os.path.join(base_dir, relative_path)

    def _init_ui(self):
        """Construye la interfaz gráfica."""
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setAlignment(Qt.AlignCenter)
        
        # --- TARJETA DE LOGIN ---
        self.card_frame = QFrame()
        # La tarjeta ocupa casi todo el espacio de la ventana fija
        self.card_frame.setFixedWidth(420) 
        self.card_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.COLOR_CARD};
                border-radius: 15px;
                border: 1px solid #e0e0e0;
            }}
        """)
        
        # Sombra suave
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 40)) 
        self.card_frame.setGraphicsEffect(shadow)

        # --- CONTENIDO ---
        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setContentsMargins(30, 40, 30, 40)
        card_layout.setSpacing(15)

        # 1. Logo
        self.logo_label = QLabel(alignment=Qt.AlignCenter)
        logo_path = self.resource_path("assets/logo.ico") 
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
        else:
            self.logo_label.setText("📦") 
            self.logo_label.setFont(QFont("Segoe UI Emoji", 50))
        
        # 2. Textos
        title_label = QLabel("Bienvenido", alignment=Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title_label.setStyleSheet(f"color: {self.COLOR_TEXT}; border: none;")
        
        subtitle_label = QLabel("Ingresa tus credenciales", alignment=Qt.AlignCenter)
        subtitle_label.setFont(QFont("Segoe UI", 10))
        subtitle_label.setStyleSheet("color: #6c757d; border: none; margin-bottom: 10px;")

        # 3. Inputs
        self.usuario_input = self._create_styled_input("Usuario", "assets/user.png")
        
        # Contenedor Password
        pass_container = QFrame()
        pass_container.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {self.COLOR_BORDER};
                border-radius: 8px;
                background-color: white;
            }}
            QFrame:hover {{ border: 1px solid #b0b0b0; }}
        """)
        pass_layout = QHBoxLayout(pass_container)
        pass_layout.setContentsMargins(0, 0, 5, 0)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(45)
        self.password_input.setFont(QFont("Segoe UI", 11))
        self.password_input.setStyleSheet("border: none; padding-left: 10px;")
        
        self.toggle_btn = QToolButton()
        self.toggle_btn.setText("👁️")
        self.toggle_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.toggle_btn.setStyleSheet("background: transparent; border: none; font-size: 16px;")
        self.toggle_btn.clicked.connect(self._toggle_password)

        pass_layout.addWidget(self.password_input)
        pass_layout.addWidget(self.toggle_btn)

        # 4. Botón Login
        self.btn_login = QPushButton("INICIAR SESIÓN")
        self.btn_login.setFixedHeight(50)
        self.btn_login.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_login.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.btn_login.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.COLOR_PRIMARY};
                color: white;
                border-radius: 8px;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{ background-color: {self.COLOR_HOVER}; }}
            QPushButton:pressed {{ background-color: #003366; }}
        """)
        
        # Eventos Enter
        self.usuario_input.returnPressed.connect(self._attempt_login)
        self.password_input.returnPressed.connect(self._attempt_login)
        self.btn_login.clicked.connect(self._attempt_login)

        # 5. Footer
        footer_label = QLabel("Sistema de Ventas v2.0", alignment=Qt.AlignCenter)
        footer_label.setStyleSheet("color: #adb5bd; font-size: 9px; margin-top: 10px; border: none;")

        # Armar tarjeta
        card_layout.addWidget(self.logo_label)
        card_layout.addWidget(title_label)
        card_layout.addWidget(subtitle_label)
        card_layout.addSpacing(10)
        card_layout.addWidget(QLabel("Usuario:", styleSheet="border:none; font-weight:bold; color:#555;"))
        card_layout.addWidget(self.usuario_input)
        card_layout.addWidget(QLabel("Contraseña:", styleSheet="border:none; font-weight:bold; color:#555;"))
        card_layout.addWidget(pass_container)
        card_layout.addSpacing(20)
        card_layout.addWidget(self.btn_login)
        card_layout.addStretch()
        card_layout.addWidget(footer_label)

        # Agregar tarjeta centrada
        main_layout.addWidget(self.card_frame)

    def _create_styled_input(self, placeholder, icon=None):
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setFixedHeight(45)
        inp.setFont(QFont("Segoe UI", 11))
        inp.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {self.COLOR_BORDER};
                border-radius: 8px;
                padding-left: 10px;
                background-color: white;
            }}
            QLineEdit:hover {{ border: 1px solid #b0b0b0; }}
            QLineEdit:focus {{ border: 2px solid {self.COLOR_FOCUS}; }}
        """)
        return inp

    def _setup_animation(self):
        """Animación suave de entrada."""
        self.animation = QPropertyAnimation(self.card_frame, b"windowOpacity")
        self.animation.setDuration(800)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.OutQuart)
        self.animation.start()

    # ---------- Lógica del Negocio ----------

    def _center_on_screen(self):
        """Centra la ventana en el monitor actual."""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def _toggle_password(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_btn.setText("🙈") 
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_btn.setText("👁️") 

    def _attempt_login(self):
        usuario = self.usuario_input.text().strip()
        password = self.password_input.text().strip()

        if not usuario or not password:
            QMessageBox.warning(self, "Atención", "Ingresa usuario y contraseña.")
            return

        self.btn_login.setEnabled(False)
        self.btn_login.setText("Cargando...")
        QApplication.processEvents()

        user_data = self._authenticate_user(usuario, password)

        if user_data:
            self._open_dashboard(user_data)
        else:
            QMessageBox.critical(self, "Error", "Credenciales incorrectas.")
            self.password_input.clear()
            self.btn_login.setEnabled(True)
            self.btn_login.setText("INICIAR SESIÓN")

    def _authenticate_user(self, usuario, password):
        try:
            conn = get_connection()
            if not conn: return None

            cursor = conn.cursor()
            # Recuperamos ID para evitar errores en Ventas
            sql = "SELECT id, nombre, rol FROM usuarios WHERE usuario=? AND contrasena=?"
            cursor.execute(sql, (usuario, password))
            result = cursor.fetchone()
            conn.close()

            if result:
                return {
                    "id": result["id"],        
                    "nombre": result["nombre"],
                    "rol": result["rol"]
                }
            return None

        except Exception as e:
            log_db(f"Error Login: {e}")
            return None

    def _open_dashboard(self, user_data):
        try:
            from gui.dashboard import DashboardWindow
            
            # Pasar datos al dashboard
            self.dashboard = DashboardWindow()
            
            # Inyectar datos de usuario (IMPORTANTE PARA VENTAS)
            if hasattr(self.dashboard, 'usuario_id'):
                self.dashboard.usuario_id = user_data['id']
            if hasattr(self.dashboard, 'usuario_actual_nombre'):
                self.dashboard.usuario_actual_nombre = user_data['nombre']

            self.dashboard.show()
            self.close()
            
        except ImportError:
            QMessageBox.critical(self, "Error", "No se encuentra 'gui/dashboard.py'")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo al abrir Dashboard: {e}")
            self.btn_login.setEnabled(True)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())