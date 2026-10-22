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
    tramo,
    asic,
    anio_academico,
    docente_nombre,
    docente_cedula,
    estudiantes_list,
):
  """Genera el acta de notas oficial con bloques fijos, orden alfabético, tramo y filtro por ASIC"""

  styles = getSampleStyleSheet()

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

  # 1. Función para dibujar Bloque 1 (Imagen y Títulos) y Bloque 2 (Datos generales) fijos en cada página
  def dibujar_encabezado_fijo(canvas, doc_obj):
    canvas.saveState()
    y_cursor = letter[0] - 20 

    # Imagen de encabezado (encabezado.jpeg)
    logo_path = "encabezado.jpeg"
    if os.path.exists(logo_path):
      canvas.drawImage(logo_path, 20, y_cursor - 45, width=752, height=45)
      y_cursor -= 48

    # Títulos institucionales (Bloque 1)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawCentredString(792 / 2.0, y_cursor - 8, "MINISTERIO DEL PODER POPULAR PARA LA EDUCACIÓN UNIVERSITARIA CIENCIA Y TECNOLOGÍA")
    y_cursor -= 14
    
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawCentredString(792 / 2.0, y_cursor - 8, "ACTA DE EXAMEN")
    y_cursor -= 18

    # Bloque 2: Datos generales fijos en cada página (Incluyendo ASIC y Tramo)
    trayecto_txt = f"Trayecto: {trayecto.upper()}"
    tramo_txt = f"Tramo: {tramo}" if tramo != "No Aplica" and tramo else "Tramo: "
    asic_txt = f"ASIC: {asic.upper()}" if asic and asic != "No Aplica" else "ASIC: ____________________"
    
    info_data = [
        [
            Paragraph(f"<b>CARRERA / PNF:</b> {carrera.upper()}", cell_style),
            Paragraph(f"<b>CURSO ACADÉMICO:</b> {anio_academico}", cell_style)
        ],
        [
            Paragraph(f"<b>ASIG. O UNIDAD CURRICULAR:</b> {materia.upper()}", cell_style),
            Paragraph(f"<b>{trayecto_txt}</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>{tramo_txt}</b>", cell_style)
        ],
        [
            Paragraph("<b>ESTADO:</b> Barinas", cell_style),
            Paragraph(f"<b>MUNICIPIO:</b> ____________________   <b>{asic_txt}</b>", cell_style)
        ]
    ]
    
    t_info = Table(info_data, colWidths=[450, 302])
    t_info.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('LINEBELOW', (0,-1), (-1,-1), 1, colors.black),
    ]))
    
    t_info.wrapOn(canvas, 752, 500)
    t_info.drawOn(canvas, 20, y_cursor - 45)

    canvas.restoreState()

  # 2. Función para dibujar el Bloque 5 (Firmas al pie) fijo al fondo de cada página
  def dibujar_pie_fijo(canvas, doc_obj):
    canvas.saveState()
    
    firma_data = [
        [
            Paragraph(f"<b>DOCENTE:</b> {docente_nombre.upper()}<br/><b>C.I:</b> {docente_cedula}", cell_style),
            Paragraph("<b>ORDINARIO</b><br/>Firma: _____________<br/>Fecha: ____/____/20___", cell_style),
            Paragraph("<b>REPARACIÓN I</b><br/>Firma: _____________<br/>Fecha: ____/____/20___", cell_style),
            Paragraph("<b>REPARACIÓN II</b><br/>Firma: _____________<br/>Fecha: ____/____/20___", cell_style)
        ]
    ]
    
    t_firma = Table(firma_data, colWidths=[188, 188, 188, 188])
    t_firma.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10), 
    ]))
    
    t_firma.wrapOn(canvas, 752, 100)
    t_firma.drawOn(canvas, 20, 20)

    canvas.restoreState()

  # Configuración del documento
  doc = SimpleDocTemplate(
      filename,
      pagesize=landscape(letter),
      rightMargin=20,
      leftMargin=20,
      topMargin=140,
      bottomMargin=65
  )

  story = []

  # Ordenar estudiantes alfabéticamente por el primer apellido
  estudiantes_ordenados = sorted(
      estudiantes_list, 
      key=lambda x: str(x.get('apellidos', '')).strip().upper()
  )

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

  for idx, est in enumerate(estudiantes_ordenados, 1):
    nombre_completo = f"{est.get('apellidos', '').upper()}, {est.get('nombres', '').upper()}"
    table_data.append([
        Paragraph(str(idx), cell_style),
        Paragraph(nombre_completo, cell_style),
        Paragraph(str(est.get('cedula', '')), cell_style),
        Paragraph("", cell_style), Paragraph("", cell_style), Paragraph("", cell_style),
        Paragraph("", cell_style), Paragraph("", cell_style), Paragraph("", cell_style),
        Paragraph("", cell_style), Paragraph("", cell_style), Paragraph("", cell_style)
    ])

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
      ('TOPPADDING', (0,0), (-1,-1), 2),
      ('BOTTOMPADDING', (0,0), (-1,-1), 2),
  ]))
  
  story.append(Spacer(1, 4))
  story.append(t_estudiantes)

  doc.build(
      story, 
      onFirstPage=lambda c, d: [dibujar_encabezado_fijo(c, d), dibujar_pie_fijo(c, d)], 
      onLaterPages=lambda c, d: [dibujar_encabezado_fijo(c, d), dibujar_pie_fijo(c, d)]
  )


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

   nombres_materias = (
      [f"{m.get('cod_materia', '')} - {m.get('nombre_materia', '')}" for m in materias_cursor]
      if materias_cursor
      else []
  )

  if nombres_materias:
    materia_sel = st.selectbox(
        "Asignatura / Unidad Curricular", nombres_materias
    )
  else:
    st.warning(
        f"⚠️ No hay materias registradas para esta carrera en el trayecto {trayecto_sel}."
    )
    materia_sel = None

  # 3. Selección del Trayecto, Tramo y ASIC
  col_tray, col_tram = st.columns(2)
  with col_tray:
    trayecto_sel = st.selectbox(
        "Trayecto", ["I", "II", "III", "IV", "V", "VI"]
    )

  with col_tram:
    usar_tramo = st.radio("¿La materia se evalúa por tramos?", ["No", "Sí"], horizontal=True, key="radio_tramo_acta")
    tramo_sel = "No Aplica"
    if usar_tramo == "Sí":
      tramo_sel = st.selectbox("Seleccione el Tramo", ["I", "II", "III"], key="sel_tramo_acta")

  # NUEVO: Selector opcional de ASIC en Parámetros Académicos
  st.markdown("---")
  usar_asic = st.radio("¿Seleccionar estudiantes por ASIC?", ["No", "Sí"], horizontal=True, key="radio_asic_actas")
  asic_sel = "No Aplica"
  
  if usar_asic == "Sí":
    asics_registradas = [str(a).strip() for a in db["inscripciones_historial"].distinct("asic") if a]
    if asics_registradas:
      asic_sel = st.selectbox("Seleccione la ASIC", asics_registradas, key="sel_asic_dropdown")
    else:
      asic_sel = st.text_input("Ingrese el nombre de la ASIC", key="txt_asic_input")

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
      # Armar consulta en inscripciones_historial incluyendo el filtro opcional de ASIC
      query_insc = {
          "cod_pnf": cod_pnf_limpio,
          "trayecto": {"$in": [trayecto_sel, f"Trayecto {trayecto_sel}"]},
          "estado": "Activo",
      }
      if usar_asic == "Sí" and asic_sel and asic_sel != "No Aplica":
        query_insc["asic"] = asic_sel

      inscripciones = list(db["inscripciones_historial"].find(query_insc, {"_id": 0}))

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
              "tramo": tramo_sel,
              "asic": asic_sel,
              "anio": anio_academico,
              "docente_nombre": docente_nombre,
              "docente_cedula": docente_cedula,
          }
          st.success(f"¡Se cargaron {len(estudiantes_encontrados)} estudiantes activos para la ASIC seleccionada!")
        else:
          st.warning("Se encontraron inscripciones, pero no coinciden con la tabla de estudiantes.")
          st.session_state["acta_estudiantes"] = []
      else:
        st.warning("No hay estudiantes activos para esta carrera, trayecto y ASIC seleccionada.")
        st.session_state["acta_estudiantes"] = []

  if "acta_estudiantes" in st.session_state and st.session_state["acta_estudiantes"]:
    st.markdown("### 📋 Verificación Final del Listado (Orden Alfabético por Apellido)")
    df_est = pd.DataFrame(st.session_state["acta_estudiantes"])
    
    if "apellidos" in df_est.columns:
      df_est = df_est.sort_values(by="apellidos", ascending=True)

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
              params["tramo"],
              params["asic"],
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
          st.success("¡Acta generada perfectamente con el filtro ASIC aplicado y diseño institucional!")
        else:
          st.error("Debe dejar al menos un estudiante seleccionado.")
