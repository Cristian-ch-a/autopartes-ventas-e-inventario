# database/migrate_add_categoria.py
import os, sqlite3, shutil, datetime

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB = os.path.join(BASE, "data", "inventario.db")

# backup
if os.path.exists(DB):
    bak = DB + "." + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".bak"
    shutil.copy2(DB, bak)
    print("Backup creado:", bak)
else:
    print("No se encontró base de datos en:", DB)
    # crea carpeta data si no existe
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    print("Carpeta data creada. Aún no hay archivo .db; las migraciones crearán la DB cuando se ejecute init_db si hace falta.")

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("PRAGMA table_info('productos')")
cols = [r[1] for r in cur.fetchall()]

if "categoria" not in cols:
    try:
        cur.execute("ALTER TABLE productos ADD COLUMN categoria TEXT;")
        cur.execute("UPDATE productos SET categoria = 'Sin categoría' WHERE categoria IS NULL;")
        conn.commit()
        print("✅ Columna 'categoria' añadida y valores inicializados.")
    except Exception as e:
        print("❌ Error al añadir la columna:", e)
else:
    print("ℹ️ La columna 'categoria' ya existe. No se hizo nada.")

conn.close()
