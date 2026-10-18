import os
from datetime import datetime
import pandas as pd
import streamlit as st
from database import db_conectada, get_db
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def registrar_log(db, usuario, accion, detalles):
  """Registra un log de auditoría en MongoDB para cada acción crítica."""
  logs_col = db["logs_auditoria"]
  logs_col.insert_one({
      "usuario": usuario,
      "accion": accion,
      "detalles": detalles,
      "fecha": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
  })


def generar_pdf_constancia_estudios(filename, estudiante, carrera_nombre, trayecto_actual):
  """Genera la constancia de estudios oficial en PDF basada estrictamente en constancia.docx."""
  doc = SimpleDocTemplate(
      filename,
      pagesize=letter,
      rightMargin=40,
      leftMargin=40,
      topMargin=30,
      bottomMargin=30,
  )

  story = []
  styles = getSampleStyleSheet()

  header_style = ParagraphStyle(
      'HeaderStyle',
      parent=styles['Normal'],
      fontName='Helvetica-Bold',
      fontSize=8,
      leading=10,
      alignment=1,
  )

  title_style = ParagraphStyle(
      'TitleStyle',
      parent=styles['Normal'],
      fontName='Helvetica-Bold',
      fontSize=11,
      leading=14,
      alignment=1,
  )

  body_style = ParagraphStyle(
      'BodyStyle',
      parent=styles['Normal'],
      fontName='Helvetica',
      fontSize=9,
      leading=13,
      alignment=4,  # Justificado
  )

  center_body_style = ParagraphStyle(
      'CenterBodyStyle',
      parent=styles['Normal'],
      fontName='Helvetica',
      fontSize=8.5,
      leading=11,
      alignment=1,
  )

  table_cell_style = ParagraphStyle(
      'TableCellStyle',
      parent=styles['Normal'],
      fontName='Helvetica',
      fontSize=8,
      leading=10,
      alignment=1,
  )

  nota_style = ParagraphStyle(
      'NotaStyle',
      parent=styles['Normal'],
      fontName='Helvetica-Bold',
      fontSize=7.5,
      leading=10,
      alignment=0,
  )

  # Cabecera con imagen encabezado_constancia.png
  logo_path = "encabezado_constancia.png"
  if os.path.exists(logo_path):
    img_logo = Image(logo_path, width=532, height=55)
    story.append(img_logo)
    story.append(Spacer(1, 8))

  encabezado_texto = """
    <b>República Bolivariana de Venezuela</b><br/>
    <b>Universidad de las Ciencias de la Salud “Hugo Chávez Frías”</b><br/>
    Secretaría General<br/>
    Dirección General de Control de Estudios
    """
  story.append(Paragraph(encabezado_texto, header_style))
  story.append(Spacer(1, 10))

  story.append(Paragraph("<b>CONSTANCIA DE ESTUDIOS</b>", title_style))
  story.append(Spacer(1, 10))

  nombres = estudiante.get('nombres', '').upper()
  apellidos = estudiante.get('apellidos', '').upper()
  cedula = estudiante.get('cedula', '')
  
  municipio = estudiante.get('municipio_est', 'Barinas')
  parroquia = estudiante.get('parroquia_est', 'El Carmen')
  asic = estudiante.get('asic_estudiante', 'El Carmen')

  texto_constancia = f"""
    Quien suscribe, <b>ISABE UVINA MERLO VARONA</b>, titular de la Cédula de Identidad Nº V-10328667, Directora (or) Secretaría de la <b>UNIVERSIDAD DE LAS CIENCIAS DE LA SALUD “HUGO CHÁVEZ FRÍAS” UCS-HChF</b>, según Resolución 012 del 10-03-2026, publicada en Gaceta Oficial N° 43334 de fecha 12 de Marzo de 2026, por medio de la presente hace constar que él(la) ciudadano(a) <b>{nombres} {apellidos}</b>, de Nacionalidad VENEZOLANA, Titular del Documento de Identidad N° <b>V-{cedula}</b>, es estudiante activo(a) del Programa Nacional de Formación en <b>{carrera_nombre.upper()}</b>. Actualmente cursando el: <b>trayecto {trayecto_actual}</b> del año 2026, en el Área de Salud Integral Comunitaria ASIC <b>{asic}</b>, ubicada en la Parroquia <b>{parroquia}</b>, Municipio <b>{municipio}</b> del Estado Barinas.
    """
  story.append(Paragraph(texto_constancia, body_style))
  story.append(Spacer(1, 10))

  meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
  now = datetime.now()
  dia_txt = str(now.day)
  mes_txt = meses[now.month - 1]
  anio_txt = str(now.year)

  texto_fecha = f"Constancia que se expide a petición de la parte interesada, en la Ciudad de Barinas, a los {dia_txt} días del mes de {mes_txt} del año {anio_txt}."
  story.append(Paragraph(texto_fecha, body_style))
  story.append(Spacer(1, 15))

  # Parte superior de firmas: ATENTAMENTE y Dirección de Secretaría
  atentamente_texto = """
    <b>ATENTAMENTE</b><br/><br/>
    <b>DIRECCIÓN DE SECRETARÍA</b><br/>
    Universidad de las Ciencias de la Salud "Hugo Chávez Frías"
    """
  story.append(Paragraph(atentamente_texto, center_body_style))
  story.append(Spacer(1, 10))

  # Cuadros de Validado por y Sello
  firma_data = [
      [
          Paragraph("<b>VALIDADO POR</b><br/><b>DIRECTOR (A) ACADÉMICO DEL NÚCLEO</b><br/><br/>NOMBRES Y APELLIDOS: YAMILIS SANCHEZ<br/>N° DOC. IDENT: V-13882909<br/><br/>FIRMA: ___________________", table_cell_style),
          Paragraph("<b>SELLO</b><br/><br/><br/>________________________", table_cell_style)
      ]
  ]

  t_firma = Table(firma_data, colWidths=[360, 172])
  t_firma.setStyle(TableStyle([
      ('VALIGN', (0,0), (-1,-1), 'TOP'),
      ('GRID', (0,0), (-1,-1), 0.5, colors.black),
      ('TOPPADDING', (0,0), (-1,-1), 5),
      ('BOTTOMPADDING', (0,0), (-1,-1), 5),
  ]))
  story.append(t_firma)
  story.append(Spacer(1, 10))

  # Nota al pie de validez
  nota_validez = "<b>NOTA:</b> Esta Constancia de no contar con la firma y sello de la Dirección de Secretaría del Núcleo Estadal, pierde su validez."
  story.append(Paragraph(nota_validez, nota_style))

  doc.build(story)


