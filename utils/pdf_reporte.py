from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime
import os

class PDFReportes:
    """
    Generador de Reportes PDF Profesionales usando ReportLab.
    Incluye encabezados, pie de página y tablas estilizadas.
    """

    @staticmethod
    def generar_pdf_reporte(titulo, datos, columnas, ruta_salida, resumen=None):
        """
        Genera el archivo PDF.
        :param resumen: Diccionario opcional con KPIs para mostrar al inicio.
        """
        try:
            doc = SimpleDocTemplate(
                ruta_salida, 
                pagesize=A4,
                rightMargin=30, leftMargin=30,
                topMargin=30, bottomMargin=30
            )
            
            elementos = []
            estilos = getSampleStyleSheet()

            # --- 1. Encabezado ---
            estilo_titulo = ParagraphStyle(
                'TituloPersonalizado', 
                parent=estilos['Title'], 
                fontSize=18, 
                textColor=colors.HexColor("#0056b3"),
                spaceAfter=10
            )
            
            estilo_subtitulo = ParagraphStyle(
                'Subtitulo', 
                parent=estilos['Normal'], 
                fontSize=10, 
                textColor=colors.gray, 
                alignment=TA_RIGHT
            )

            # Fecha de generación
            fecha_gen = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            elementos.append(Paragraph(f"Generado el: {fecha_gen}", estilo_subtitulo))
            elementos.append(Spacer(1, 10))
            
            # Título Principal
            elementos.append(Paragraph(titulo, estilo_titulo))
            elementos.append(Spacer(1, 20))

            # --- 2. Sección de Resumen (KPIs) ---
            if resumen:
                kpi_data = [
                    ["Ingresos Totales", "Transacciones", "Productos Vendidos"],
                    [
                        f"{resumen.get('ingresos', 0):,.2f} Bs", 
                        str(resumen.get('transacciones', 0)), 
                        str(resumen.get('productos', 0))
                    ]
                ]
                
                tabla_kpi = Table(kpi_data, colWidths=[6*cm, 5*cm, 5*cm])
                tabla_kpi.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e9ecef")),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,1), (-1,1), 12),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                    ('TOPPADDING', (0,0), (-1,-1), 10),
                    ('GRID', (0,0), (-1,-1), 1, colors.white),
                    ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#ced4da")),
                ]))
                elementos.append(tabla_kpi)
                elementos.append(Spacer(1, 20))

            # --- 3. Tabla de Datos ---
            if datos:
                # Extraer encabezados y filas
                keys_columnas = [col[0] for col in columnas]
                labels_columnas = [col[1] for col in columnas]
                
                data_matriz = [labels_columnas]
                
                for d in datos:
                    fila = []
                    for key in keys_columnas:
                        valor = d.get(key, "")
                        # Formato básico para números
                        if isinstance(valor, float):
                            valor = f"{valor:.2f}"
                        fila.append(str(valor))
                    data_matriz.append(fila)

                # Definir anchos de columna dinámicos (ajuste simple)
                # Se asume A4 ancho ~ 19cm útiles. Repartimos.
                # ID, Fecha, Cod, Prod, Cant, Unit, Total
                anchos = [1.2*cm, 2.5*cm, 2.5*cm, 6*cm, 1.5*cm, 2.5*cm, 2.5*cm]
                
                tabla_datos = Table(data_matriz, colWidths=anchos, repeatRows=1)
                
                # Estilo Profesional
                estilo_tabla = TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#343a40")), # Header Oscuro
                    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                    ('ALIGN', (0,0), (-1,0), 'CENTER'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,0), 10),
                    
                    ('BOTTOMPADDING', (0,0), (-1,0), 8),
                    ('BACKGROUND', (0,1), (-1,-1), colors.white),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#dee2e6")),
                    ('ALIGN', (-2,1), (-1,-1), 'RIGHT'), # Alinear precios a la derecha
                    ('FONTSIZE', (0,1), (-1,-1), 9),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8f9fa")]), # Filas Zebra
                ])
                
                tabla_datos.setStyle(estilo_tabla)
                elementos.append(tabla_datos)
            else:
                elementos.append(Paragraph("No se encontraron registros para este periodo.", estilos['Normal']))

            # --- 4. Generar ---
            doc.build(elementos)
            return True

        except Exception as e:
            print(f"Error generando PDF: {e}")
            return False