# reset_db.py
"""
Script profesional para crear/actualizar la base de datos SQLite
a partir del archivo database/esquemas.sql.

- Hace backup de inventario.db si ya existe (en carpeta data/backups).
- Activa PRAGMA foreign_keys = ON.
- Ejecuta todo el SQL en esquemas.sql usando executescript.
- Uso: python reset_db.py
"""

import os
import shutil
import sqlite3
from datetime import datetime

# --- Ajusta aquí si tu estructura es distinta ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))            # carpeta autopa rtes_ventas
DB_DIR = os.path.join(PROJECT_ROOT, "data")
DB_PATH = os.path.join(DB_DIR, "inventario.db")
SQL_DIR = os.path.join(PROJECT_ROOT, "database")
SQL_PATH = os.path.join(SQL_DIR, "esquemas.sql")

BACKUPS_DIR = os.path.join(DB_DIR, "backups")

# ---------------------------------------------------------------------
def ensure_dirs():
    os.makedirs(DB_DIR, exist_ok=True)
    os.makedirs(BACKUPS_DIR, exist_ok=True)

def backup_db():
    if os.path.exists(DB_PATH):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = os.path.basename(DB_PATH)
        backup_name = f"{os.path.splitext(base)[0]}_{ts}.db"
        backup_path = os.path.join(BACKUPS_DIR, backup_name)
        shutil.copy2(DB_PATH, backup_path)
        print(f"[INFO] Backup creado: {backup_path}")
    else:
        print("[INFO] No existe inventario.db previo — no se crea backup.")

def load_sql_script(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo SQL: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def apply_schema(sql_script):
    # Conectar y ejecutar. usamos executescript para permitir múltiples statements.
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        # Asegurar claves foráneas activadas
        cur.execute("PRAGMA foreign_keys = ON;")
        # Ejecutar todo el script
        cur.executescript(sql_script)
        conn.commit()
    finally:
        conn.close()

def main():
    print("== Reset DB - inicio ==")
    ensure_dirs()
    backup_db()

    try:
        sql_script = load_sql_script(SQL_PATH)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return

    try:
        apply_schema(sql_script)
        print("[OK] Esquema aplicado correctamente.")
        print(f"[OK] Base de datos creada/actualizada en: {DB_PATH}")
    except sqlite3.DatabaseError as db_e:
        print(f"[ERROR] SQLite: {db_e}")
    except Exception as e:
        print(f"[ERROR] Ocurrió un error: {e}")

if __name__ == "__main__":
    main()
