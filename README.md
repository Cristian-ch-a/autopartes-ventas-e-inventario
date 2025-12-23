# 🏎️ Sistema de Ventas e Inventario - Autopartes

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-GUI-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

Una solución de escritorio robusta y ligera diseñada para la gestión eficiente de autopartes. Este proyecto combina una arquitectura modular con una interfaz intuitiva, ideal para entornos de aprendizaje y aplicaciones comerciales a pequeña escala.

---

## ✨ Características Principales

* **📦 Gestión de Productos:** CRUD completo (Altas, Bajas, Modificaciones y Consultas).
* **📉 Control de Stock:** Monitoreo en tiempo real de niveles de inventario.
* **💰 Registro de Ventas:** Interfaz fluida para procesar transacciones rápidamente.
* **🖥️ Interfaz Moderna:** Desarrollada con **PyQt5** para una experiencia de usuario nativa y ágil.
* **💾 Almacenamiento Local:** Base de datos **SQLite** integrada, sin necesidad de configuraciones complejas de servidor.

---

## 🛠️ Stack Tecnológico

| Tecnología | Propósito |
| :--- | :--- |
| **Python 3** | Lenguaje núcleo del sistema |
| **PyQt5** | Framework para la interfaz gráfica (GUI) |
| **SQLite** | Motor de base de datos relacional ligero |

---

## 📂 Arquitectura del Proyecto

El sistema sigue una estructura organizada por módulos para facilitar el mantenimiento y la escalabilidad:

```bash
autopartes-ventas-e-inventario/
├── 🎨 assets/         # Recursos visuales (iconos, imágenes)
├── ⚙️ controllers/    # Lógica de negocio y manejo de eventos
├── 📊 models/         # Definición de tablas y consultas (Data Access)
├── 🖼️ gui/            # Archivos .ui y vistas de PyQt5
├── 🗄️ database/       # Scripts SQL y configuración inicial
├── 🛠️ utils/          # Funciones auxiliares y herramientas
│
├── 🚀 main.py         # Punto de entrada principal del sistema
├── 🔄 reset_db.py     # Script para inicializar/limpiar la base de datos
└── 📄 README.md        # Documentación del proyecto

---



## 🚀 Guía de Instalación

Sigue estos pasos detallados para configurar tu entorno de desarrollo local de forma rápida y segura.

### 1️⃣ Clonar el Repositorio
Primero, descarga el proyecto a tu máquina local:
```bash
git clone [https://github.com/Cristian-ch-a/autopartes-ventas-e-inventario.git](https://github.com/Cristian-ch-a/autopartes-ventas-e-inventario.git)
cd autopartes-ventas-e-inventario
