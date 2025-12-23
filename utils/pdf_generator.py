# utils/pdf_generator.py
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTES_DIR = os.path.join(BASE_DIR, "reportes")
os.makedirs(REPORTES_DIR, exist_ok=True)

def generar_ficha_pdf(producto: dict):
    """
    Genera un PDF con la ficha técnica del producto.
    Retorna la ruta del archivo generado.
    """
    filename = f"ficha_{producto.get('codigo','SIN_CODIGO')}.pdf"
    path = os.path.join(REPORTES_DIR, filename)

    doc = SimpleDocTemplate(path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Título
    story.append(Paragraph(f"Ficha Técnica - {producto.get('codigo','')}", styles["Title"]))
    story.append(Spacer(1, 12))

    # Datos básicos
    story.append(Paragraph(f"<b>Nombre:</b> {producto.get('nombre','')}", styles["Normal"]))
    story.append(Paragraph(f"<b>Aplicación:</b> {producto.get('aplicacion','')}", styles["Normal"]))
    story.append(Paragraph(f"<b>Cód. Original:</b> {producto.get('cod_original','')}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Medidas
    if producto.get("medidas"):
        data = [["Medida", "Valor"]]
        for k, v in producto["medidas"].items():
            data.append([k, str(v)])
        tabla = Table(data)
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.grey),
            ("TEXTCOLOR",(0,0),(-1,0),colors.whitesmoke),
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("GRID",(0,0),(-1,-1),1,colors.black),
        ]))
        story.append(tabla)
        story.append(Spacer(1, 12))

    # Imagen
    if producto.get("imagen_path") and os.path.exists(producto["imagen_path"]):
        img = Image(producto["imagen_path"], width=200, height=200)
        story.append(img)

    doc.build(story)
    return path
