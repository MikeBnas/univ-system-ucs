import pandas as pd
import streamlit as st
from database import db_conectada, get_db


def render():
  st.title("🏛️ Gestión de Carreras, Materias y Trayectos")

  if not db_conectada:
    st.error("Sin conexión a DB.")
    return

  db = get_db()
  carreras_col = db["carreras"]
  materias_col = db["materias"]

  tab1, tab2 = st.tabs(["📚 Carreras", "📖 Materias por Carrera"])

  with tab1:
    st.subheader("Registrar Carrera")
    with st.form("form_carrera", clear_on_submit=True):
      codigo_carrera = st.text_input(
          "Código de Carrera (Clave ej: FIS-01)"
      )
      nombre_carrera = st.text_input(
          "Nombre de la Carrera (ej: Fisioterapia)"
      )
      btn_carrera = st.form_submit_button("Guardar Carrera")

      if btn_carrera and codigo_carrera and nombre_carrera:
        if carreras_col.find_one({"cod_pnf": codigo_carrera}):
          st.warning("El código de carrera ya existe.")
        else:
          carreras_col.insert_one({
              "cod_pnf": codigo_carrera,
              "nombre_pnf": nombre_carrera,
          })
          st.success(f"Carrera {nombre_carrera} registrada.")
          st.rerun()

    st.markdown("### Carreras Existentes")
    carreras_list = list(carreras_col.find({}, {"_id": 0}))
    if carreras_list:
      st.dataframe(pd.DataFrame(carreras_list), use_container_width=True)

  with tab2:
    st.subheader("Asignar Materias a Carreras y Trayectos")
    carreras_cursor = list(carreras_col.find({}, {"_id": 0}))
    nombres_carreras = (
        [c["cod_pnf"] + " - " + c["nombre_pnf"] for c in carreras_cursor]
        if carreras_cursor
        else []
    )

    if not nombres_carreras:
        st.warning("Primero debes registrar al menos una carrera.")
        return

    with st.form("form_materia", clear_on_submit=True):
      carrera_asoc = st.selectbox("Carrera Asociada", nombres_carreras)
      codigo_materia = st.text_input(
          "Código de Materia (Clave ej: ANAT-101)"
      )
      nombre_materia = st.text_input("Nombre de la Materia (ej: Anatomía I)")
      trayecto_materia = st.selectbox(
          "Trayecto",
          [
              "I",
              "II",
              "III",
              "IV",
              "V",
              "VI"
          ],
      )

      btn_materia = st.form_submit_button("Guardar Materia")

      if btn_materia and codigo_materia and nombre_materia:
        cod_carr_limpio = carrera_asoc.split(" - ")[0]
        if materias_col.find_one({"codigo_materia": codigo_materia}):
          st.warning("El código de materia ya existe.")
        else:
          materias_col.insert_one({
              "codigo_materia": codigo_materia,
              "nombre_materia": nombre_materia,
              "codigo_pnf": cod_carr_limpio,
              "trayecto": trayecto_materia,
          })
          st.success(f"Materia {nombre_materia} agregada con éxito.")
          st.rerun()

    st.markdown("### Listado de Materias Registradas")
    materias_list = list(materias_col.find({}, {"_id": 0}))
    if materias_list:
      st.dataframe(pd.DataFrame(materias_list), use_container_width=True)