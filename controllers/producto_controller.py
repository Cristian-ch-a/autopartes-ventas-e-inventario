# controllers/producto_controller.py
import os
import sqlite3
import json
from typing import Optional, Dict, Any, List
from database.db import get_connection, log_db

def _get_columns() -> List[str]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("PRAGMA table_info('productos')")
    cols = [r[1] for r in cur.fetchall()]
    conn.close()
    return cols

class ProductoController:
    @staticmethod
    def obtener_todos() -> List[tuple]:
        cols = _get_columns()
        select_map = {
            "codigo": "codigo" if "codigo" in cols else "'' AS codigo",
            "nombre": "nombre" if "nombre" in cols else "'' AS nombre",
            "categoria": "categoria" if "categoria" in cols else "'' AS categoria",
            "stock": "stock" if "stock" in cols else "0 AS stock",
            "precio": "precio" if "precio" in cols else "0.0 AS precio",
        }
        sql = f"SELECT {', '.join(select_map.values())} FROM productos ORDER BY nombre COLLATE NOCASE"
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql)
        rows = [tuple(r) for r in cur.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def insertar(
        codigo: str,
        nombre: str,
        tipo_repuesto: Optional[str] = "",
        categoria: Optional[str] = "",
        aplicacion: Optional[str] = "",
        cod_original: Optional[str] = "",
        descripcion: Optional[str] = "",
        medidas_dict: Optional[Dict[str, Any]] = None,
        stock: int = 0,
        precio: float = 0.0,
        imagen_path: Optional[str] = None
    ) -> int:
        if not codigo or not nombre:
            raise ValueError("Código y nombre son obligatorios.")

        columnas = _get_columns()
        conn = get_connection()
        cur = conn.cursor()
        try:
            medidas_json = json.dumps(medidas_dict or {}, ensure_ascii=False)
            imagen_nombre = os.path.basename(imagen_path) if imagen_path else None

            campos_validos = {
                "codigo": codigo.strip(),
                "nombre": nombre.strip(),
                "tipo_repuesto": (tipo_repuesto or "").strip(),
                "categoria": (categoria or "").strip(),
                "aplicacion": (aplicacion or "").strip(),
                "cod_original": (cod_original or "").strip(),
                "descripcion": (descripcion or "").strip(),
                "medidas": medidas_json,
                "stock": int(stock or 0),
                "precio": float(precio or 0.0),
                "imagen": imagen_nombre
            }

            campos = [c for c in campos_validos.keys() if c in columnas]
            valores = [campos_validos[c] for c in campos]

            if not campos:
                raise Exception("No hay campos válidos para insertar en la tabla productos.")

            placeholders = ",".join(["?"] * len(campos))
            sql = f"INSERT INTO productos ({','.join(campos)}) VALUES ({placeholders})"
            cur.execute(sql, valores)
            conn.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError as ie:
            conn.rollback()
            raise Exception("El código de producto ya existe.") from ie
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def obtener_por_codigo(codigo: str) -> Optional[Dict[str, Any]]:
        if not codigo:
            return None

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM productos WHERE codigo = ?", (codigo,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return None

        producto = dict(row)
        medidas_val = producto.get("medidas")
        if isinstance(medidas_val, str) and medidas_val.strip() != "":
            try:
                producto["medidas"] = json.loads(medidas_val)
            except json.JSONDecodeError:
                producto["medidas"] = {}
        else:
            producto["medidas"] = producto.get("medidas") or {}

        for campo in ["aplicacion", "cod_original", "tipo_repuesto", "categoria", "descripcion"]:
            producto.setdefault(campo, "")

        producto["imagen_path"] = producto.get("imagen") or None
        return producto

    @staticmethod
    def actualizar(codigo_original: str, **kwargs) -> bool:
        if not codigo_original:
            raise ValueError("Debe especificar el código original para actualizar.")

        columnas = _get_columns()
        conn = get_connection()
        cur = conn.cursor()
        try:
            if "medidas" in kwargs and isinstance(kwargs["medidas"], dict):
                kwargs["medidas"] = json.dumps(kwargs["medidas"], ensure_ascii=False)

            items = [(k, v) for k, v in kwargs.items() if k in columnas]
            if not items:
                raise ValueError("No hay campos válidos para actualizar.")

            cols_sql = ", ".join([f"{k}=?" for k, _ in items])
            valores = [v for _, v in items]
            valores.append(codigo_original)

            sql = f"UPDATE productos SET {cols_sql} WHERE codigo = ?"
            cur.execute(sql, valores)
            if cur.rowcount == 0:
                conn.rollback()
                return False
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def eliminar(codigo: str) -> bool:
        if not codigo:
            return False
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM productos WHERE codigo = ?", (codigo,))
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
