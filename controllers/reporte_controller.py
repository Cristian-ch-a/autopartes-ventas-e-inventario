import sqlite3
from database.db import get_connection, log_db
from typing import List, Dict, Any

class ReporteVentasController:
    """
    Controlador avanzado para la generación de reportes y estadísticas.
    Optimizado para consultas rápidas y seguras.
    """

    @staticmethod
    def ventas_por_fecha(fecha_inicio: str, fecha_fin: str) -> List[Dict[str, Any]]:
        """
        Obtiene el detalle de ventas en un rango de fechas.
        Retorna una lista de diccionarios lista para ser renderizada en tablas.
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                # Query optimizada con JOINs explícitos
                sql = """
                    SELECT 
                        v.id,
                        v.fecha_venta,
                        p.codigo AS codigo_producto,
                        p.nombre AS nombre_producto,
                        v.cantidad,
                        v.precio_unitario,
                        v.total,
                        u.nombre AS vendedor  -- Obtenemos el nombre real, no el usuario
                    FROM ventas v
                    INNER JOIN productos p ON v.id_producto = p.id
                    LEFT JOIN usuarios u ON v.vendido_por = u.id
                    WHERE date(v.fecha_venta) BETWEEN date(?) AND date(?)
                    ORDER BY v.fecha_venta DESC, v.id DESC
                """
                cursor.execute(sql, (fecha_inicio, fecha_fin))
                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            log_db(f"Error Reporte Detallado: {e}")
            return []

    @staticmethod
    def obtener_kpis(fecha_inicio: str, fecha_fin: str) -> Dict[str, float]:
        """
        Calcula los indicadores clave (KPIs) para el rango seleccionado.
        Ideal para mostrar en tarjetas de resumen (Dashboard).
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                sql = """
                    SELECT 
                        COUNT(*) as total_transacciones,
                        COALESCE(SUM(total), 0) as ingresos_totales,
                        COALESCE(SUM(cantidad), 0) as productos_vendidos
                    FROM ventas 
                    WHERE date(fecha_venta) BETWEEN date(?) AND date(?)
                """
                cursor.execute(sql, (fecha_inicio, fecha_fin))
                row = cursor.fetchone()
                
                if row:
                    return {
                        "transacciones": row["total_transacciones"],
                        "ingresos": row["ingresos_totales"],
                        "productos": row["productos_vendidos"]
                    }
                return {"transacciones": 0, "ingresos": 0.0, "productos": 0}

        except Exception as e:
            log_db(f"Error KPIs: {e}")
            return {"transacciones": 0, "ingresos": 0.0, "productos": 0}