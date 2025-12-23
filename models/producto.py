# models/producto.py
# ----------------------------------------------------
# Clase Producto — Modelo limpio, profesional y escalable
# ----------------------------------------------------

class Producto:
    def __init__(
        self,
        id_producto=None,
        codigo="",
        nombre="",
        categoria="",
        marca="",
        descripcion="",
        stock=0,
        precio=0.0,
        imagen_path=None,
        ancho=None,
        alto=None,
        profundidad=None,
        peso=None
    ):
        self.id_producto = id_producto
        self.codigo = codigo
        self.nombre = nombre
        self.categoria = categoria
        self.marca = marca
        self.descripcion = descripcion
        self.stock = stock
        self.precio = precio
        self.imagen_path = imagen_path

        # Medidas
        self.ancho = ancho
        self.alto = alto
        self.profundidad = profundidad
        self.peso = peso

    def to_dict(self):
        """Devuelve el producto en formato dict para su uso en controladores."""
        return {
            "id_producto": self.id_producto,
            "codigo": self.codigo,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "marca": self.marca,
            "descripcion": self.descripcion,
            "stock": self.stock,
            "precio": self.precio,
            "imagen_path": self.imagen_path,
            "ancho": self.ancho,
            "alto": self.alto,
            "profundidad": self.profundidad,
            "peso": self.peso
        }

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
