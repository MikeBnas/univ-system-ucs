import streamlit as st
from database import db_conectada, get_db, inicializar_admin_por_defecto
from modules.security import hash_password
from modules.security import verificar_password

# Inicializar admin por defecto al arrancar
inicializar_admin_por_defecto()

st.set_page_config(
    page_title="Sistema de Gestión Académica", page_icon="🎓", layout="wide"
)

# Inicializar variables de sesión
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
if "username" not in st.session_state:
  st.session_state.username = ""
if "rol" not in st.session_state:
  st.session_state.rol = ""
if "cedula" not in st.session_state:
  st.session_state.cedula = ""
if "menu_activo" not in st.session_state:
  st.session_state.menu_activo = "🏠 Inicio"


def show_auth_screen():
  st.title("🎓 Sistema de Gestión Académica")
  if not db_conectada:
    st.error(
        "⚠️ No se pudo conectar a MongoDB. Asegúrate de encender el servicio"
        " local o configurar tu URI en la nube."
    )
    return

  col1, col2, col3 = st.columns([1, 2, 1])
  with col2:
    tab_login, tab_register, tab_recuperar = st.tabs([
        "🔑 Iniciar Sesión",
        "📝 Registrarse",
        "❓ Recuperar Contraseña",
    ])

    db = get_db()
    usuarios_col = db["usuarios"]

    with tab_login:
      st.markdown("### Acceso al Sistema")
      with st.form("login_form"):
        usuario_input = st.text_input("Usuario o Correo")
        password_input = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Ingresar")

        if submit:
          if usuario_input and password_input:
            user_doc = usuarios_col.find_one({
                "$or": [
                    {"usuario": usuario_input},
                    {"email": usuario_input},
                ]
            })

            from modules.security import verificar_password

            if user_doc and verificar_password(user_doc.get("password", ""), password_input):
              st.session_state.logged_in = True
              st.session_state.username = user_doc["usuario"]
              st.session_state.rol = user_doc.get("rol", "Estudiante")
              st.session_state.cedula = user_doc.get("cedula", "")
              st.session_state.menu_activo = "🏠 Inicio"
              st.success("¡Bienvenido!")
              st.rerun()
            else:
              st.error("Usuario o contraseña incorrectos.")
          else:
            st.error("Por favor, complete todos los campos.")

    with tab_register:
      st.markdown("### Solicitud de Cuenta Nueva")
      with st.form("register_form"):
        st.markdown(
            "*(Nota: Todo nuevo registro se crea con rol de **Estudiante** y requiere cédula obligatoria)*"
        )
        nuevo_usuario = st.text_input("Nombre de Usuario")
        
        nueva_cedula_input = st.text_input(
            "Cédula de Identidad", 
            placeholder="Ej: 13234321",
            help="Ingrese su número de cédula sin puntos ni espacios."
        )
        
        nuevo_email_input = st.text_input(
            "Correo Electrónico", 
            placeholder="Ej: usuario@correo.com",
            help="Ingrese su correo electrónico sin espacios en blanco."
        )
        
        nuevo_pass = st.text_input("Contraseña", type="password")
        submit_reg = st.form_submit_button("Registrarse")

        if submit_reg:
          nueva_cedula = "".join(c for c in nueva_cedula_input if c.isdigit()).strip()
          nuevo_email = nuevo_email_input.strip()

          if nuevo_usuario and nueva_cedula and nuevo_email and nuevo_pass:
            if " " in nuevo_email:
              st.error("El correo electrónico no puede contener espacios en blanco.")

            if usuarios_col.find_one({"usuario": nuevo_usuario}):
              st.warning("El nombre de usuario ya está en uso.")
            elif usuarios_col.find_one({"cedula": nueva_cedula}):
              st.warning("La cédula ya se encuentra registrada.")
            else:
              usuarios_col.insert_one({
                  "usuario": nuevo_usuario,
                  "cedula": nueva_cedula,
                  "email": nuevo_email,
                  "password": hash_password(nuevo_pass),
                  "rol": "Estudiante",
              })
              st.success(
                  "¡Cuenta creada con éxito! Ya puedes iniciar sesión."
              )
          else:
            st.error("Llena todos los campos obligatorios correctamente.")

    with tab_recuperar:
      from modules import recuperar
      recuperar.render()


