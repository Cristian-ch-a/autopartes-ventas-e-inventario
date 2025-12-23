# migra_db.py (ejecutar una vez)
import sqlite3, json, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # ajusta si llamas desde otro lado
DB = os.path.join(BASE_DIR, "data", "inventario.db")

con = sqlite3.connect(DB)
cur = con.cursor()

# 1) crear nueva tabla temporal si no existe estructura
cur.execute("""
CREATE TABLE IF NOT EXISTS productos_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE,
    nombre TEXT,
    descripcion TEXT,
    tipo_repuesto TEXT,
    categoria TEXT,
    aplicacion TEXT,
    cod_original TEXT,
    medidas TEXT,
    stock INTEGER DEFAULT 0,
    precio REAL DEFAULT 0.0,
    imagen TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# 2) copiar filas transformando columnas existentes
cur.execute("PRAGMA table_info(productos)")
cols = [r[1] for r in cur.fetchall()]

# Si existe la tabla antigua, copiar con heurística:
try:
    cur.execute("SELECT * FROM productos")
    rows = cur.fetchall()
    # formar insert dinámico
    for r in rows:
        rowdict = {}
        for i, c in enumerate(cols):
            rowdict[c] = r[i]
        # asegúrate de convertir medidas si vienen en múltiples columnas u otros formatos
        medidas = rowdict.get("medidas")
        if medidas is None:
            medidas = "{}"
        # si medidas ya es texto JSON vacío o dict-like, usar tal cual
        cur.execute("""
            INSERT OR IGNORE INTO productos_new
            (codigo,nombre,descripcion,tipo_repuesto,categoria,aplicacion,cod_original,medidas,stock,precio,imagen)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            rowdict.get("codigo"),
            rowdict.get("nombre"),
            rowdict.get("descripcion"),
            rowdict.get("tipo_repuesto"),
            rowdict.get("categoria"),
            rowdict.get("aplicacion"),
            rowdict.get("cod_original"),
            medidas,
            rowdict.get("stock") or 0,
            rowdict.get("precio") or 0.0,
            rowdict.get("imagen")
        ))
    con.commit()
except Exception:
    # si no hay tabla o falla lectura, se ignora
    pass

# 3) renombrar tablas (haz backup antes)
# cur.execute("ALTER TABLE productos RENAME TO productos_old")
# cur.execute("ALTER TABLE productos_new RENAME TO productos")
# con.commit()

con.close()
