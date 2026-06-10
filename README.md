# Help_Desk
Es una aplicación para gestionar solicitudes, problemas o preguntas de clientes o empleados.

# Estructura del proyecto
Help_Desk/
├── app/                   # Módulo principal de la aplicación
│   ├── services/          # Lógica de negocio y servicios externos
│   │   └── .gitkeep
│   ├── static/            # Archivos estáticos (CSS, JS, Imágenes)
│   │   ├── css/
│   │   │   └── .gitkeep
│   │   ├── img/
│   │   │   └── .gitkeep
│   │   └── js/
│   │       └── .gitkeep
│   ├── templates/         # Plantillas HTML
│   │   ├── login/
│   │   │   └── login.html
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   └── index.html
│   ├── __init__.py        # Inicialización de la aplicación Flask/paquete
│   ├── forms.py           # Definición de formularios (ej. WTForms)
│   ├── models.py          # Modelos de bases de datos
│   ├── routes.py          # Definición de rutas y controladores
│   └── utils.py           # Funciones de utilidad y helpers
├── config.py              # Configuraciones de entorno y variables globales
├── README.md              # Documentación del proyecto
├── requirements.txt       # Dependencias del proyecto
└── run.py                 # Script de entrada para ejecutar la aplicación
