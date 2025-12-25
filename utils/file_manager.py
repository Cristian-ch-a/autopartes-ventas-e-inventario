# utils/file_manager.py
import os, shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(BASE_DIR, "assets", "imagenes_productos")

def guardar_imagen_producto(ruta_origen, codigo_producto):
    """
    Copia la imagen seleccionada a /assets/imagenes_productos/
    Renombra con el código del producto.
    Retorna la ruta relativa.
    """
    if not os.path.exists(IMG_DIR):
        os.makedirs(IMG_DIR)

    ext = os.path.splitext(ruta_origen)[1].lower()
    nombre_destino = f"{codigo_producto}{ext}"
    ruta_destino = os.path.join(IMG_DIR, nombre_destino)
    shutil.copy(ruta_origen, ruta_destino)

    # Guardamos ruta relativa para la BD
    ruta_relativa = os.path.relpath(ruta_destino, BASE_DIR)
    return ruta_relativa
