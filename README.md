# 🏎️ Sistema de Ventas e Inventario – Autopartes

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-GUI-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

Aplicación de escritorio desarrollada en **Python** para la gestión de ventas e inventario de autopartes.  
El proyecto aplica una **arquitectura modular**, una **interfaz gráfica clara** y **persistencia de datos local**, orientado tanto al aprendizaje práctico como a un uso real en pequeños negocios.

---

## ✨ Características principales

- 📦 **Gestión de productos**  
  Operaciones CRUD completas: altas, bajas, modificaciones y consultas.

- 📉 **Control de inventario**  
  Seguimiento de stock y disponibilidad de productos.

- 💰 **Registro de ventas**  
  Procesamiento ordenado de transacciones.

- 🖥️ **Interfaz gráfica de escritorio**  
  Construida con **PyQt5**, ofreciendo una experiencia de usuario nativa y fluida.

- 💾 **Persistencia local**  
  Base de datos **SQLite**, sin necesidad de servidor.

---

## 🛠️ Stack tecnológico

| Tecnología | Uso |
|-----------|-----|
| **Python 3** | Lógica principal del sistema |
| **PyQt5** | Interfaz gráfica (GUI) |
| **SQLite** | Base de datos relacional local |
| **Git / GitHub** | Control de versiones |

---

## 📂 Arquitectura del proyecto

El proyecto está organizado por módulos para facilitar la lectura del código, el mantenimiento y la escalabilidad.

```bash
autopartes-ventas-e-inventario/
│
├── assets/         # Recursos visuales
├── controllers/    # Lógica de negocio y control
├── models/         # Modelos de datos y consultas
├── gui/            # Interfaces gráficas (PyQt5)
├── database/       # Configuración y scripts de base de datos
├── utils/          # Utilidades generales
│
├── main.py         # Punto de entrada principal
├── reset_db.py     # Inicialización / reinicio de la base de datos
├── README.md       # Documentación del proyecto
└── .gitignore
```
---

## 🚀 Guía de instalación
1️⃣ Clonar el repositorio
```bash
git clone https://github.com/Cristian-ch-a/autopartes-ventas-e-inventario.git
cd autopartes-ventas-e-inventario
```
## 2️⃣ Crear y activar entorno virtual

Se recomienda utilizar un entorno virtual para aislar dependencias.

Windows (PowerShell)
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```
Linux / macOS
```bash
python3 -m venv venv
source venv/bin/activate
```
3️⃣ Instalar dependencias
```bash
pip install PyQt5
```
Si existe el archivo de requerimientos:
```bash
pip install -r requirements.txt
```
4️⃣ Inicializar la base de datos

## ⚠️ IMPORTANTE
El archivo de base de datos (.db) no se incluye en el repositorio por seguridad y buenas prácticas.

Ejecuta el siguiente script para crear una base de datos limpia:
```bash
python reset_db.py
```
5️⃣ Ejecutar la aplicación
```bash
python main.py
```
---

## 🎯 Objetivos del proyecto

-Aplicar buenas prácticas de organización en Python.

-Desarrollar una aplicación de escritorio funcional.

-Implementar persistencia de datos con SQLite.

-Construir un proyecto sólido para portafolio profesional.

---

## 🛠️ Estado del proyecto

🚧 En desarrollo activo.

Mejoras planificadas

 -📈 Estadísticas y gráficas

 -🔐 Sistema de autenticación y roles de usuario
 
 ---

 👤 Autor

Cristian
GitHub: https://github.com/Cristian-ch-a
