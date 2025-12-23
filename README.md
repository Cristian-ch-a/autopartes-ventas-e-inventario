# Sistema de Ventas e Inventario para Autopartes

Sistema de escritorio desarrollado en **Python** para la gestión básica de ventas e inventario de autopartes.  
El proyecto está orientado al aprendizaje práctico y a la aplicación de buenas prácticas en desarrollo de software.

---

## 📌 Características principales

- Gestión de productos (altas, bajas y modificaciones)
- Control de inventario
- Registro de ventas
- Interfaz gráfica desarrollada con **PyQt5**
- Base de datos local usando **SQLite**

---

## 🧰 Tecnologías utilizadas

- Python 3
- PyQt5
- SQLite

---

## 📁 Estructura del proyecto

autopartes-ventas-e-inventario/
│
├── assets/ # Recursos gráficos
├── controllers/ # Lógica de control
├── models/ # Modelos de datos
├── gui/ # Interfaz gráfica
├── database/ # Scripts y configuración de base de datos
├── utils/ # Utilidades generales
│
├── main.py # Punto de entrada del sistema
├── reset_db.py # Script para reiniciar la base de datos
├── README.md
└── .gitignore

yaml
Copiar código

---

## 🗄️ Base de datos

Este proyecto utiliza **SQLite** como base de datos local.

⚠️ El archivo de base de datos (`.db`) **no se incluye** en el repositorio por seguridad y buenas prácticas.

Para crear o reiniciar la base de datos, utiliza el script:

```bash
python reset_db.py
Esto generará una base de datos limpia para pruebas.

▶️ Cómo ejecutar el proyecto
1️⃣ Clonar el repositorio
bash
Copiar código
git clone https://github.com/Cristian-ch-a/autopartes-ventas-e-inventario.git
cd autopartes-ventas-e-inventario
2️⃣ Crear y activar entorno virtual
bash
Copiar código
python -m venv venv
Windows (PowerShell):

bash
Copiar código
.\venv\Scripts\Activate.ps1
3️⃣ Instalar dependencias
bash
Copiar código
pip install -r requirements.txt
pip install PyQt5
4️⃣ Ejecutar la aplicación
bash
Copiar código
python main.py
🎯 Objetivo del proyecto
Este proyecto tiene como finalidad:

Practicar programación en Python

Aplicar arquitectura básica por módulos

Trabajar con interfaces gráficas y bases de datos

Construir un portafolio de proyectos reales

📌 Estado del proyecto
🛠️ En desarrollo / aprendizaje continuo.

👤 Autor
Cristian
GitHub: https://github.com/Cristian-ch-a
