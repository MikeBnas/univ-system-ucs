import os
import pandas as pd
import streamlit as st
from database import db_conectada, get_db
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generar_pdf_acta(
    filename,
    carrera,
    materia,
    trayecto,
    anio_academico,
    docente_nombre,
    docente_cedula,
    estudiantes_list,
):
  """Genera el acta de notas oficial con el título de acta y la alineación perfecta de firmas por evaluación"""
  
  # Configurar documento en formato horizontal (landscape) con márgenes de 20 pt (ancho útil = 752 pt)
  doc = SimpleDocTemplate(
      filename,
      pagesize=landscape(letter),
      rightMargin=20,
      leftMargin=20,
      topMargin=20,
      bottomMargin=20
  )

  story = []
  styles = getSampleStyleSheet()

  # Estilos personalizados
  ministerio_style = ParagraphStyle(
      'MinisterioStyle',
      parent=styles['Normal'],
      fontName='Helvetica-Bold',
      fontSize=8,
      leading=10,
      alignment=1
  )
  
  acta_title_style = ParagraphStyle(
      'ActaTitleStyle',
      parent=styles['Normal'],
      fontName='Helvetica-Bold',
      fontSize=10,
      leading=12,
      alignment=1
  )

  header_style = ParagraphStyle(
      'HeaderStyle',
      parent=styles['Normal'],
      fontName='Helvetica-Bold',
      fontSize=6,
      leading=7.5,
      alignment=1
  )

  cell_style = ParagraphStyle(
      'CellStyle',
      parent=styles['Normal'],
      fontName='Helvetica',
      fontSize=6.5,
      leading=8.5,
      alignment=0
  )

  # 1. ENCABEZADO INSTITUCIONAL CON IMAGEN Y TÍTULOS OFICIALES
  if os.path.exists("encabezado.jpeg"):
    img = Image("encabezado.jpeg", width=752, height=45)
    story.append(img)
    story.append(Spacer(1, 3))

  story.append(Paragraph("MINISTERIO DEL PODER POPULAR PARA LA EDUCACIÓN UNIVERSITARIA CIENCIA Y TECNOLOGÍA", ministerio_style))
  story.append(Spacer(1, 2))
  story.append(Paragraph("ACTA DE EXAMEN", acta_title_style))
  story.append(Spacer(1, 6))

  # 2. DATOS GENERALES (Carrera, Materia, Trayecto, Curso, Estado, Municipio, ASIC)
  info_data = [
      [
          Paragraph(f"<b>CARRERA / PNF:</b> {carrera.upper()}", cell_style),
          Paragraph(f"<b>CURSO ACADÉMICO:</b> {anio_academico}", cell_style)
      ],
      [
          Paragraph(f"<b>ASIGNATURA O UNIDAD CURRICULAR:</b> {materia.upper()}", cell_style),
          Paragraph(f"<b>TRAYECTO:</b> {trayecto.upper()}", cell_style)
      ],
      [
          Paragraph("<b>ESTADO:</b> Barinas", cell_style),
          Paragraph("<b>MUNICIPIO:</b> ____________________   <b>ASIC:</b> ____________________", cell_style)
      ]
  ]
  
  t_info = Table(info_data, colWidths=[450, 302]) # Suman 752 pt exactos
  t_info.setStyle(TableStyle([
      ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
      ('BOTTOMPADDING', (0,0), (-1,-1), 3),
      ('TOPPADDING', (0,0), (-1,-1), 3),
      ('LINEBELOW', (0,-1), (-1,-1), 1, colors.black),
  ]))
  story.append(t_info)
  story.append(Spacer(1, 6))

  # 3. TABLA DE ESTUDIANTES CON SUBCOLUMNAS OFICIALES
  table_data = [
      [
          Paragraph("N°", header_style),
          Paragraph("NOMBRES Y APELLIDOS", header_style),
          Paragraph("C. IDENT.", header_style),
          Paragraph("ORDINARIO", header_style), "", "",  
          Paragraph("REPARACIÓN I", header_style), "", "", 
          Paragraph("REPARACIÓN II", header_style), "", "" 
      ],
      [
          "", "", "",  
          Paragraph("FIRMA", header_style), Paragraph("EXAMEN", header_style), Paragraph("FINAL", header_style),
          Paragraph("FIRMA", header_style), Paragraph("EXAMEN", header_style), Paragraph("FINAL", header_style),
          Paragraph("FIRMA", header_style), Paragraph("EXAMEN", header_style), Paragraph("FINAL", header_style)
      ]
  ]

  for idx, est in enumerate(estudiantes_list, 1):
    nombre_completo = f"{est.get('apellidos', '').upper()}, {est.get('nombres', '').upper()}"
    table_data.append([
        Paragraph(str(idx), cell_style),
        Paragraph(nombre_completo, cell_style),
        Paragraph(str(est.get('cedula', '')), cell_style),
        Paragraph("", cell_style), Paragraph("", cell_style), Paragraph("", cell_style),
        Paragraph("", cell_style), Paragraph("", cell_style), Paragraph("", cell_style),
        Paragraph("", cell_style), Paragraph("", cell_style), Paragraph("", cell_style)
    ])

  # Anchos de columna exactos que suman 752 pt en total
  t_estudiantes = Table(
      table_data, 
      colWidths=[22, 190, 66, 52, 52, 52, 52, 52, 52, 52, 52, 58],
      repeatRows=2  
  )
  
  t_estudiantes.setStyle(TableStyle([
      ('BACKGROUND', (0,0), (-1,1), colors.lightgrey),
      ('ALIGN', (0,0), (-1,-1), 'CENTER'),
      ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
      ('GRID', (0,0), (-1,-1), 0.5, colors.black),
      ('SPAN', (0,0), (0,1)), 
      ('SPAN', (1,0), (1,1)), 
      ('SPAN', (2,0), (2,1)), 
      ('SPAN', (3,0), (5,0)), 
      ('SPAN', (6,0), (8,0)), 
      ('SPAN', (9,0), (11,0)),
      ('TOPPADDING', (0,0), (-1,-1), 2.5),
      ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
  ]))
  story.append(t_estudiantes)
  story.append(Spacer(1, 8))

  # 4. BLOQUE DE FIRMAS AL PIE (Datos del docente y columnas exactas de firma por evaluación)
  firma_data = [
      [
          Paragraph(f"<b>DOCENTE:</b> {docente_nombre.upper()}<br/><b>C.I:</b> {docente_cedula}", cell_style),
          Paragraph("<b>ORDINARIO</b><br/>Firma: _____________<br/>Fecha: ____/____/20___", cell_style),
          Paragraph("<b>REPARACIÓN I</b><br/>Firma: _____________<br/>Fecha: ____/____/20___", cell_style),
          Paragraph("<b>REPARACIÓN II</b><br/>Firma: _____________<br/>Fecha: ____/____/20___", cell_style)
      ]
  ]
  
  t_firma = Table(firma_data, colWidths=[188, 188, 188, 188]) # Suman 752 pt total
  t_firma.setStyle(TableStyle([
      ('VALIGN', (0,0), (-1,-1), 'TOP'),
      ('GRID', (0,0), (-1,-1), 0.5, colors.black),
      ('TOPPADDING', (0,0), (-1,-1), 5),
      ('BOTTOMPADDING', (0,0), (-1,-1), 15), 
  ]))
  
  story.append(KeepTogether([t_firma]))

  # Construir PDF
  doc.build(story)


