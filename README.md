🎓 Sistema de Gestión Académica - UCS

Plataforma web académica moderna, segura y eficiente desarrollada para la Universidad de las Ciencias de la Salud (UCS), diseñada para optimizar los procesos de control de estudios, gestión de calificaciones, importación masiva de datos y generación de reportes oficiales.

🚀 Características Principales

👥 Control de Acceso por Roles (RBAC):

Administrador: Gestión total del sistema, inicialización de parámetros, control de usuarios y supervisión académica.

Docentes: Registro y actualización de notas, visualización de asignaturas y gestión de evaluaciones.

Estudiantes: Consulta de expediente académico, historial de notas y auto-registro seguro.

📊 Importador Masivo de Excel: Herramienta optimizada para procesar e insertar grandes volúmenes de calificaciones y notas directamente a la base de datos de forma automatizada.

📄 Generación de Reportes Oficiales en PDF: Creación dinámica de actas de notas y constancias académicas utilizando ReportLab, con diseño institucional y alta calidad gráfica.

✉️ Sistema de Notificaciones por Correo: Integración con Resend API para alertas institucionales y recuperación segura de contraseñas.

🔒 Seguridad y Privacidad: Encriptación robusta de contraseñas mediante hashing personalizado y separación estricta de credenciales utilizando el gestor oficial de secretos (st.secrets).

🛠️ Stack Tecnológico

Backend / Frontend: Python / Streamlit

Base de Datos: MongoDB Atlas (NoSQL Cloud Database) con PyMongo

Procesamiento de Datos: Pandas & OpenPyXL

Generación de Documentos: ReportLab

Servicio de Correo: Resend

📂 Estructura del Proyecto

univ-system-ucs/
├── .streamlit/
│   └── secrets.toml        # Credenciales locales (Ignorado por Git)
├── modules/
│   ├── security.py         # Funciones de cifrado y autenticación
│   └── ...                 # Módulos de lógica académica
├── app.py                  # Archivo principal de la aplicación Streamlit
├── database.py             # Conexión segura a MongoDB Atlas / Local
├── requirements.txt        # Dependencias del proyecto
└── README.md               # Documentación oficial


⚙️ Configuración y Despliegue Local

Sigue estos pasos para clonar y poner en marcha el proyecto en tu entorno de desarrollo:

Clona el repositorio:

git clone https://github.com/tu-usuario/univ-system-ucs.git
cd univ-system-ucs


Crea y activa un entorno virtual:

python -m venv venv
source venv/bin/activate  # En Windows usa: venv\Scripts\activate


Instala las dependencias:

pip install -r requirements.txt


Configura tus secretos locales:
Crea una carpeta llamada .streamlit en la raíz del proyecto y dentro un archivo llamado secrets.toml:

[mongo]
uri = "mongodb+srv://tu_usuario:tu_contraseña@cluster0.zofdeo6.mongodb.net/?retryWrites=true&w=majority"


Ejecuta la aplicación:

streamlit run app.py


☁️ Despliegue en Producción (Streamlit Cloud)

El sistema está preparado para integrarse de forma continua con Streamlit Cloud:

Conecta tu repositorio de GitHub (puede ser privado).

Configura las variables de entorno de producción en el panel de Streamlit Cloud bajo Settings -> Secrets:

[mongo]
uri = "tu_uri_de_conexion_mongodb_atlas"


¡Listo! La app se compilará automáticamente de forma segura.

🛡️ Protocolo de Seguridad

Este proyecto implementa buenas prácticas de seguridad:

Ninguna clave de base de datos o credencial API se encuentra expuesta en el código fuente.

El archivo de configuración local secrets.toml está protegido mediante .gitignore.

Conexión cifrada TLS con MongoDB Atlas optimizada para entornos en la nube.
