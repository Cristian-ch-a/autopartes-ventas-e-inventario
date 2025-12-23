# controllers/venta_controller.py
import sqlite3
from typing import Dict, Any, List
from database.db import get_connection, log_db 

class VentaController:

    @staticmethod
    def registrar_venta(codigo_producto: str, cantidad: int, precio_unitario: float, vendido_por: int) -> Dict[str, Any]:
        """
        Registra una venta de forma atómica (Todo o nada).
        """
        if cantidad <= 0: 
            return {"status": False, "message": "La cantidad debe ser mayor a 0."}
        
        conn = get_connection()
        if not conn: 
            return {"status": False, "message": "No hay conexión con la base de datos."}

        try:
            # 'with conn' maneja el commit/rollback automáticamente
            with conn: 
                cursor = conn.cursor()
                
                # 1. Verificar existencia y stock del producto
                cursor.execute("SELECT id, stock, nombre FROM productos WHERE codigo = ?", (codigo_producto,))
                producto = cursor.fetchone()
                
                if not producto:
                    return {"status": False, "message": f"El producto '{codigo_producto}' no existe."}
                
                id_prod = producto['id']
                stock_actual = producto['stock']
                
                if stock_actual < cantidad:
                    return {"status": False, "message": f"Stock insuficiente. Disponible: {stock_actual}."}

                # 2. Calcular total
                total = precio_unitario * cantidad
                
                # 3. Insertar Venta
                # Aquí es donde fallaba si 'vendido_por' no era un ID válido
                cursor.execute("""
                    INSERT INTO ventas (id_producto, cantidad, precio_unitario, total, vendido_por, fecha_venta)
                    VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'))
                """, (id_prod, cantidad, precio_unitario, total, vendido_por))
                
                venta_id = cursor.lastrowid

                # 4. Descontar Stock
                cursor.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (cantidad, id_prod))
                
                log_db(f"Venta ID {venta_id} OK. Prod: {codigo_producto}, Cant: {cantidad}, User: {vendido_por}")

                return {
                    "status": True, 
                    "message": "Venta registrada correctamente.", 
                    "total": total,
                    "nuevo_stock": stock_actual - cantidad
                }

        except sqlite3.IntegrityError as e:
            # Este mensaje saldrá si el usuario ID no existe en la tabla usuarios
            log_db(f"Error Integridad Venta: {e} | Usuario ID intentado: {vendido_por}")
            return {"status": False, "message": f"Error de Base de Datos: El usuario (ID {vendido_por}) no existe o el producto es inválido."}
            
        except Exception as e:
            log_db(f"Error General Venta: {e}")
            return {"status": False, "message": f"Error inesperado: {str(e)}"}
        finally:
            conn.close()

    @staticmethod
    def obtener_historial() -> List[Dict[str, Any]]:
        conn = get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT v.id, p.codigo as codigo_producto, p.nombre as nombre_producto, 
                       v.cantidad, v.precio_unitario, v.total, v.fecha_venta 
                FROM ventas v
                LEFT JOIN productos p ON v.id_producto = p.id
                ORDER BY v.id DESC LIMIT 50
            """)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            log_db(f"Error Historial: {e}")
            return []
        finally:
            conn.close()