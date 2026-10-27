from datetime import datetime
import pandas as pd
import streamlit as st
from database import get_db
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os


def registrar_log(db, usuario, accion, detalles):
  """Registra un log de auditoría en MongoDB para cada acción crítica."""
  logs_col = db["logs_auditoria"]
  logs_col.insert_one({
      "usuario": usuario,
      "accion": accion,
      "detalles": detalles,
      "fecha": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
  })


def generar_pdf_constancia_notas(filename, estudiante, notas_list, carrera_nombre, total_materias_carrera):
  """Genera el recorrido/constancia de notas en PDF con conteo dinámico, trayecto-año y notas enteras."""
  doc = SimpleDocTemplate(
      filename,
      pagesize=letter,
      rightMargin=30,
      leftMargin=30,
      topMargin=25,
      bottomMargin=25,
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
      fontSize=10,
      leading=12,
      alignment=1,
  )

  body_style = ParagraphStyle(
      'BodyStyle',
      parent=styles['Normal'],
      fontName='Helvetica',
      fontSize=8,
      leading=11,
      alignment=4,
  )

  center_body_style = ParagraphStyle(
      'CenterBodyStyle',
      parent=styles['Normal'],
      fontName='Helvetica',
      fontSize=8.5,
      leading=11,
      alignment=1,
  )

  table_header = ParagraphStyle(
      'TableHeader',
      parent=styles['Normal'],
      fontName='Helvetica-Bold',
      fontSize=7.5,
      leading=9,
      alignment=1,
  )

  table_cell = ParagraphStyle(
      'TableCell',
      parent=styles['Normal'],
      fontName='Helvetica',
      fontSize=7.5,
      leading=9,
      alignment=0,
  )

  # Encabezado con Logo y Membrete
  logo_path = "logo_ucs.jpeg"
  if os.path.exists(logo_path):
    img_logo = Image(logo_path, width=45, height=45)
    texto_membrete = Paragraph(
        "República Bolivariana de Venezuela<br/>"
        "Universidad de las Ciencias de la Salud \"Hugo Chávez Frías\"<br/>"
        "Secretaría General<br/>"
        "Dirección General de Control de Estudios<br/>"
        "Dirección de Control de Estudios de los Programas Nacionales de Formación",
        header_style
    )
    t_head = Table([[img_logo, texto_membrete]], colWidths=[55, 497])
    t_head.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (0,0), 'LEFT'),
    ]))
    story.append(t_head)
  else:
    story.append(Paragraph(
        "República Bolivariana de Venezuela<br/>"
        "Universidad de las Ciencias de la Salud \"Hugo Chávez Frías\"<br/>"
        "Secretaría General<br/>"
        "Dirección General de Control de Estudios<br/>"
        "Dirección de Control de Estudios de los Programas Nacionales de Formación",
        header_style
    ))

  story.append(Spacer(1, 8))
  story.append(Paragraph("<b>CONSTANCIA DE NOTAS</b>", title_style))
  story.append(Spacer(1, 6))

  nombre_est = f"{estudiante.get('apellidos', '').upper()}, {estudiante.get('nombres', '').upper()}"
  cedula_est = estudiante.get('cedula', '')
  cantidad_aprobadas = len(notas_list)

  texto_constancia = f"""
    Quien suscribe, Directora General de Control de Estudios de la Universidad de las Ciencias de la Salud "Hugo Chávez Frías", por medio de la presente hace constar que el/la ciudadana(a): <b>{nombre_est}</b>, titular del documento de identidad N° <b>V-{cedula_est}</b>, tiene aprobadas hasta la fecha de emisión de este documento la cantidad de <b>{cantidad_aprobadas}</b> Unidades Curriculares del Programa Nacional de Formación en <b>{carrera_nombre.upper()} (PNF)</b> de un total de <b>{total_materias_carrera}</b>; obteniendo las siguientes calificaciones:
    """
  story.append(Paragraph(texto_constancia, body_style))
  story.append(Spacer(1, 6))

  table_data = [[
      Paragraph("CÓDIGO", table_header),
      Paragraph("UNIDAD CURRICULAR", table_header),
      Paragraph("TRAYECTO / TRAMO", table_header),
      Paragraph("NOTA", table_header),
  ]]

  for n in notas_list:
    raw_nota = n.get("nota", 0)
    try:
      nota_entera = int(round(float(raw_nota)))
    except (ValueError, TypeError):
      nota_entera = 0

    trayecto_base = str(n.get("trayecto", "I")).replace("Trayecto ", "").strip()
    anio_carga = str(n.get("anio", "2026"))
    tramo_val = n.get("tramo")
    
    if tramo_val:
      trayecto_anio_str = f"Trayecto {trayecto_base} - Tramo {tramo_val} ({anio_carga})"
    else:
      trayecto_anio_str = f"{trayecto_base} - {anio_carga}"

    table_data.append([
        Paragraph(str(n.get("cod_materia", "")), table_cell),
        Paragraph(str(n.get("nombre_materia", "")).upper(), table_cell),
        Paragraph(trayecto_anio_str, table_cell),
        Paragraph(str(nota_entera), table_cell),
    ])

  t_notas = Table(table_data, colWidths=[80, 292, 100, 80])
  t_notas.setStyle(TableStyle([
      ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
      ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
      ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
      ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
      ('TOPPADDING', (0, 0), (-1, -1), 2),
      ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
  ]))
  story.append(t_notas)
  story.append(Spacer(1, 6))

  meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
  now = datetime.now()
  dia_txt = str(now.day)
  mes_txt = meses[now.month - 1]
  anio_txt = str(now.year)

  texto_escala = "Cabe destacar que la escala de notas es del 1 al 20, siendo la mínima aprobatoria de 12 puntos."
  texto_fecha = f"Constancia que se expide a los {dia_txt} días del mes de {mes_txt} del año {anio_txt}."

  story.append(Paragraph(texto_escala, body_style))
  story.append(Spacer(1, 4))
  story.append(Paragraph(texto_fecha, body_style))
  story.append(Spacer(1, 12))

  bloque_firma = f"""
    <b>ISABEL MERLO</b><br/>
    Directora General de Control de Estudios<br/>
    Providencia Administrativa 2018-027-CUOV-04.13 de fecha 09/04/2018
    """
  story.append(Paragraph(bloque_firma, center_body_style))
  story.append(Spacer(1, 8))
  story.append(Paragraph("<b>Sello de Control de Estudios</b>", center_body_style))

  doc.build(story)

