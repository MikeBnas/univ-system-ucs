from datetime import datetime
import streamlit as st
from database import get_db


def registrar_log(db, usuario, accion, detalles):
  """Registra un log de auditoría en MongoDB para cada acción crítica."""
  logs_col = db["logs_auditoria"]
  logs_col.insert_one({
      "usuario": usuario,
      "accion": accion,
      "detalles": detalles,
      "fecha": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
  })


def render():
  st.subheader("❓ Módulo de Ayuda y Soporte Universitario")

  rol_actual = st.session_state.get("rol", "Estudiante")
  username = st.session_state.get("username", "Usuario")
  cedula = st.session_state.get("cedula", "")

  db = get_db()
  tickets_col = db["tickets_soporte"]

  # Pestañas principales de Ayuda y Contacto
  tab_guia, tab_contacto = st.tabs(["📖 Guía de Uso del Sistema", "💬 Contactar al Administrador (Tickets)"])

  with tab_guia:
    if rol_actual == "Estudiante":
      st.markdown("### 🎓 Guía para Estudiantes")
      st.markdown("""
      Bienvenido al sistema de gestión universitaria. Como estudiante, tienes acceso a las siguientes funciones principales:
      
      1. **Visualización de Notas y Recorrido Académico:**
         - Al iniciar sesión con tu cuenta vinculada a tu cédula, verás tu perfil con tus datos personales.
         - Puedes consultar tus calificaciones obtenidas por asignatura, trayecto y año en el apartado correspondiente del sistema.
      
      2. **Solicitud de Documentos Académicos:**
         - Desde tu perfil de estudiante, puedes hacer clic en el botón **"Solicitar Documento"**.
         - Allí podrás seleccionar el tipo de documento que requieres (ej. **Récord de Notas** o **Constancia de Estudios**).
         - Podrás escribir observaciones adicionales y enviar la solicitud, la cual generará un ticket con fecha de creación y estado actualizado (Pendiente / Respondido).
      """)
    elif rol_actual == "Docente":
      st.markdown("### 👨‍🏫 Guía para Docentes")
      st.markdown("""
      Bienvenido al panel docente del sistema de gestión universitaria. Aquí tienes las directrices para tus funciones:
      
      1. **Carga de Notas para los Estudiantes:**
         - Accede al módulo de **Calificaciones y Notas**.
         - Selecciona la unidad curricular o materia correspondiente, el tipo de evaluación (Ordinario, Reparación I, Reparación II) y el listado de estudiantes activos aparecerá para registrar o actualizar las notas numéricas de forma individual o masiva.
      
      2. **Creación y Descarga de Actas de Notas:**
         - Dirígete al módulo **Actas de Notas**.
         - Selecciona el año académico, la carrera (PNF), el trayecto, el tramo y la ASIC si aplica.
         - El sistema cargará automáticamente los estudiantes inscritos activos en orden alfabético estricto.
         - Podrás verificar el listado y hacer clic en **"Generar y Descargar Acta Oficial en PDF"** para obtener el documento con la estructura institucional exacta lista para imprimir y firmar.
      """)
    else:  # Administrador o general
      st.markdown("### 👑 Guía General del Sistema (Administrador)")
      st.markdown("""
      Como administrador, posees control total sobre la plataforma:
      - Gestión de usuarios y asignación de roles.
      - Administración de carreras, materias y años académicos.
      - Revisión y aprobación de solicitudes de documentos académicos y tickets de soporte técnico.
      """)

  with tab_contacto:
    st.markdown("### 💬 Centro de Soporte y Contacto con el Administrador")
    st.info("¿Tienes dudas, problemas técnicos o requieres asistencia personalizada? Envía un ticket y el equipo administrativo te dará respuesta por este medio.")

    # Formulario para enviar ticket de soporte
    with st.form("form_ticket_soporte", clear_on_submit=True):
      st.markdown("#### Enviar Nueva Solicitud o Mensaje al Administrador")
      asunto = st.text_input("Asunto de la Solicitud", placeholder="Ej. Error al visualizar mis notas de Trayecto II...")
      descripcion = st.text_area("Descripción Detallada", placeholder="Describe aquí tu consulta o inconveniente en texto...")
      btn_enviar_ticket = st.form_submit_button("📤 Enviar Ticket de Soporte", type="primary")

      if btn_enviar_ticket:
        if asunto and descripcion:
          nuevo_ticket = {
              "usuario": username,
              "cedula": str(cedula),
              "rol": rol_actual,
              "asunto": asunto,
              "descripcion": descripcion,
              "fecha": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
              "estado": "Pendiente",
              "respuesta": ""
          }
          tickets_col.insert_one(nuevo_ticket)
          registrar_log(db, username, "CREAR_TICKET_SOPORTE", f"Creó ticket de soporte: {asunto}")
          st.success("¡Ticket enviado con éxito! El administrador lo revisará a la brevedad.")
          st.rerun()
        else:
          st.error("Por favor completa el asunto y la descripción de tu solicitud.")

    st.markdown("---")
    st.markdown("#### 🎫 Historial de Mis Tickets y Respuestas")

    # Mostrar tickets según el usuario (Si es Admin ve todos, si es usuario normal ve los suyos)
    if rol_actual == "Administrador":
      st.markdown("*(Vista de Administrador: Gestión completa de tickets)*")
      filtro_estado = st.selectbox("Filtrar tickets por estado", ["Todos", "Pendiente", "Respondido"])
      query_t = {} if filtro_estado == "Todos" else {"estado": filtro_estado}
      mis_tickets = list(tickets_col.find(query_t).sort("fecha", -1))
    else:
      c_str = str(cedula).strip()
      mis_tickets = list(tickets_col.find({"$or": [{"usuario": username}, {"cedula": c_str}]}).sort("fecha", -1))

    if mis_tickets:
      for t in mis_tickets:
        t_id = t["_id"]
        estado_t = t.get("estado", "Pendiente")
        color_bg = "#d4edda" if estado_t == "Respondido" else "#fff3cd"
        icono_estado = "✅ Respondido" if estado_t == "Respondido" else "⏳ Pendiente"

        with st.expander(f"Ticket #{str(t_id)[-6:]} - {t.get('asunto')} [{icono_estado}] ({t.get('fecha')})"):
          st.write(f"**Enviado por:** {t.get('usuario')} (Rol: {t.get('rol')}, C.I: {t.get('cedula', 'N/A')})")
          st.write(f"**Asunto:** {t.get('asunto')}")
          st.write(f"**Descripción:** {t.get('descripcion')}")
          st.write(f"**Estado:** {estado_t}")
          
          if t.get('respuesta'):
            st.success(f"**Respuesta del Administrador:** {t.get('respuesta')}")

          # Si es Administrador, permitir responder o cerrar el ticket
          if rol_actual == "Administrador":
            st.markdown("---")
            with st.form(f"form_resp_ticket_{t_id}"):
              texto_respuesta = st.text_area("Escribir Respuesta al Usuario", value=t.get('respuesta', ''))
              col_r1, col_r2 = st.columns(2)
              with col_r1:
                btn_responder = st.form_submit_button("💬 Enviar Respuesta y Marcar Respondido", type="primary")
              with col_r2:
                btn_eliminar = st.form_submit_button("🗑️ Eliminar Ticket", type="secondary")

              if btn_responder:
                tickets_col.update_one(
                    {"_id": t_id},
                    {"$set": {"estado": "Respondido", "respuesta": texto_respuesta}}
                )
                registrar_log(db, username, "RESPONDER_TICKET_SOPORTE", f"Respondió ticket #{str(t_id)[-6:]}")
                st.success("¡Respuesta enviada y ticket actualizado correctamente!")
                st.rerun()

              if btn_eliminar:
                tickets_col.delete_one({"_id": t_id})
                registrar_log(db, username, "ELIMINAR_TICKET_SOPORTE", f"Eliminó ticket #{str(t_id)[-6:]}")
                st.success("¡Ticket eliminado del sistema!")
                st.rerun()
    else:
      st.info("No hay tickets de soporte registrados.")