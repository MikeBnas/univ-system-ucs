from datetime import datetime
import pandas as pd
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


def render_estudiante(cedula, nombre_estudiante):
  st.markdown("### 📨 Solicitud de Documentos Académicos")
  st.info("Aquí puedes solicitar un **Récord de Notas** o una **Constancia de Estudios** al departamento de Control de Estudios.")

  db = get_db()
  solicitudes_col = db["solicitudes"]

  with st.form("form_nueva_solicitud"):
    tipo_doc = st.selectbox(
        "Tipo de Documento a Solicitar",
        ["Récord de Notas", "Constancia de Estudios"]
    )
    observacion = st.text_area("Observación o Motivo (Opcional)", placeholder="Ej. Requiero el documento para trámites personales...")
    btn_enviar = st.form_submit_button("📤 Enviar Solicitud", type="primary")

    if btn_enviar:
      ticket = {
          "cedula": str(cedula),
          "nombre": nombre_estudiante,
          "tipo_documento": tipo_doc,
          "observacion": observacion,
          "fecha": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
          "estado": "Pendiente",
          "en_listado": False
      }
      solicitudes_col.insert_one(ticket)
      registrar_log(db, nombre_estudiante, "CREAR_SOLICITUD", f"Solicitó {tipo_doc} (Cédula: {cedula})")
      st.success("¡Solicitud enviada con éxito! Se ha generado tu ticket.")
      st.rerun()

  st.markdown("---")
  st.markdown("#### 🎫 Mis Solicitudes y Estado de Tickets")

  c_str = str(cedula)
  c_int = int(c_str) if c_str.isdigit() else None
  q = {"$or": [{"cedula": c_str}]}
  if c_int is not None:
    q["$or"].append({"cedula": c_int})

  mis_solicitudes = list(solicitudes_col.find(q, {"_id": 0}).sort("fecha", -1))

  if mis_solicitudes:
    for s in mis_solicitudes:
      estado = s.get("estado", "Pendiente")
      
      if estado == "Respondido":
        color_bg = "#d4edda"
        mensaje_estado = "✅ <b>¡Respondido!</b> Tu solicitud ha sido procesada. <b>Por favor acude a la sede administrativa a retirar tu documento.</b>"
      else:
        color_bg = "#fff3cd"
        mensaje_estado = "⏳ <b>Pendiente:</b> Tu solicitud está siendo procesada por Control de Estudios."

      with st.container():
        st.markdown(
            f"""
            <div style="background-color: {color_bg}; padding: 12px; border-radius: 6px; margin-bottom: 10px; border: 1px solid #ccc; color: #333;">
                <b>Documento:</b> {s.get('tipo_documento')}<br>
                <b>Fecha de Solicitud:</b> {s.get('fecha')}<br>
                <b>Estado:</b> {mensaje_estado}<br>
                <small>Observación: {s.get('observacion', 'Ninguna')}</small>
            </div>
            """,
            unsafe_allow_html=True
        )
  else:
    st.info("No tienes solicitudes registradas actualmente.")