def generar_pdf_pase_trayecto(filename, estudiante, notas_list, carrera_nombre, trayecto, asic=""):
  """Genera el documento Pase de Año / Trayecto utilizando el formato institucional."""
  doc = SimpleDocTemplate(
      filename,
      pagesize=letter,
      rightMargin=30,
      leftMargin=30,
      topMargin=25,
      bottomMargin=25,
  )

  story = []
  styles = getSampleStyleSheet()

  title_style = ParagraphStyle(
      'TitleStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=12, alignment=1
  )

  info_style = ParagraphStyle(
      'InfoStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=12, alignment=0
  )

  table_header = ParagraphStyle(
      'TableHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, alignment=1
  )

  table_cell = ParagraphStyle(
      'TableCell', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, alignment=1
  )

  # Encabezado con Logo (Pase de año)
  logo_path = "encabezado_pase.png"
  if os.path.exists(logo_path):
    img = Image(logo_path, width=540, height=65) 
    story.append(img)
    story.append(Spacer(1, 10))

  # Títulos
  story.append(Paragraph("Universidad de las Ciencias de la Salud \"Hugo Chávez Frías\"", title_style))
  story.append(Paragraph(f"P.N.F {carrera_nombre.upper()}", title_style))
  story.append(Spacer(1, 8))
  story.append(Paragraph(f"RESULTADOS DE LAS CALIFICACIONES OBTENIDAS EN EL TRAYECTO {trayecto.upper()} ACADÉMICO {carrera_nombre.upper()}", title_style))
  story.append(Spacer(1, 12))

  # Información del Estudiante
  nombre_est = estudiante.get('nombres', '').upper()
  apellido_est = estudiante.get('apellidos', '').upper()
  cedula_est = estudiante.get('cedula', '')

  texto_info = f"""
  TRAYECTO ACADÉMICO: {trayecto.upper()}<br/>
  CÉDULA DE IDENTIDAD: {cedula_est}<br/>
  ESTADO: BARINAS<br/>
  MUNICIPIO: BARINAS<br/>
  ASIC (Circuito): {asic.upper()}<br/>
  APELLIDOS: {apellido_est}<br/>
  NOMBRES: {nombre_est}
  """
  story.append(Paragraph(texto_info, info_style))
  story.append(Spacer(1, 12))

  # Tabla de Calificaciones
  table_data = [[
      Paragraph("TRAMO", table_header),
      Paragraph("ASIGNATURAS", table_header),
      Paragraph("CERTIFICATIVA", table_header),
      Paragraph("REPARACIÓN I", table_header),
      Paragraph("REPARACIÓN II", table_header),
      Paragraph("FINAL", table_header),
  ]]

  # Agrupamos notas por tramos (PRIMERO, SEGUNDO, TERCERO)
  tramos_estructura = ["I", "II", "III"]
  nombres_tramos = {"I": "PRIMERO", "II": "SEGUNDO", "III": "TERCERO"}

  for t in tramos_estructura:
      notas_tramo = [n for n in notas_list if n.get("tramo") == t]
      
      # Si no hay materias para este tramo, agregamos una fila en blanco para mantener la estructura
      if not notas_tramo:
          notas_tramo = [{"nombre_materia": "------------------", "nota": "", "tipo_evaluacion": ""}]
          
      for idx, n in enumerate(notas_tramo):
          tramo_label = nombres_tramos[t] if idx == 0 else ""

          cert = str(n.get("nota", "")) if n.get("tipo_evaluacion", "") in ["Ordinario", ""] else ""
          rep1 = str(n.get("nota", "")) if n.get("tipo_evaluacion") == "Reparación I" else ""
          rep2 = str(n.get("nota", "")) if n.get("tipo_evaluacion") == "Reparación II" else ""
          final = str(n.get("nota", ""))

          # Si es registro vacío, limpiar notas
          if n.get("nombre_materia") == "------------------":
              cert = rep1 = rep2 = final = ""

          table_data.append([
              Paragraph(tramo_label, table_cell),
              Paragraph(str(n.get("nombre_materia", "")).upper(), table_cell),
              Paragraph(cert, table_cell),
              Paragraph(rep1, table_cell),
              Paragraph(rep2, table_cell),
              Paragraph(final, table_cell)
          ])

  # Notas registradas que no tengan tramo asignado
  notas_sin_tramo = [n for n in notas_list if not n.get("tramo") or n.get("tramo") not in tramos_estructura]
  for n in notas_sin_tramo:
      cert = str(n.get("nota", "")) if n.get("tipo_evaluacion", "") in ["Ordinario", ""] else ""
      rep1 = str(n.get("nota", "")) if n.get("tipo_evaluacion") == "Reparación I" else ""
      rep2 = str(n.get("nota", "")) if n.get("tipo_evaluacion") == "Reparación II" else ""
      final = str(n.get("nota", ""))

      table_data.append([
          Paragraph("-", table_cell),
          Paragraph(str(n.get("nombre_materia", "")).upper(), table_cell),
          Paragraph(cert, table_cell),
          Paragraph(rep1, table_cell),
          Paragraph(rep2, table_cell),
          Paragraph(final, table_cell)
      ])

  t_notas = Table(table_data, colWidths=[65, 207, 70, 70, 70, 50])
  t_notas.setStyle(TableStyle([
      ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
      ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
      ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
  ]))
  
  story.append(t_notas)
  story.append(Spacer(1, 15))

  # Pie de Página (Observaciones, Conclusiones y Firmas)
  meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
  now = datetime.now()
  dia_txt = str(now.day)
  mes_txt = meses[now.month - 1]

  footer_text = f"""
  <b>PROMEDIO DEL TRAYECTO:</b><br/>
  <b>OBSERVACIONES:</b><br/>
  <b>CONCLUSIONES:</b> PROMOVIDO: ______ NO PROMOVIDO: ______<br/><br/>
  FECHA DE ELABORACIÓN: <b>{dia_txt}</b> MES: <b>{mes_txt.upper()}</b><br/><br/>
  CERTIFICO: Que los datos consignados en el presente documento son rigurosamente ciertos, según consta en los Registros de la Secretaría a mi cargo.<br/><br/><br/><br/>
  NOMBRES Y APELLIDOS DEL DIRECTOR DE SECRETARIA DEL NUCLEO ESTADAL:<br/>
  <b>YAMILIS DEL CARMEN SANCHEZ CALLES</b><br/><br/>
  FIRMA Y SELLO DE LA UCS:
  """
  story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13)))

  doc.build(story)


