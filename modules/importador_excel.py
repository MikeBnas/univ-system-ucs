from datetime import datetime
import pandas as pd
import streamlit as st
from database import db_conectada, get_db


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
  st.title("📂 Importación Masiva de Datos (Excel)")

  if not db_conectada:
    st.error(
        "⚠️ No hay conexión con MongoDB. Asegúrate de que el servicio esté"
        " activo."
    )
    return

  db = get_db()
  usuario_actual = st.session_state.get("username", "Admin")

  st.markdown("""
    Sube tus archivos en formato **Excel (.xlsx)** divididos por categoría. El sistema procesará la información y la vinculará automáticamente respetando las claves principales.
    """)

  # Selector de la colección a la que deseas cargarle datos
  tipo_carga = st.selectbox(
      "Selecciona qué tipo de datos vas a importar:",
      [
          "Carreras",
          "Materias",
          "Estudiantes",
          "Inscripciones (Historial)",
          "Calificaciones y Notas",
      ],
  )

  archivo_subido = st.file_uploader(
      f"Cargar archivo Excel para: {tipo_carga}", type=["xlsx", "xls"]
  )

  if archivo_subido is not None:
    try:
      # Leer el archivo excel con pandas
      df = pd.read_excel(archivo_subido)
      st.markdown("### Vista previa de los datos a cargar:")
      st.dataframe(df.head(), use_container_width=True)

      if st.button(
          f"Confirmar e Importar {tipo_carga}", type="primary"
      ):
        registros = df.to_dict(orient="records")
        coleccion = None
        clave_unica = None

        # Configurar colección y clave primaria según la selección
        if tipo_carga == "Carreras":
          coleccion = db["carreras"]
          clave_unica = "cod_pnf"
        elif tipo_carga == "Materias":
          coleccion = db["materias"]
          clave_unica = "cod_materia"
        elif tipo_carga == "Estudiantes":
          coleccion = db["estudiantes"]
          clave_unica = "cedula"
        elif tipo_carga == "Inscripciones (Historial)":
          coleccion = db["inscripciones_historial"]
          clave_unica = None
        elif tipo_carga == "Calificaciones y Notas":
          coleccion = db["notas"]
          clave_unica = None  # Las notas se manejan por combinación única de cédula, materia y tipo de evaluación

        if coleccion is not None:
          contador_nuevos = 0
          contador_actualizados = 0

          for item in registros:
            # Limpiar valores nulos de pandas (NaN)
            item_limpio = {
                k: v
                for k, v in item.items()
                if pd.notna(v)
            }

            if tipo_carga == "Calificaciones y Notas":
              # Estructurar y normalizar con el formato exacto requerido para las notas
              cedula_val = str(item_limpio.get("cedula", "")).strip()
              cod_materia_val = str(item_limpio.get("cod_materia", "")).strip()
              tipo_eval_val = str(item_limpio.get("tipo_evaluacion", "Ordinario")).strip()

              if cedula_val and cod_materia_val:
                # Buscar nombre de materia en la BD si no viene especificado en el Excel
                nombre_mat = str(item_limpio.get("nombre_materia", "")).strip()
                if not nombre_mat:
                  mat_doc = db["materias"].find_one({"cod_materia": cod_materia_val})
                  nombre_mat = mat_doc.get("nombre_materia", "Unidad Curricular") if mat_doc else "Unidad Curricular"

                doc_nota = {
                    "cedula": cedula_val,
                    "cod_materia": cod_materia_val,
                    "nombre_materia": nombre_mat,
                    "trayecto": str(item_limpio.get("trayecto", "I")),
                    "nota": float(item_limpio.get("nota", 0.0)),
                    "tipo_evaluacion": tipo_eval_val,
                    "docente": str(item_limpio.get("docente", usuario_actual)),
                    "anio": str(item_limpio.get("anio", datetime.now().year)),
                    "fecha_registro": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                }

                # Upsert basado en combinación de cédula, materia y tipo de evaluación
                filtro_nota = {
                    "cedula": cedula_val,
                    "cod_materia": cod_materia_val,
                    "tipo_evaluacion": tipo_eval_val
                }
                
                resultado = coleccion.update_one(
                    filtro_nota, {"$set": doc_nota}, upsert=True
                )
                if resultado.upserted_id:
                  contador_nuevos += 1
                else:
                  contador_actualizados += 1

            elif clave_unica and clave_unica in item_limpio:
              # Usar Upsert estándar para otras colecciones
              filtro = {clave_unica: item_limpio[clave_unica]}
              resultado = coleccion.update_one(
                  filtro, {"$set": item_limpio}, upsert=True
              )
              if resultado.upserted_id:
                contador_nuevos += 1
              else:
                contador_actualizados += 1
            else:
              # Inserción directa (para historiales múltiples)
              coleccion.insert_one(item_limpio)
              contador_nuevos += 1

          registrar_log(db, usuario_actual, "IMPORTAR_EXCEL", f"Importación masiva en {tipo_carga}: {contador_nuevos} nuevos, {contador_actualizados} actualizados.")
          st.success(
              f"¡Importación completada con éxito! Registros nuevos:"
              f" {contador_nuevos}, Actualizados: {contador_actualizados}"
          )
        else:
          st.error("No se pudo determinar la colección destino.")

    except Exception as e:
      st.error(
          f"Ocurrió un error al procesar el archivo Excel: {str(e)}"
      )