def show_dashboard():
  st.sidebar.title(f"👤 {st.session_state.username}")
  st.sidebar.caption(f"Rol: **{st.session_state.rol}**")
  st.sidebar.markdown("---")

  # Definir menú dinámico basado en el rol
  opciones_menu = ["🏠 Inicio", "📊 Calificaciones y Notas"]

  if st.session_state.rol == "Administrador":
    opciones_menu.extend([
        "👨‍🎓 Estudiantes",
        "👥 Gestión de Usuarios",
        "🏛️ Carreras y Materias",
        "📄 Actas de Notas",
        "📨 Solicitudes",
        "📂 Importar Excel"        
    ])
  elif st.session_state.rol == "Docente":
    opciones_menu.append("📄 Actas de Notas")
    opciones_menu.append("❓ Ayuda y Soporte")
  elif st.session_state.rol == "Estudiante":
    opciones_menu = ["🏠 Inicio", "📊 Calificaciones y Notas", "❓ Ayuda y Soporte"]

  # Asegurar que el menú activo esté dentro de las opciones permitidas
  if st.session_state.menu_activo not in opciones_menu:
    st.session_state.menu_activo = "🏠 Inicio"

  # Radio de navegación vinculado directamente a st.session_state.menu_activo via key
  st.sidebar.radio("Navegación", opciones_menu, key="menu_activo")

  st.sidebar.markdown("---")
  if st.sidebar.button("Cerrar Sesión", type="primary"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.rol = ""
    st.session_state.cedula = ""
    st.session_state.menu_activo = "🏠 Inicio"
    if "mostrar_modulo_solicitud" in st.session_state:
      del st.session_state.mostrar_modulo_solicitud
    st.rerun()

  # Enrutador basado en st.session_state.menu_activo
  current_view = st.session_state.menu_activo

  if current_view == "🏠 Inicio":
    if st.session_state.rol == "Estudiante":
      st.title("👤 Mi Perfil de Estudiante")
      db = get_db()
      cedula_est = st.session_state.get("cedula", "")

      c_str = str(cedula_est).strip()
      c_int = int(c_str) if c_str.isdigit() else None
      q_est = {"$or": [{"cedula": c_str}]}
      if c_int is not None:
        q_est["$or"].append({"cedula": c_int})

      est_doc = db["estudiantes"].find_one(q_est)

      if est_doc:
        st.markdown(f"### Bienvenido, {est_doc.get('nombres', '')} {est_doc.get('apellidos', '')}")
        st.info("Datos personales registrados en el sistema académico:")

        col1, col2 = st.columns(2)
        with col1:
          st.write(f"**Cédula:** {est_doc.get('cedula', '')}")
          st.write(f"**Nombres:** {est_doc.get('nombres', '')}")
          st.write(f"**Apellidos:** {est_doc.get('apellidos', '')}")
        with col2:
          st.write(f"**Correo:** {est_doc.get('email', est_doc.get('correo', 'N/A'))}")
          st.write(f"**Teléfono:** {est_doc.get('telefono', 'N/A')}")
          st.write(f"**Dirección:** {est_doc.get('direccion', 'N/A')}")

        st.markdown("---")
        if "mostrar_modulo_solicitud" not in st.session_state:
          st.session_state.mostrar_modulo_solicitud = False

        if not st.session_state.mostrar_modulo_solicitud:
          if st.button("📄 Solicitar Documento", type="primary"):
            st.session_state.mostrar_modulo_solicitud = True
            st.rerun()
        else:
          if st.button("⬅️ Volver a mi Perfil"):
            st.session_state.mostrar_modulo_solicitud = False
            st.rerun()

          from modules import solicitudes
          solicitudes.render_estudiante(cedula_est, f"{est_doc.get('nombres', '')} {est_doc.get('apellidos', '')}")
      else:
        st.warning("⚠️ No se encontró un registro en la tabla de estudiantes asociado a tu cédula registrada.")
        st.write(f"Cédula registrada en tu cuenta: **{cedula_est}**")
        st.info("Por favor contacta al administrador si tus datos no aparecen sincronizados.")
    
    elif st.session_state.rol == "Docente":
      st.title("👤 Perfil de Docente y Accesos Directos")
      st.write(f"¡Hola, **{st.session_state.username}**! Bienvenido al panel principal.")
      
      st.markdown("---")
      st.markdown("### 🚀 Accesos Directos")
      st.caption("Selecciona una tarjeta para abrir rápidamente los módulos principales:")

      col_d1, col_d2, col_d3 = st.columns(3)
      with col_d1:
        st.info("📊 **Calificaciones y Notas**\n\nCarga y gestiona las notas de tus estudiantes.")
        if st.button("Abrir Módulo de Notas", type="primary", use_container_width=True):
          st.session_state.menu_activo = "📊 Calificaciones y Notas"
          st.rerun()
      with col_d2:
        st.info("📄 **Actas de Notas**\n\nGenera y descarga las actas oficiales en PDF.")
        if st.button("Abrir Módulo de Actas", type="primary", use_container_width=True):
          st.session_state.menu_activo = "📄 Actas de Notas"
          st.rerun()
      with col_d3:
        st.info("❓ **Ayuda y Soporte**\n\nConsulta guías o contacta al administrador.")
        if st.button("Abrir Ayuda y Soporte", type="primary", use_container_width=True):
          st.session_state.menu_activo = "❓ Ayuda y Soporte"
          st.rerun()
    else:
      st.title("Panel de Control Académico")
      st.write(f"Hola **{st.session_state.username}**, panel activo.")

  elif current_view == "👨‍🎓 Estudiantes":
    from modules import estudiantes
    estudiantes.render()

  elif current_view == "🏛️ Carreras y Materias":
    from modules import carreras
    carreras.render()

  elif current_view == "📊 Calificaciones y Notas":
    from modules import notas
    notas.render()

  elif current_view == "👥 Gestión de Usuarios":
    from modules import usuarios
    usuarios.render()

  elif current_view == "📅 Años Académicos":
    st.title("Configuración de Años Académicos")
    st.info("Administración de periodos lectivos...")

  elif current_view == "📄 Actas de Notas":
    from modules import actas
    actas.render()
    
  elif current_view == "📂 Importar Excel":
    from modules import importador_excel
    importador_excel.render()

  elif current_view == "📨 Solicitudes":
    from modules import solicitudes
    solicitudes.render_admin()

  elif current_view == "❓ Ayuda y Soporte":
     from modules import ayuda_module
     ayuda_module.render()

if not st.session_state.logged_in:
  show_auth_screen()
else:
  show_dashboard()