def render():
  st.subheader("📊 Módulo de Calificaciones, Notas y Recorridos")

  db = get_db()
  notas_col = db["notas"]
  estudiantes_col = db["estudiantes"]
  carreras_col = db["carreras"]
  materias_col = db["materias"]
  listas_col = db["listas_generacion"]

  rol_actual = st.session_state.get("rol", "Docente")
  usuario_actual = st.session_state.get("username", "Desconocido")

  # ==========================================
  # VISTA 1: ROL ESTUDIANTE
  # ==========================================
  if rol_actual == "Estudiante":
    st.markdown("### 🎓 Mi Recorrido Académico y Calificaciones")
    cedula_estudiante = st.text_input(
        "Confirme su Cédula de Identidad para ver sus notas"
    ).strip()

    if cedula_estudiante:
      c_str = cedula_estudiante
      c_int = int(c_str) if c_str.isdigit() else None
      q_est = {"$or": [{"cedula": c_str}]}
      if c_int is not None:
        q_est["$or"].append({"cedula": c_int})

      notas_estudiante = list(notas_col.find(q_est, {"_id": 0}))

      if notas_estudiante:
        df_notas = pd.DataFrame(notas_estudiante)
        st.dataframe(df_notas, use_container_width=True, hide_index=True)
      else:
        st.info("No se encontraron calificaciones registradas para esta cédula.")
    return

  # ==========================================
  # VISTA 2: ROL ADMINISTRADOR Y DOCENTE
  # ==========================================
  if rol_actual in ["Administrador", "Docente"]:
    st.markdown("### 📝 Carga y Gestión de Calificaciones (Admin / Docente)")

    # Pestañas dinámicas según el rol
    if rol_actual == "Administrador":
      tab_carga, tab_gestion, tab_solicitudes_notas = st.tabs([
          "➕ Cargar Nota Individual",
          "📋 Listado y Gestión de Notas",
          "📥 Solicitudes Pendientes de Notas"
      ])
    else:
      tab_carga, tab_gestion = st.tabs([
          "➕ Cargar Nota Individual",
          "📋 Listado y Gestión de Notas"
      ])
      tab_solicitudes_notas = None

    with tab_carga:
      st.markdown("#### Buscar Estudiante por Cédula")
      cedula_buscar = st.text_input(
          "Introduce la cédula del estudiante a calificar"
      ).strip()

      if cedula_buscar:
        c_str = cedula_buscar
        c_int = int(c_str) if c_str.isdigit() else None
        q_est = {"$or": [{"cedula": c_str}]}
        if c_int is not None:
          q_est["$or"].append({"cedula": c_int})

        estudiante_encontrado = estudiantes_col.find_one(q_est)

        if estudiante_encontrado:
          nombre_completo = f"{estudiante_encontrado.get('apellidos', '').upper()}, {estudiante_encontrado.get('nombres', '').upper()}"
          cedula_encontrada = estudiante_encontrado.get('cedula')

          st.success(
              f"Vas a cargar nota para: **{nombre_completo}** - Cédula:"
              f" **{cedula_encontrada}**"
          )

          carreras_list = list(carreras_col.find({}, {"_id": 0}))
          nombres_carreras = [
              f"{c.get('cod_pnf', '')} - {c.get('nombre_pnf', '')}"
              for c in carreras_list
          ]
          carrera_sel = st.selectbox(
              "Seleccionar Carrera / PNF", nombres_carreras
          )
          cod_pnf = (
              carrera_sel.split(" - ")[0] if " - " in carrera_sel else ""
          )
          nombre_pnf_limpio = (
              carrera_sel.split(" - ")[1] if " - " in carrera_sel else ""
          )

          trayecto_sel = st.selectbox(
              "Seleccionar Trayecto", ["I", "II", "III", "IV", "V", "VI"]
          )

          materias_list = list(
              materias_col.find(
                  {
                      "cod_pnf": cod_pnf,
                      "trayecto": {"$in": [trayecto_sel, f"Trayecto {trayecto_sel}"]},
                  },
                  {"_id": 0},
              )
          )
          nombres_materias = [
              f"{m.get('cod_materia', '')} - {m.get('nombre_materia', '')}"
              for m in materias_list
          ]

          if nombres_materias:
            materia_sel = st.selectbox(
                "Seleccionar Materia / Unidad Curricular", nombres_materias
            )
            cod_materia = (
                materia_sel.split(" - ")[0] if " - " in materia_sel else ""
            )
            nombre_mat_limpio = (
                materia_sel.split(" - ")[1] if " - " in materia_sel else ""
            )

            # 1. Selector de modalidad y tramo FUERA del form para que aparezca al instante
            tipo_eval = st.selectbox(
                "Tipo de Evaluación",
                ["Ordinario", "Reparación I", "Reparación II"],
            )

            modalidad_eval = st.radio(
                "¿La materia es evaluada por tramos?",
                ["Normal", "Por Tramo"],
                horizontal=True,
                key="modalidad_eval_radio"
            )

            tramo_sel = None
            if modalidad_eval == "Por Tramo":
              tramo_sel = st.selectbox("Seleccionar Tramo", ["I", "II", "III"], key="tramo_selector")

            # 2. Formulario para ingresar la nota final y guardar
            with st.form("form_guardar_nota_individual"):
              col_n1, col_n2 = st.columns(2)
              with col_n1:
                nota_valor = st.number_input(
                    "Calificación (0 a 20)",
                    min_value=0.0,
                    max_value=20.0,
                    step=0.5,
                )
              with col_n2:
                anio_fecha = st.selectbox(
                    "Año Académico / Fecha", [str(y) for y in range(2026, 2018, -1)]
                )
                docente_ingresa = st.text_input(
                    "Nombre del Docente", value=usuario_actual
                )

              btn_guardar = st.form_submit_button(
                  "💾 Guardar Calificación", type="primary"
              )

              if btn_guardar:
                es_por_tramo = (modalidad_eval == "Por Tramo")
                doc_nota = {
                    "cedula": str(cedula_encontrada),
                    "cod_materia": cod_materia,
                    "nombre_materia": nombre_mat_limpio,
                    "trayecto": trayecto_sel,
                    "es_por_tramo": es_por_tramo,
                    "tramo": tramo_sel if es_por_tramo else None,
                    "nota": nota_valor,
                    "tipo_evaluacion": tipo_eval,
                    "docente": docente_ingresa,
                    "anio": anio_fecha,
                    "fecha_registro": datetime.utcnow().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                }

                # Criterio de actualización considerando el tramo
                filtro_query = {
                    "cedula": str(cedula_encontrada),
                    "cod_materia": cod_materia,
                    "tipo_evaluacion": tipo_eval,
                    "tramo": tramo_sel if es_por_tramo else None
                }

                notas_col.update_one(
                    filtro_query,
                    {"$set": doc_nota},
                    upsert=True,
                )

                registrar_log(
                    db,
                    usuario_actual,
                    "CARGAR_NOTA",
                    f"Cargada nota {nota_valor} en {cod_materia} (Tramo: {tramo_sel if es_por_tramo else 'N/A'}) para cédula {cedula_encontrada}",
                )

                st.success("¡Calificación guardada exitosamente!")
          else:
            st.warning(
                "No hay materias registradas para este PNF y trayecto."
            )
        else:
          st.error("No se encontró ningún estudiante con esa cédula.")

      # Mostrar listado de notas cargadas recientemente / por estudiante
      st.markdown("---")
      st.markdown("#### 📋 Consultar Notas por Estudiante")
      ver_cedula_list = st.text_input(
          "Ingrese cédula para consultar sus notas cargadas"
      ).strip()
      if ver_cedula_list:
        c_str = ver_cedula_list
        c_int = int(c_str) if c_str.isdigit() else None
        q_notas = {"$or": [{"cedula": c_str}]}
        if c_int is not None:
          q_notas["$or"].append({"cedula": c_int})

        notas_est = list(notas_col.find(q_notas, {"_id": 0}))
        if notas_est:
          st.dataframe(
              pd.DataFrame(notas_est), use_container_width=True, hide_index=True
          )
        else:
          st.info("No hay notas registradas para esta cédula.")

    with tab_gestion:
      st.markdown("#### Listado y Auditoría de Notas")

      cedula_filtro = st.text_input(
          "Filtrar notas por Cédula de Estudiante (Opcional)"
      ).strip()

      if cedula_filtro:
        c_str = cedula_filtro
        c_int = int(c_str) if c_str.isdigit() else None
        query = {"$or": [{"cedula": c_str}]}
        if c_int is not None:
          query["$or"].append({"cedula": c_int})
      else:
        query = {}

      notas_registradas = list(notas_col.find(query, {"_id": 0}))

      if notas_registradas:
        df_notas = pd.DataFrame(notas_registradas)
        st.dataframe(df_notas, use_container_width=True, hide_index=True)

        if rol_actual == "Administrador":
          st.markdown("---")
          st.markdown("### 👑 Funciones Avanzadas de Administrador")

          st.markdown("#### ✏️ Editar o Eliminar Nota Existente")
          with st.form("form_editar_nota"):
            col_e1, col_e2 = st.columns(2)
            with col_e1:
              cedula_edit = st.text_input("Cédula del estudiante a editar").strip()
              mat_edit = st.text_input("Código de la materia a editar").strip()
              tramo_edit = st.selectbox("Tramo (si aplica)", ["Ninguno", "I", "II", "III"])
              nueva_nota = st.number_input(
                  "Nueva Nota", min_value=0.0, max_value=20.0, step=0.5
              )
            with col_e2:
              nuevo_docente = st.text_input("Nuevo Docente", value=usuario_actual).strip()
              nuevo_anio = st.selectbox("Nuevo Año Académico / Fecha", [str(y) for y in range(2026, 2018, -1)])
              nuevo_tipo_eval = st.selectbox(
                  "Nuevo Tipo de Evaluación",
                  ["Ordinario", "Reparación I", "Reparación II"],
              )

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
              btn_actualizar = st.form_submit_button("Actualizar Nota", type="primary")
            with col_btn2:
              btn_eliminar = st.form_submit_button("🗑️ Eliminar Nota", type="secondary")

            if btn_actualizar:
              c_str = cedula_edit
              c_int = int(c_str) if c_str.isdigit() else None
              q_edit = {"$or": [{"cedula": c_str}]}
              if c_int is not None:
                q_edit["$or"].append({"cedula": c_int})
              q_edit["cod_materia"] = mat_edit
              q_edit["tramo"] = None if tramo_edit == "Ninguno" else tramo_edit

              res = notas_col.update_one(
                  q_edit,
                  {
                      "$set": {
                          "nota": nueva_nota,
                          "docente": nuevo_docente,
                          "anio": nuevo_anio,
                          "tipo_evaluacion": nuevo_tipo_eval,
                          "fecha_registro": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                      }
                  },
              )
              if res.modified_count > 0 or res.matched_count > 0:
                registrar_log(
                    db,
                    usuario_actual,
                    "EDITAR_NOTA",
                    f"Actualizada nota para cédula {cedula_edit} en materia {mat_edit} (Docente: {nuevo_docente}, Año: {nuevo_anio}, Tipo: {nuevo_tipo_eval})",
                )
                st.success("¡Nota y campos actualizados correctamente!")
                st.rerun()
              else:
                st.warning("No se encontró el registro exacto para actualizar.")

            if btn_eliminar:
              c_str = cedula_edit
              c_int = int(c_str) if c_str.isdigit() else None
              q_del = {"$or": [{"cedula": c_str}]}
              if c_int is not None:
                q_del["$or"].append({"cedula": c_int})
              q_del["cod_materia"] = mat_edit
              q_del["tramo"] = None if tramo_edit == "Ninguno" else tramo_edit

              res_del = notas_col.delete_one(q_del)
              if res_del.deleted_count > 0:
                registrar_log(
                    db,
                    usuario_actual,
                    "ELIMINAR_NOTA",
                    f"Eliminada nota para cédula {cedula_edit} en materia {mat_edit} (Tramo: {tramo_edit})",
                )
                st.error("¡La nota ha sido eliminada exitosamente del sistema!")
                st.rerun()
              else:
                st.warning("No se encontró el registro exacto para eliminar.")
          st.markdown("#### 📄 Emitir Recorrido de Notas Oficial (PDF)")
          cedula_pdf = st.text_input(
              "Introduce la cédula para generar el PDF oficial según notas_general"
          ).strip()

          if cedula_pdf:
            c_str = cedula_pdf
            c_int = int(c_str) if c_str.isdigit() else None
            q_est = {"$or": [{"cedula": c_str}]}
            if c_int is not None:
              q_est["$or"].append({"cedula": c_int})

            q_not = {"$or": [{"cedula": c_str}]}
            if c_int is not None:
              q_not["$or"].append({"cedula": c_int})

            est_pdf = estudiantes_col.find_one(q_est)
            notas_pdf = list(notas_col.find(q_not, {"_id": 0}))

            if est_pdf and notas_pdf:
              inscripcion_est = db["inscripciones_historial"].find_one(q_est)
              carrera_nombre_real = "Estudios Universitarios"
              total_materias_carrera = 0
              
              if inscripcion_est and "cod_pnf" in inscripcion_est:
                cod_pnf_est = inscripcion_est["cod_pnf"]
                carrera_doc = carreras_col.find_one({"cod_pnf": cod_pnf_est})
                if carrera_doc:
                  carrera_nombre_real = carrera_doc.get("nombre_pnf", "Estudios Universitarios")
                total_materias_carrera = materias_col.count_documents({"cod_pnf": cod_pnf_est})

              pdf_filename = f"Constancia_Notas_{cedula_pdf}.pdf"
              generar_pdf_constancia_notas(
                  pdf_filename, est_pdf, notas_pdf, carrera_nombre_real, total_materias_carrera
              )

              with open(pdf_filename, "rb") as f:
                st.download_button(
                    label="📥 Descargar Constancia/Recorrido de Notas en PDF",
                    data=f,
                    file_name=pdf_filename,
                    mime="application/pdf",
                )
              registrar_log(
                  db,
                  usuario_actual,
                  "EMITIR_RECORRIDOPDF",
                  f"Generado PDF de notas para cédula {cedula_pdf}",
              )
            else:
              st.warning(
                  "Estudiante no encontrado o sin notas registradas para emitir el PDF."
              )
      else:
        st.info("No hay notas registradas en el sistema bajo este criterio.")

    # Pestaña exclusiva para Administrador
    if tab_solicitudes_notas is not None:
      with tab_solicitudes_notas:
        st.markdown("#### 📥 Estudiantes en Listado de Generación de Notas")
        st.info("Aquí aparecen directamente los estudiantes que solicitaron su **Récord de Notas** desde el módulo de solicitudes.")

        lista_notas_pendientes = list(listas_col.find({"tipo_documento": "Récord de Notas"}))

        if lista_notas_pendientes:
          df_pendientes = pd.DataFrame(lista_notas_pendientes)[["cedula", "nombre", "fecha_agregado"]]
          df_pendientes.columns = ["Cédula", "Estudiante", "Fecha Solicitud / Agregado"]
          st.dataframe(df_pendientes, use_container_width=True, hide_index=True)

          st.markdown("---")
          st.markdown("##### ⚡ Acción Rápida: Seleccionar Estudiante del Listado")
          
          cedulas_opciones = [str(item["cedula"]) for item in lista_notas_pendientes]
          cedula_seleccionada = st.selectbox("Seleccione la Cédula del Solicitante", cedulas_opciones)

          if cedula_seleccionada:
            est_sol = estudiantes_col.find_one({"cedula": cedula_seleccionada}) or estudiantes_col.find_one({"cedula": int(cedula_seleccionada) if cedula_seleccionada.isdigit() else 0})
            
            if est_sol:
              st.success(f"Estudiante seleccionado: **{est_sol.get('apellidos','').upper()}, {est_sol.get('nombres','').upper()}** (C.I: {est_sol.get('cedula')})")
              
              c_str = str(est_sol.get('cedula'))
              c_int = int(c_str) if c_str.isdigit() else None
              q_not = {"$or": [{"cedula": c_str}]}
              if c_int is not None:
                q_not["$or"].append({"cedula": c_int})

              notas_sol = list(notas_col.find(q_not, {"_id": 0}))
              
              if notas_sol:
                st.write("Calificaciones actuales registradas:")
                st.dataframe(pd.DataFrame(notas_sol), use_container_width=True, hide_index=True)

                if rol_actual == "Administrador":
                  inscripcion_est = db["inscripciones_historial"].find_one(q_not)
                  carrera_nombre_real = "Estudios Universitarios"
                  total_materias_carrera = 0
                  
                  if inscripcion_est and "cod_pnf" in inscripcion_est:
                    cod_pnf_est = inscripcion_est["cod_pnf"]
                    carrera_doc = carreras_col.find_one({"cod_pnf": cod_pnf_est})
                    if carrera_doc:
                      carrera_nombre_real = carrera_doc.get("nombre_pnf", "Estudios Universitarios")
                    total_materias_carrera = materias_col.count_documents({"cod_pnf": cod_pnf_est})

                  pdf_filename = f"Constancia_Notas_{cedula_seleccionada}.pdf"
                  generar_pdf_constancia_notas(
                      pdf_filename, est_sol, notas_sol, carrera_nombre_real, total_materias_carrera
                  )

                  with open(pdf_filename, "rb") as f:
                    st.download_button(
                        label=f"📥 Descargar Recorrido Oficial en PDF para {est_sol.get('nombres')}",
                        data=f,
                        file_name=pdf_filename,
                        mime="application/pdf",
                        key=f"dl_pdf_{cedula_seleccionada}"
                    )
              else:
                st.warning("Este estudiante aún no tiene calificaciones cargadas.")
        else:
          st.info("No hay solicitudes pendientes en el listado de generación de notas actualmente.")

      # Nueva pestaña exclusiva para Administrador (Pase de Año)
    if tab_pase_ano is not None:
      with tab_pase_ano:
        st.markdown("#### 🎓 Generación de Documento Pase de Año / Trayecto")
        st.info("Busca al estudiante, visualiza sus calificaciones para un trayecto determinado y emite el documento oficial **Pase de Trayecto** en PDF.")

        cedula_pase = st.text_input("Ingrese la Cédula del Estudiante para emitir el Pase de Año").strip()

        if cedula_pase:
          c_str = cedula_pase
          c_int = int(c_str) if c_str.isdigit() else None
          q_est_pase = {"$or": [{"cedula": c_str}]}
          if c_int is not None:
            q_est_pase["$or"].append({"cedula": c_int})

          est_pase = estudiantes_col.find_one(q_est_pase)

          if est_pase:
            st.success(f"Estudiante encontrado: **{est_pase.get('apellidos', '').upper()}, {est_pase.get('nombres', '').upper()}**")

            # Obtener datos de la carrera actual (desde inscripciones_historial)
            inscripcion_pase = db["inscripciones_historial"].find_one(q_est_pase)
            carrera_nombre_pase = "Estudios Universitarios"
            asic_estudiante = "No Aplica"

            if inscripcion_pase:
              asic_estudiante = inscripcion_pase.get("asic", "No Aplica")
              if "cod_pnf" in inscripcion_pase:
                carrera_doc_pase = carreras_col.find_one({"cod_pnf": inscripcion_pase["cod_pnf"]})
                if carrera_doc_pase:
                  carrera_nombre_pase = carrera_doc_pase.get("nombre_pnf", "Estudios Universitarios")

            col_p1, col_p2 = st.columns(2)
            with col_p1:
              trayecto_pase_sel = st.selectbox("Seleccione el Trayecto a generar", ["I", "II", "III", "IV", "V", "VI"], key="sel_trayecto_pase")
            with col_p2:
              asic_input = st.text_input("ASIC (Circuito)", value=asic_estudiante, key="asic_pase_input")

            # Buscar las notas correspondientes al trayecto
            q_not_pase = q_est_pase.copy()
            q_not_pase["trayecto"] = {"$in": [trayecto_pase_sel, f"Trayecto {trayecto_pase_sel}"]}
            
            notas_pase = list(notas_col.find(q_not_pase, {"_id": 0}))

            if notas_pase:
              st.markdown(f"**Previsualización de Calificaciones (Trayecto {trayecto_pase_sel}):**")
              df_notas_pase = pd.DataFrame(notas_pase)
              st.dataframe(df_notas_pase, use_container_width=True, hide_index=True)

              if st.button("📄 Generar y Descargar Pase de Año (PDF)"):
                pdf_pase_filename = f"Pase_Ano_{cedula_pase}_Trayecto_{trayecto_pase_sel}.pdf"
                
                generar_pdf_pase_trayecto(
                    pdf_pase_filename,
                    est_pase,
                    notas_pase,
                    carrera_nombre_pase,
                    trayecto_pase_sel,
                    asic_input
                )

                with open(pdf_pase_filename, "rb") as f:
                  st.download_button(
                      label=f"📥 Descargar PDF Pase de Año para {est_pase.get('nombres')}",
                      data=f,
                      file_name=pdf_pase_filename,
                      mime="application/pdf",
                  )
                
                registrar_log(
                    db,
                    usuario_actual,
                    "EMITIR_PASE_ANO",
                    f"Generado PDF de Pase de Año para cédula {cedula_pase} en Trayecto {trayecto_pase_sel}",
                )
            else:
              st.warning("No hay notas registradas para este estudiante en el trayecto seleccionado.")
          else:
            st.error("No se encontró ningún estudiante con esa cédula.")
