# database/db.py
import sqlite3
import os
import sys
from datetime import datetime

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = get_base_path()
DB_FOLDER = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DB_FOLDER, "inventario.db")
LOG_PATH = os.path.join(DB_FOLDER, "system_log.txt")

# Aseguramos que la carpeta de datos exista
if not os.path.exists(DB_FOLDER):
    try:
        os.makedirs(DB_FOLDER, exist_ok=True)
    except OSError as e:
        # Si no podemos crear la carpeta, lanzar y registrar: esto es crítico
        print(f"Error crítico: No se pudo crear carpeta de datos: {e}")
        raise

def get_connection() -> sqlite3.Connection:
    """
    Crea y retorna una conexión segura a la base de datos SQLite.
    Si ocurre un error, registra y propaga la excepción.
    """
    try:
        conn = sqlite3.connect(DB_PATH, timeout=20)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        # Registrar y propagar (no devolver None)
        log_db(f"ERROR CRÍTICO DE CONEXIÓN: {e}")
        raise

def log_db(message: str) -> None:
    """
    Registra eventos y errores en un archivo de texto para auditoría.
    No debe interrumpir la aplicación si falla (fallo silencioso en log).
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        # No propagamos errores del log para no enmascarar errores reales.
        pass
