import pandas as pd
import streamlit as st
from database import db_conectada, get_db


def render():
  st.title("👥 Gestión de Usuarios y Roles")

  if not db_conectada:
    st.error("No hay conexión con MongoDB.")
    return

  db = get_db()
  coleccion = db["usuarios"]

  tab1, tab2 = st.tabs(["📋 Listado de Usuarios", "➕ Crear Nuevo Usuario"])

  with tab1:
    st.subheader("Usuarios del Sistema")
    usuarios_cursor = list(coleccion.find({}, {"_id": 0, "password": 0}))

    if usuarios_cursor:
      df = pd.DataFrame(usuarios_cursor)
      st.dataframe(df, use_container_width=True)

      # Sección para cambiar roles
      st.markdown("### Modificar Rol de Usuario")
      col1, col2 = st.columns(2)
      with col1:
        user_select = st.selectbox(
            "Seleccionar Usuario", [u["usuario"] for u in usuarios_cursor]
        )
      with col2:
        nuevo_rol = st.selectbox(
            "Nuevo Rol", ["Administrador", "Docente"]
        )

      if st.button("Actualizar Rol"):
        coleccion.update_one(
            {"usuario": user_select}, {"$set": {"rol": nuevo_rol}}
        )
        st.success(
            f"Rol del usuario '{user_select}' actualizado a '{nuevo_rol}' con"
            " éxito."
        )
        st.rerun()
    else:
      st.info("No hay usuarios registrados.")

  with tab2:
    st.subheader("Registrar Nuevo Usuario (Admin)")
    with st.form("form_nuevo_usuario", clear_on_submit=True):
      u_name = st.text_input("Nombre de Usuario")
      u_email = st.text_input("Correo Electrónico")
      u_pass = st.text_input("Contraseña Temporal", type="password")
      u_rol = st.selectbox("Rol Asignado", ["Docente", "Administrador"])

      submit_u = st.form_submit_button("Crear Usuario")

      if submit_u:
        if u_name and u_pass:
          if coleccion.find_one({"usuario": u_name}):
            st.warning("El usuario ya existe.")
          else:
            coleccion.insert_one({
                "usuario": u_name,
                "email": u_email,
                "password": u_pass,
                "rol": u_rol,
            })
            st.success(f"Usuario {u_name} creado exitosamente como {u_rol}.")
            st.rerun()
        else:
          st.error("Completa al menos el usuario y la contraseña.")