def render_admin():
  st.subheader("📨 Gestión de Solicitudes de Estudiantes (Administrador)")

  db = get_db()
  solicitudes_col = db["solicitudes"]
  listas_col = db["listas_generacion"] # Colección para almacenar los estudiantes agregados a los listados
  usuario_actual = st.session_state.get("username", "Admin")

  # Pestañas para separar la gestión de tickets y los listados de generación
  tab_gestion, tab_listados = st.tabs(["🎫 Gestión de Tickets", "📑 Listados para Generar Documentos"])

  with tab_gestion:
    filtro_estado = st.selectbox("Filtrar por estado", ["Todas", "Pendiente", "Respondido"])

    query = {} if filtro_estado == "Todas" else {"estado": filtro_estado}
    solicitudes_list = list(solicitudes_col.find(query).sort("fecha", -1))

    if solicitudes_list:
      st.markdown(f"Total de solicitudes encontradas: **{len(solicitudes_list)}**")
      
      for s in solicitudes_list:
        s_id = s["_id"]
        cedula = s.get("cedula")
        nombre = s.get("nombre")
        tipo = s.get("tipo_documento")
        fecha = s.get("fecha")
        estado = s.get("estado", "Pendiente")
        obs = s.get("observacion", "Ninguna")
        en_listado = s.get("en_listado", False)

        icono = "⏳ Pendiente" if estado == "Pendiente" else "✅ Respondido"

        with st.expander(f"Ticket #{str(s_id)[-6:]} - {nombre} (C.I: {cedula}) - {tipo} [{icono}]"):
          st.write(f"**Fecha:** {fecha}")
          st.write(f"**Tipo de Documento:** {tipo}")
          st.write(f"**Estudiante:** {nombre} (Cédula: {cedula})")
          st.write(f"**Observación:** {obs}")
          st.write(f"**Estado Actual:** {estado}")

          col_a, col_b = st.columns(2)
          with col_a:
            # Botón para agregar a listado de generación si no ha sido agregado
            if not en_listado:
              if st.button("➕ Agregar a listado para generar", key=f"add_{s_id}"):
                listas_col.insert_one({
                    "ticket_id": s_id,
                    "cedula": cedula,
                    "nombre": nombre,
                    "tipo_documento": tipo,
                    "fecha_agregado": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                })
                solicitudes_col.update_one({"_id": s_id}, {"$set": {"en_listado": True}})
                registrar_log(db, usuario_actual, "AGREGAR_LISTADO", f"Agregó cédula {cedula} al listado de {tipo}")
                st.success(f"¡Estudiante agregado al listado de {tipo}!")
                st.rerun()
            else:
              st.info("📌 Ya se encuentra agregado en el listado de generación.")

          with col_b:
            if estado == "Pendiente":
              if st.button("✅ Marcar como Respondido", key=f"resp_{s_id}"):
                solicitudes_col.update_one({"_id": s_id}, {"$set": {"estado": "Respondido"}})
                registrar_log(db, usuario_actual, "RESPONDER_SOLICITUD", f"Marcó como respondido ticket de cédula {cedula}")
                st.success("¡Solicitud marcada como respondida y notificada al estudiante!")
                st.rerun()
            else:
              if st.button("⏳ Marcar como Pendiente", key=f"pend_{s_id}"):
                solicitudes_col.update_one({"_id": s_id}, {"$set": {"estado": "Pendiente"}})
                registrar_log(db, usuario_actual, "CAMBIAR_ESTADO_SOLICITUD", f"Marcó como pendiente ticket de cédula {cedula}")
                st.rerun()

          if st.button("🗑️ Eliminar Solicitud", key=f"del_{s_id}"):
            # Si estaba en listado, lo removemos también
            listas_col.delete_one({"ticket_id": s_id})
            solicitudes_col.delete_one({"_id": s_id})
            registrar_log(db, usuario_actual, "ELIMINAR_SOLICITUD", f"Eliminó ticket de cédula {cedula}")
            st.success("¡Solicitud eliminada!")
            st.rerun()
    else:
      st.info("No hay solicitudes registradas con el filtro seleccionado.")

  with tab_listados:
    st.markdown("#### 📑 Listados Pendientes para Generación de Documentos")

    # Listado de Notas (Récord de Notas)
    st.markdown("##### 📊 Listado para Generar Notas")
    lista_notas = list(listas_col.find({"tipo_documento": "Récord de Notas"}))
    if lista_notas:
      df_notas = pd.DataFrame(lista_notas)[["cedula", "nombre", "fecha_agregado"]]
      df_notas.columns = ["Cédula", "Estudiante", "Fecha Agregado"]
      st.dataframe(df_notas, use_container_width=True, hide_index=True)

      if st.button("🗑️ Vaciar Listado de Notas", type="primary", key="vaciar_notas"):
        listas_col.delete_many({"tipo_documento": "Récord de Notas"})
        registrar_log(db, usuario_actual, "VACIAR_LISTADO", "Vació el listado de generación de notas")
        st.success("¡Listado de notas vaciado correctamente!")
        st.rerun()
    else:
      st.info("No hay estudiantes en el listado de generación de notas.")

    st.markdown("---")

    # Listado de Constancias (Constancia de Estudios)
    st.markdown("##### 📜 Listado para Generar Constancias")
    lista_constancias = list(listas_col.find({"tipo_documento": "Constancia de Estudios"}))
    if lista_constancias:
      df_const = pd.DataFrame(lista_constancias)[["cedula", "nombre", "fecha_agregado"]]
      df_const.columns = ["Cédula", "Estudiante", "Fecha Agregado"]
      st.dataframe(df_const, use_container_width=True, hide_index=True)

      if st.button("🗑️ Vaciar Listado de Constancias", type="primary", key="vaciar_const"):
        listas_col.delete_many({"tipo_documento": "Constancia de Estudios"})
        registrar_log(db, usuario_actual, "VACIAR_LISTADO", "Vació el listado de generación de constancias")
        st.success("¡Listado de constancias vaciado correctamente!")
        st.rerun()
    else:
      st.info("No hay estudiantes en el listado de generación de constancias.")