def render():
  st.title("📄 Generador Oficial de Actas de Notas")

  if not db_conectada:
    st.error("⚠️ Sin conexión a MongoDB.")
    return

  db = get_db()

  # 1. Selección del Año Académico
  st.markdown("### 1. Parámetros Académicos")
  col_anio, col_car = st.columns(2)
  with col_anio:
    anio_academico = st.selectbox(
        "Año Académico / Periodo", ["2026", "2025", "2024", "2023"]
    )

  # 2. Selección de la Carrera
  carreras_list = list(db["carreras"].find({}, {"_id": 0}))
  if not carreras_list:
    st.warning("⚠️ Debe registrar carreras en el sistema antes de generar actas.")
    return

  nombres_carreras = [f"{c.get('cod_pnf', '')} - {c.get('nombre_pnf', '')}" for c in carreras_list]
  with col_car:
    carrera_sel = st.selectbox("Seleccionar Carrera", nombres_carreras)

  cod_pnf_limpio = carrera_sel.split(" - ")[0] if " - " in carrera_sel else carrera_sel

  # 3. Selección del Trayecto
  col_tray, col_mat = st.columns(2)
  with col_tray:
    trayecto_sel = st.selectbox(
        "Trayecto", ["I", "II", "III", "IV", "V", "VI"]
    )

  # 4. Filtrado de Materias
  trayectos_a_buscar = [trayecto_sel, f"Trayecto {trayecto_sel}"]
  materias_cursor = list(
      db["materias"].find(
          {
              "cod_pnf": cod_pnf_limpio,
              "trayecto": {"$in": trayectos_a_buscar},
          },
          {"_id": 0},
      )
  )

  nombres_materias = (
      [f"{m.get('cod_materia', '')} - {m.get('nombre_materia', '')}" for m in materias_cursor]
      if materias_cursor
      else []
  )

  with col_mat:
    if nombres_materias:
      materia_sel = st.selectbox(
          "Asignatura / Unidad Curricular", nombres_materias
      )
    else:
      st.warning(
          f"⚠️ No hay materias registradas para esta carrera en el trayecto {trayecto_sel}."
      )
      materia_sel = None

  st.markdown("---")
  st.markdown("### 2. Datos del Docente Responsable")
  col3, col4 = st.columns(2)
  with col3:
    docente_nombre = st.text_input(
        "Nombres y Apellidos del Docente", value=st.session_state.username
    )
  with col4:
    docente_cedula = st.text_input("Cédula de Identidad del Docente")

  btn_buscar = st.button(
      "🔍 Cargar y Verificar Estudiantes Activos", type="primary"
  )

  if btn_buscar:
    if not materia_sel:
      st.error("Seleccione una materia válida.")
    else:
      inscripciones = list(
          db["inscripciones_historial"].find(
              {
                  "cod_pnf": cod_pnf_limpio,
                  "trayecto": {"$in": [trayecto_sel, f"Trayecto {trayecto_sel}"]},
                  "estado": "Activo",
              },
              {"_id": 0},
          )
      )

      if inscripciones:
        cedulas_inscritas = [str(i["cedula"]).strip() for i in inscripciones]

        estudiantes_encontrados = list(
            db["estudiantes"].find(
                {
                    "$or": [
                        {"cedula": {"$in": cedulas_inscritas}},
                        {"cedula": {"$in": [int(c) for c in cedulas_inscritas if c.isdigit()]}}
                    ]
                },
                {"_id": 0},
            )
        )

        if estudiantes_encontrados:
          st.session_state["acta_estudiantes"] = estudiantes_encontrados
          st.session_state["acta_params"] = {
              "carrera": carrera_sel,
              "materia": materia_sel,
              "trayecto": trayecto_sel,
              "anio": anio_academico,
              "docente_nombre": docente_nombre,
              "docente_cedula": docente_cedula,
          }
          st.success(f"¡Se cargaron {len(estudiantes_encontrados)} estudiantes activos!")
        else:
          st.warning("Se encontraron inscripciones, pero no coinciden con la tabla de estudiantes.")
          st.session_state["acta_estudiantes"] = []
      else:
        st.warning("No hay estudiantes activos para esta carrera y trayecto.")
        st.session_state["acta_estudiantes"] = []

  if "acta_estudiantes" in st.session_state and st.session_state["acta_estudiantes"]:
    st.markdown("### 📋 Verificación Final del Listado")
    df_est = pd.DataFrame(st.session_state["acta_estudiantes"])
    df_est["Incluir en Acta"] = True

    cols = ["Incluir en Acta"] + [col for col in df_est.columns if col != "Incluir en Acta"]
    df_est = df_est[cols]

    df_editado = st.data_editor(
        df_est, use_container_width=True, hide_index=True
    )

    if st.button("📄 Generar y Descargar Acta en PDF"):
      if not docente_nombre or not docente_cedula:
        st.error("Por favor complete el nombre y la cédula del docente.")
      else:
        estudiantes_finales = df_editado[
            df_editado["Incluir en Acta"] == True
        ].to_dict(orient="records")

        if estudiantes_finales:
          params = st.session_state["acta_params"]
          pdf_filename = "acta_calificaciones.pdf"

          generar_pdf_acta(
              pdf_filename,
              params["carrera"],
              params["materia"],
              params["trayecto"],
              params["anio"],
              params["docente_nombre"],
              params["docente_cedula"],
              estudiantes_finales,
          )

          with open(pdf_filename, "rb") as pdf_file:
            st.download_button(
                label="📥 Descargar Acta Oficial en PDF",
                data=pdf_file,
                file_name=f"Acta_{params['carrera'].split(' - ')[0]}_Trayecto{params['trayecto']}.pdf",
                mime="application/pdf",
            )
          st.success("¡PDF generado correctamente y listo para abrir e imprimir!")
        else:
          st.error("Debe dejar al menos un estudiante seleccionado.")