def render():
  st.title("👨‍🎓 Gestión de Estudiantes e Inscripciones")

  if not db_conectada:
    st.error("⚠️ Sin conexión a MongoDB.")
    return

  db = get_db()
  estudiantes_col = db["estudiantes"]
  carreras_col = db["carreras"]
  inscripciones_col = db["inscripciones_historial"]
  listas_col = db["listas_generacion"]
  usuario_actual = st.session_state.get("username", "Admin")

  tab1, tab2, tab3 = st.tabs([
      "📋 Listado General",
      "➕ Registrar / Inscribir",
      "🔄 Historial de Carreras y Constancias",
  ])

  carreras_disponibles = list(carreras_col.find({}, {"_id": 0}))
  nombres_carreras = (
      [c["cod_pnf"] + " - " + c["nombre_pnf"] for c in carreras_disponibles]
      if carreras_disponibles
      else ["Sin carreras registradas"]
  )

  with tab1:
    st.subheader("Estudiantes Registrados")
    cursor = list(estudiantes_col.find({}, {"_id": 0}))
    if cursor:
      df = pd.DataFrame(cursor)
      st.dataframe(df, use_container_width=True)
    else:
      st.info("No hay estudiantes cargados.")

    st.markdown("---")
    st.markdown("#### 📋 Solicitudes de Constancias Pendientes (Listado General)")
    lista_constancias = list(listas_col.find({"tipo_documento": "Constancia de Estudios"}))

    if lista_constancias:
      df_const = pd.DataFrame(lista_constancias)[["cedula", "nombre", "fecha_agregado"]]
      df_const.columns = ["Cédula", "Estudiante", "Fecha Agregado"]
      st.dataframe(df_const, use_container_width=True, hide_index=True)

      cedulas_const_opciones = [str(item["cedula"]) for item in lista_constancias]
      cedula_sel_c = st.selectbox("Seleccione Cédula del Estudiante para Emitir su Constancia", cedulas_const_opciones, key="sel_const_gen")

      if cedula_sel_c:
        est_c = estudiantes_col.find_one({"cedula": cedula_sel_c}) or estudiantes_col.find_one({"cedula": int(cedula_sel_c) if cedula_sel_c.isdigit() else 0})
        
        if est_c:
          inscripcion_c = inscripciones_col.find_one({"cedula": cedula_sel_c}) or inscripciones_col.find_one({"cedula": int(cedula_sel_c) if cedula_sel_c.isdigit() else 0})
          carrera_nom_c = "Estudios Universitarios"
          tray_c = "I"

          if inscripcion_c:
            tray_c = inscripcion_c.get("trayecto", "I").replace("Trayecto ", "").strip()
            cp = inscripcion_c.get("cod_pnf")
            cdoc = carreras_col.find_one({"cod_pnf": cp})
            if cdoc:
              carrera_nom_c = cdoc.get("nombre_pnf", "Estudios Universitarios")

          pdf_filename_gen = f"Constancia_Estudios_{cedula_sel_c}.pdf"
          generar_pdf_constancia_estudios(pdf_filename_gen, est_c, carrera_nom_c, tray_c)

          with open(pdf_filename_gen, "rb") as f:
            st.download_button(
                label=f"📥 Descargar Constancia Oficial en PDF para {est_c.get('nombres')}",
                data=f,
                file_name=pdf_filename_gen,
                mime="application/pdf",
                key=f"dl_c_{cedula_sel_c}"
            )

      if st.button("🗑️ Vaciar Listado de Constancias", type="primary", key="vaciar_constancias_btn"):
        listas_col.delete_many({"tipo_documento": "Constancia de Estudios"})
        registrar_log(db, usuario_actual, "VACIAR_LISTADO", "Vació el listado de generación de constancias")
        st.success("¡Listado de constancias vaciado correctamente!")
        st.rerun()
    else:
      st.info("No hay solicitudes pendientes en el listado de generación de constancias.")

  with tab2:
    st.subheader("Registro y Asignación de Carrera")
    with st.form("form_reg_estudiante", clear_on_submit=True):
      col1, col2 = st.columns(2)
      with col1:
        cedula = st.text_input("Cédula (Clave Principal)")
        nombres = st.text_input("Nombres")
      with col2:
        correo = st.text_input("Correo Electrónico")
        apellidos = st.text_input("Apellidos")

      st.markdown("---")
      st.markdown("#### Datos Académicos Iniciales y Ubicación")
      carrera_sel = st.selectbox("Seleccionar Carrera", nombres_carreras)
      trayecto_sel = st.selectbox(
          "Trayecto / Periodo",
          [
              "I",
              "II",
              "III",
              "IV",
              "V",
              "VI"
          ],
      )
      
      col_u1, col_u2, col_u3 = st.columns(3)
      with col_u1:
        asic_est = st.text_input("ASIC", value="El Carmen")
      with col_u2:
        parroquia_est = st.text_input("Parroquia", value="El Carmen")
      with col_u3:
        municipio_est = st.text_input("Municipio", value="Barinas")

      submit = st.form_submit_button("Guardar e Inscribir")

      if submit:
        if cedula and nombres and apellidos:
          estudiante_existente = estudiantes_col.find_one({"cedula": cedula})
          if not estudiante_existente:
            estudiantes_col.insert_one({
                "cedula": cedula,
                "nombres": nombres,
                "apellidos": apellidos,
                "correo": correo,
                "asic_estudiante": asic_est,
                "parroquia_est": parroquia_est,
                "municipio_est": municipio_est
            })

          inscripciones_col.update_many(
              {"cedula": cedula, "estado": "Activo"},
              {"$set": {"estado": "Histórico"}},
          )

          codigo_carrera_limpio = (
              carrera_sel.split(" - ")[0]
              if " - " in carrera_sel
              else carrera_sel
          )

          inscripciones_col.insert_one({
              "cedula": cedula,
              "cod_pnf": codigo_carrera_limpio,
              "trayecto": trayecto_sel,
              "estado": "Activo",
          })

          st.success(
              f"Estudiante {nombres} {apellidos} procesado e inscrito en"
              f" {carrera_sel} ({trayecto_sel})."
          )
          st.rerun()
        else:
          st.error("Completa Cédula, Nombres y Apellidos.")

  with tab3:
    st.subheader("Historial de Trayectos, Cambios de Carrera y Constancia")
    cedula_consulta = st.text_input(
        "Ingrese la Cédula para ver su historial y emitir constancia:"
    ).strip()

    if cedula_consulta:
      c_str = cedula_consulta
      c_int = int(c_str) if c_str.isdigit() else None
      q = {"$or": [{"cedula": c_str}]}
      if c_int is not None:
        q["$or"].append({"cedula": c_int})

      estudiante_encontrado = estudiantes_col.find_one(q)

      if estudiante_encontrado:
        st.success(f"Estudiante Encontrado: **{estudiante_encontrado.get('apellidos','').upper()}, {estudiante_encontrado.get('nombres','').upper()}** (C.I: {estudiante_encontrado.get('cedula')})")

        with st.expander("⚙️ Editar Datos de Ubicación (ASIC, Municipio, Parroquia)"):
          with st.form("form_editar_ubicacion_est"):
            nuevo_asic = st.text_input("ASIC del Estudiante", value=estudiante_encontrado.get("asic_estudiante", "El Carmen"))
            nueva_parroquia = st.text_input("Parroquia", value=estudiante_encontrado.get("parroquia_est", "El Carmen"))
            nuevo_municipio = st.text_input("Municipio", value=estudiante_encontrado.get("municipio_est", "Barinas"))
            btn_actualizar_ubi = st.form_submit_button("Guardar Cambios de Ubicación")

            if btn_actualizar_ubi:
              estudiantes_col.update_one(
                  {"_id": estudiante_encontrado["_id"]},
                  {"$set": {
                      "asic_estudiante": nuevo_asic,
                      "parroquia_est": nueva_parroquia,
                      "municipio_est": nuevo_municipio
                  }}
              )
              registrar_log(db, usuario_actual, "ACTUALIZAR_UBICACION", f"Actualizó ubicación para cédula {estudiante_encontrado.get('cedula')}")
              st.success("¡Datos actualizados correctamente!")
              st.rerun()

        inscripcion_activa = inscripciones_col.find_one({**q, "estado": "Activo"}) or inscripciones_col.find_one(q)
        carrera_nombre_est = "Estudios Universitarios"
        trayecto_val_est = "I"

        if inscripcion_activa:
          trayecto_val_est = inscripcion_activa.get("trayecto", "I").replace("Trayecto ", "").strip()
          cod_p = inscripcion_activa.get("cod_pnf")
          carr_doc = carreras_col.find_one({"cod_pnf": cod_p})
          if carr_doc:
            carrera_nombre_est = carr_doc.get("nombre_pnf", "Estudios Universitarios")

        st.markdown("---")
        st.markdown("##### 📄 Emisión de Constancia de Estudios Oficial")
        if st.button("📥 Generar y Descargar Constancia de Estudios en PDF", type="primary", key="btn_gen_const_tab3"):
          pdf_filename = f"Constancia_Estudios_{estudiante_encontrado.get('cedula')}.pdf"
          generar_pdf_constancia_estudios(pdf_filename, estudiante_encontrado, carrera_nombre_est, trayecto_val_est)

          with open(pdf_filename, "rb") as f:
            st.download_button(
                label="📥 Descargar PDF Generado",
                data=f,
                file_name=pdf_filename,
                mime="application/pdf",
                key="dl_btn_tab3_pdf"
            )
          registrar_log(db, usuario_actual, "EMITIR_CONSTANCIAPDF", f"Generó Constancia de Estudios para cédula {estudiante_encontrado.get('cedula')}")
          st.success("¡Constancia generada exitosamente!")

      historial = list(
          inscripciones_col.find(q, {"_id": 0})
      )

      if historial:
        carreras_dict = {
            c["cod_pnf"]: c["nombre_pnf"]
            for c in db["carreras"].find({}, {"_id": 0})
        }

        historial_enriquecido = []
        for item in historial:
          cod_carrera = item.get("cod_pnf")
          nombre_carrera = carreras_dict.get(cod_carrera, cod_carrera)

          item_copia = item.copy()
          item_copia["nombre_pnf"] = nombre_carrera
          historial_enriquecido.append(item_copia)

        st.markdown("---")
        st.markdown("##### 📊 Historial de Inscripciones")
        st.dataframe(pd.DataFrame(historial_enriquecido), use_container_width=True)
      else:
        st.warning(
            f"No se encontró historial para la cédula '{cedula_consulta}'."
        )