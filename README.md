# Sistema de Gestión HelpDesk 🚀

Un sistema web completo e intuitivo para la gestión de solicitudes, problemas y preguntas (tickets) diseñado para optimizar el flujo de soporte técnico y la interacción entre clientes y empleados.

---

## 🌟 Características Principales

* **Autenticación Segura**: Sistema de Login y Registro con contraseñas encriptadas (Bcrypt).
* **Gestión de Roles**: Accesos granulares diferenciados para Administradores, Agentes y Clientes.
* **Dashboard Interactivo**: Creación, edición, seguimiento e historial detallado de tickets.
* **Búsqueda Avanzada**: Búsqueda asíncrona en tiempo real sin recargar la página.
* **Papelera de Reciclaje (Soft Delete)**: Mecanismo de seguridad para evitar eliminación permanente accidental por parte de usuarios, exclusivo de administradores.
* **Reportes Analíticos**: Gráficas dinámicas de estado, prioridad y rendimiento de agentes generadas con *ApexCharts*.
* **Notificaciones por Correo Automáticas**: Reportes diarios y resúmenes enviados automáticamente por correo electrónico (SMTP + APScheduler) a los administradores.
* **Diseño Premium**: Interfaz moderna, minimalista y responsiva desarrollada con Bootstrap 5, colores personalizados e iconografía (FontAwesome).

---

## 🛠️ Tecnologías Utilizadas

* **Backend:** Python 3.11, Flask, APScheduler
* **Base de Datos:** MySQL (mysql-connector-python)
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla), Bootstrap 5
* **Librerías Adicionales:** 
  * `Flask-Bcrypt` (Seguridad de contraseñas)
  * `python-dotenv` (Gestión de credenciales)
  * `ApexCharts` (Reportes gráficos interactivos)
  * `SweetAlert2` (Alertas y modales estéticos)

---

## ⚙️ Instalación y Configuración Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/HzMarc/Help_Desk.git
cd Help_Desk
```

### 2. Configurar el Entorno Virtual (Opcional pero recomendado)
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos MySQL
1. Asegúrate de tener MySQL Server en ejecución.
2. Ejecuta el script SQL incluido en `Documentacion/Script para MySQL Workbench 8.0 CE.md` para crear la base de datos `helpdesk` y sus tablas correspondientes.

### 5. Configurar Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto basándote en la siguiente estructura:

```env
# Base de Datos
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=tu_contraseña_mysql
DB_NAME=helpdesk
DB_PORT=3308

# Configuración de Correo (Ejemplo con Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_correo@gmail.com
MAIL_PASSWORD=tu_app_password
MAIL_DEFAULT_SENDER=tu_correo@gmail.com
```

### 6. Ejecutar la Aplicación
```bash
python run.py
```
La aplicación estará disponible en: `http://127.0.0.1:5000/`

---

## 📂 Estructura del Proyecto

```text
Help_Desk/
├── app/                      # Módulo principal de la aplicación Flask
│   ├── services/             # Lógica de negocio (ej. Generador de reportes HTML)
│   ├── static/               # Archivos estáticos (CSS, JS, Imágenes)
│   ├── templates/            # Plantillas Jinja2 (HTML)
│   ├── __init__.py           # Inicialización de Flask y base de datos
│   ├── models.py             # Funciones de consulta a la base de datos
│   ├── routes.py             # Definición de rutas/controladores
│   └── utils.py              # Decoradores (auth, roles) y envío de correos
├── Documentacion/            # Manuales, requerimientos y scripts DB
├── .env                      # Variables de Entorno (Credenciales ocultas)
├── config.py                 # Configuración principal cargada desde .env
├── requirements.txt          # Dependencias de Python
└── run.py                    # Punto de entrada de la aplicación + Cron Jobs
```

---
*Desarrollado y mantenido como solución integral para soporte técnico empresarial.*
