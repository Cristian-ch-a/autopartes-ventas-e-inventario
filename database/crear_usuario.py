import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "inventario.db")

usuario = "admin"
contrasena = "1234"
nombre = "Administrador"
rol = "admin"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("""
        INSERT INTO usuarios (nombre, usuario, contrasena, rol)
        VALUES (?, ?, ?, ?)
    """, (nombre, usuario, contrasena, rol))
    conn.commit()
    print("✅ Usuario creado correctamente.")
except sqlite3.IntegrityError:
    print("⚠️ El usuario ya existe.")
finally:
    conn.close()

