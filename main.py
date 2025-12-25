# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QFont, QIcon
from gui.login import LoginWindow

# Función para aplicar estilos externos (si existieran en el futuro)
def aplicar_estilos(app):
    qss_path = os.path.join("assets", "style.qss")
    if os.path.exists(qss_path):
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
        except:
            pass

# Manejador de errores graves al iniciar
def mostrar_error(e):
    if not QApplication.instance():
        app = QApplication(sys.argv)
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Error Fatal")
    msg.setText("Ocurrió un error inesperado al iniciar el sistema.")
    msg.setInformativeText(str(e))
    msg.exec_()

def main():
    try:
        # 1. INICIALIZAR MOTOR DE LA APP
        app = QApplication(sys.argv)
        app.setApplicationName("Sistema de Ventas e Inventario - Autopartes RAFO")
        
        # Fuente Global Moderna
        app.setFont(QFont("Segoe UI", 10))

        # 2. ICONO DE LA VENTANA (Barra de tareas)
        icon_path = os.path.join("assets", "logo.ico")
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))

        # 3. CARGAR ESTILOS
        aplicar_estilos(app)

        # 4. ABRIR VENTANA DE LOGIN
        ventana_login = LoginWindow()
        ventana_login.show()

        # 5. EJECUTAR BUCLE PRINCIPAL
        sys.exit(app.exec_())

    except Exception as e:
        mostrar_error(e)

if __name__ == "__main__":
    main()