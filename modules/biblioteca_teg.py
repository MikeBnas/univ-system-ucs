from datetime import datetime
import pandas as pd
import streamlit as st
from database import db_conectada, get_db

def inyectar_estilos_pubmed():
  """Estilos CSS inspirados en PubMed / repositorios científicos modernos y carruseles."""
  st.markdown(
      """
      <style>
      /* Encabezado estilo PubMed */
      .pubmed-header {
          background: linear-gradient(135deg, #0b3954 0%, #087e8b 100%);
          padding: 1.8rem 2rem;
          border-radius: 10px;
          color: white;
          margin-bottom: 1.5rem;
          box-shadow: 0 4px 12px rgba(0,0,0,0.08);
      }
      .pubmed-header h1 {
          margin: 0;
          font-size: 1.9rem;
          font-weight: 700;
          letter-spacing: -0.5px;
      }
      .pubmed-header p {
          margin: 0.4rem 0 0 0;
          font-size: 0.98rem;
          opacity: 0.92;
      }

      /* Tarjetas de Resultados estilo artículo científico */
      .teg-card {
          background-color: #ffffff;
          border: 1px solid #e1e8ed;
          border-left: 5px solid #087e8b;
          border-radius: 8px;
          padding: 1.1rem 1.3rem;
          margin-bottom: 1rem;
          transition: all 0.2s ease;
          box-shadow: 0 2px 5px rgba(0,0,0,0.03);
      }
      .teg-card:hover {
          box-shadow: 0 6px 16px rgba(8, 126, 139, 0.12);
          border-color: #087e8b;
      }
      .teg-title {
          color: #0b3954;
          font-size: 1.15rem;
          font-weight: 700;
          margin-bottom: 0.3rem;
          line-height: 1.35;
      }
      .teg-meta {
          color: #52606d;
          font-size: 0.86rem;
          margin-bottom: 0.6rem;
      }
      .teg-badge {
          display: inline-block;
          background-color: #e6f4f1;
          color: #087e8b;
          padding: 2px 9px;
          border-radius: 12px;
          font-size: 0.78rem;
          font-weight: 600;
          margin-right: 6px;
      }
      .teg-abstract {
          color: #323f4b;
          font-size: 0.92rem;
          line-height: 1.5;
          margin-top: 0.5rem;
      }

      /* Tarjetas de Carrusel */
      .carousel-card {
          background: #f8fafc;
          border: 1px solid #cbd5e1;
          border-radius: 8px;
          padding: 0.9rem;
          height: 100%;
      }
      .carousel-tag {
          font-size: 0.72rem;
          text-transform: uppercase;
          font-weight: 700;
          color: #087e8b;
          letter-spacing: 0.5px;
      }
      </style>
      """,
      unsafe_allow_html=True,
  )


def registrar_busqueda_analitica(db, filtros_usados, resultados_count):
  """Guarda métricas de búsqueda en MongoDB."""
  if any(filtros_usados.values()):
    db["analitica_biblioteca"].insert_one({
        "termino_busqueda": filtros_usados.get("query", ""),
        "carrera": filtros_usados.get("carrera", "Todas"),
        "especialidad": filtros_usados.get("especialidad", "Todas"),
        "anio": filtros_usados.get("anio", "Todos"),
        "resultados_encontrados": resultados_count,
        "usuario": st.session_state.get("username", "Anonimo"),
        "rol": st.session_state.get("rol", "Estudiante"),
        "fecha": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
    })


def render_carrusel(titulo_seccion, icono, documentos, key_prefix):
  """Renderiza un carrusel paginado horizontalmente (3 tarjetas por vista) al estilo repositorio."""
  st.markdown(f"### {icono} {titulo_seccion}")

  if not documentos:
    st.info("Aún no hay trabajos suficientes para mostrar en esta sección.")
    return

  # Estado de paginación del carrusel
  state_key = f"carousel_idx_{key_prefix}"
  if state_key not in st.session_state:
    st.session_state[state_key] = 0

  items_por_pagina = 3
  total_items = len(documentos)
  max_idx = max(0, (total_items - 1) // items_por_pagina)

  col_prev, col_cards, col_next = st.columns([0.6, 10, 0.6])

  with col_prev:
    st.write("")
    st.write("")
    if st.button(
        "◀",
        key=f"prev_{key_prefix}",
        disabled=(st.session_state[state_key] == 0),
    ):
      st.session_state[state_key] -= 1
      st.rerun()

  with col_next:
    st.write("")
    st.write("")
    if st.button(
        "▶",
        key=f"next_{key_prefix}",
        disabled=(st.session_state[state_key] >= max_idx),
    ):
      st.session_state[state_key] += 1
      st.rerun()

  inicio = st.session_state[state_key] * items_por_pagina
  visibles = documentos[inicio : inicio + items_por_pagina]

  with col_cards:
    cols = st.columns(len(visibles))
    for idx, doc in enumerate(visibles):
      with cols[idx]:
        with st.container(border=True):
          img_url = str(doc.get("url_imagen", "")).strip()
          if img_url and img_url.startswith("http"):
            st.image(img_url, use_container_width=True)
          else:
            st.markdown(
                "<div"
                " style='height:110px;background:#e2e8f0;border-radius:6px;display:flex;align-items:center;justify-content:center;color:#475569;font-size:2rem;'>📘</div>",
                unsafe_allow_html=True,
            )

          st.markdown(
              f"<span class='carousel-tag'>{doc.get('carrera', 'General')} •"
              f" {doc.get('anio', 'S/A')}</span>",
              unsafe_allow_html=True,
          )
          titulo_corto = str(doc.get("titulo", "Sin título"))
          if len(titulo_corto) > 65:
            titulo_corto = titulo_corto[:62] + "..."
          st.markdown(f"**{titulo_corto}**")
          st.caption(f"✍️ {doc.get('autor', 'Autor no registrado')}")

          c1, c2 = st.columns(2)
          c1.caption(f"👍 {doc.get('votos', 0)} votos")
          doc_url = str(doc.get("url_documento", "")).strip()
          if doc_url and doc_url.startswith("http"):
            c2.link_button("📄 Leer", doc_url, use_container_width=True)


def render_guia_teg():
  """Renderiza la pestaña de orientación para elaborar el TEG y las Diapositivas con enlaces a Google Drive."""
  st.markdown("### 🎓 Guía Metodológica: Elaboración del TEG y Diapositivas")
  st.caption(
      "Orientaciones oficiales basadas en el Manual de Normas para la"
      " Elaboración del Trabajo Especial de Grado (DG-PNFA) y el Anexo N° 15"
      " para la defensa oral en la UCS 'Hugo Chávez Frías'."
  )

  # ==============================================================================
  # DOCUMENTOS OFICIALES ALOJADOS EN GOOGLE DRIVE
  # ==============================================================================
  st.markdown("#### 📂 Documentos Oficiales de Consulta y Descarga (Google Drive)")

  # Leer enlaces desde st.secrets si existen, o usar los enlaces configurados por defecto
  url_manual_teg = "https://drive.google.com/file/d/REEMPLAZAR_CON_ID_TEG_MANUAL/view?usp=sharing"
  url_diapositivas_teg = "https://drive.google.com/file/d/REEMPLAZAR_CON_ID_DIAPOSITIVAS_TEG/view?usp=sharing"

  if "google_drive" in st.secrets:
    url_manual_teg = st.secrets["google_drive"].get(
        "teg_manual_url", url_manual_teg
    )
    url_diapositivas_teg = st.secrets["google_drive"].get(
        "diapositivas_teg_url", url_diapositivas_teg
    )

  col_d1, col_d2 = st.columns(2)
  with col_d1:
    with st.container(border=True):
      st.markdown("##### 📘 Manual de Normas TEG (`teg_manual.pdf`)")
      st.write(
          "Contiene las normas metodológicas, estructura por capítulos,"
          " citación APA, plazos de entrega, criterios de evaluación del jurado"
          " y todos los anexos oficiales."
      )
      st.link_button(
          "📥 Abrir / Descargar Manual TEG (Google Drive)",
          url_manual_teg,
          type="primary",
          use_container_width=True,
      )

  with col_d2:
    with st.container(border=True):
      st.markdown("##### 📊 Guía de Diapositivas (`diapositivas_teg.docx`)")
      st.write(
          "Contiene la estructura oficial lámina por lámina (Anexo N° 15),"
          " especificaciones de tipografía, uso obligatorio del cintillo UCS y"
          " pautas de diseño para la presentación."
      )
      st.link_button(
          "📥 Abrir / Descargar Guía de Diapositivas (Google Drive)",
          url_diapositivas_teg,
          type="primary",
          use_container_width=True,
      )

  st.markdown("---")

  # ==============================================================================
  # SUB-PESTAÑAS CON LAS INDICACIONES DETALLADAS DE AMBOS DOCUMENTOS
  # ==============================================================================
  sub_manual, sub_diapos, sub_tramites = st.tabs([
      "📝 Cómo realizar el TEG (Manual)",
      "🖥️ Cómo hacer las Diapositivas",
      "⚖️ Consignación y Evaluación",
  ])

  # ------------------------------------------------------------------------------
  # 1. CÓMO REALIZAR EL TRABAJO ESPECIAL DE GRADO (teg_manual.pdf)
  # ------------------------------------------------------------------------------
  with sub_manual:
    st.markdown("#### Etapas y Condiciones Generales del TEG")
    st.markdown(
        "El Trabajo Especial de Grado (TEG) demuestra la capacidad analítica,"
        " operativa y de investigación del participante para aportar soluciones"
        " al Sistema Público Nacional de Salud (SPNS). Se rige por las **Normas"
        " APA (última edición)** y se divide en **dos (2) etapas**:"
    )

    c_et1, c_et2 = st.columns(2)
    with c_et1:
      st.info(
          "**1. Proyecto de TEG**\n\n"
          "- **Extensión:** Entre **40 y 50 páginas** (incluyendo preliminares y referencias).\n"
          "- **Redacción:** En **tiempo futuro** y tercera persona.\n"
          "- **Alcance:** Desarrolla hasta el **Capítulo III (Marco Metodológico)**."
      )
    with c_et2:
      st.success(
          "**2. Trabajo Especial de Grado (Final)**\n\n"
          "- **Requisito:** Haber aprobado el Proyecto y la totalidad de las unidades curriculares.\n"
          "- **Redacción:** En **tiempo pasado** y tercera persona.\n"
          "- **Alcance:** Añade el **Capítulo IV (Resultados)** y el **Capítulo V (Conclusiones y Recomendaciones)**."
      )

    st.markdown(
        "- **Participación:** Individual o colectiva (**máximo 2 integrantes**,"
        " previa solicitud escrita y justificada ante la Coordinación del"
        " PNFA).\n"
        "- **Tutor(a):** Docente ordinario, contratado o jubilado (de la UCS o"
        " externo) con grado académico igual o superior al que se opta. Requiere"
        " consignar CV resumido, copia de cédula, título de postgrado y"
        " **Carta de Aceptación (Anexo N° 1)**."
    )

    st.markdown("#### Estructura Capitular Obligatoria")

    with st.expander("📌 Páginas Preliminares e Introducción", expanded=True):
      st.markdown(
          "- **Portada y Contraportada (Anexo N° 2):** Membrete oficial UCS,"
          " Núcleo, Centro de Formación, título del trabajo, grado a optar,"
          " autor(a), tutor(a), lugar y fecha.\n"
          "- **Cartas y Actas:** Acta de Aceptación del Comité de Bioética"
          " (Anexo N° 3), Carta de Aceptación del Tutor (Anexo N° 1), Carta de"
          " Autorización de Presentación del Tutor (Anexo N° 4 u 8) y Acta de"
          " Valoración (Anexo N° 6 o 9).\n"
          "- **Índices:** Índice General, Lista de Tablas, Lista de Gráficos y"
          " Lista de Figuras.\n"
          "- **Resumen (Anexo N° 7 / 10):** Máximo **250 palabras** para el"
          " Proyecto (futuro) y **300 palabras** para el TEG Final (pasado)."
          " Incluye de **3 a 5 palabras clave**.\n"
          "- **Introducción:** Máximo **3 páginas**. Ubica la temática, área y"
          " línea de investigación (MPPS/UCS), propósito, postura teórica,"
          " diseño metodológico y estructura de capítulos."
      )

    with st.expander("📌 Capítulo I: El Problema (~10 páginas)"):
      st.markdown(
          "- **Contextualización y delimitación:** De lo mundial y regional"
          " hasta lo local (Estado, Municipio o **ASIC** donde se ejecuta la"
          " investigación).\n"
          "- **Formulación e Interrogantes:** Deben guardar relación directa"
          " con los objetivos específicos.\n"
          "- **Objetivos:** **1 Objetivo General** y hasta **3 a 5 Objetivos"
          " Específicos**.\n"
          "- **Justificación:** Importancia académica, social, profesional y"
          " tecnológica, cerrando con la **línea de investigación** del PNFA."
      )

    with st.expander("📌 Capítulo II: Marco Teórico / Referencial"):
      st.markdown(
          "- **Antecedentes:** De **3 a 5 estudios** nacionales e"
          " internacionales (preferiblemente de los **últimos 5 años**),"
          " detallando autor, año, objetivo, metodología, resultados y aporte al"
          " estudio.\n"
          "- **Bases Teóricas:** Teorías y conceptos que sustentan la"
          " investigación.\n"
          "- **Sistema de Variables / Categorías:** Definición conceptual y"
          " operacionalización.\n"
          "- **Normas Éticas y Bioéticas:** Principios éticos aplicados en"
          " salud y consentimiento informado.\n"
          "- **Bases Legales:** Constitución, leyes, reglamentos y normas"
          " técnicas vigentes."
      )

    with st.expander("📌 Capítulo III: Marco Metodológico"):
      st.markdown(
          "- **Enfoque y Diseño:** Tipo de investigación (Documental, De Campo,"
          " Experimental o Emergente) y postura paradigmática.\n"
          "- **Población y Muestra / Informantes Clave:** Criterios de"
          " inclusión/exclusión y tipo de muestreo.\n"
          "- **Técnicas e Instrumentos:** Encuesta, observación, entrevista,"
          " revisión documental (especificando fármacos/productos con nombre"
          " genérico, dosis y vía si aplica).\n"
          "- **Validez y Confiabilidad:** Juicio de expertos y coeficiente"
          " estadístico (entre 0 y 1).\n"
          "- **Operacionalización de Variables** (Definición, Dimensiones,"
          " Indicadores, Ítems) o **Matriz de Categorización** (Categorías,"
          " Subcategorías, Códigos)."
      )

    with st.expander("📌 Capítulos IV y V (Exclusivos del TEG Final)"):
      st.markdown(
          "- **Capítulo IV (Presentación y Análisis de Resultados):** Tablas y"
          " gráficos procesados estadísticamente, con su interpretación y"
          " análisis en función de los objetivos e interrogantes.\n"
          "- **Capítulo V (Conclusiones y Recomendaciones):** Respuesta directa"
          " a cada objetivo, deducciones, limitaciones encontradas y"
          " sugerencias factibles para fortalecer los servicios de salud y el"
          " Buen Vivir.\n"
          "- **Referencias y Anexos:** Todas las citas en texto deben aparecer"
          " en las referencias (Normas APA). Anexos: instrumentos,"
          " consentimiento informado, aval bioético, etc."
      )

  # ------------------------------------------------------------------------------
  # 2. CÓMO HACER LAS DIAPOSITIVAS (diapositivas_teg.docx / Anexo N° 15)
  # ------------------------------------------------------------------------------
  with sub_diapos:
    st.markdown(
        "#### Lineamientos Oficiales para la Presentación Oral (Anexo N° 15)"
    )
    st.warning(
        "⚠️ **Regla Institucional Obligatoria:** Se debe mantener el **cintillo"
        " oficial de la UCS** en la parte superior de **TODAS las láminas**."
    )

    col_estilo1, col_estilo2 = st.columns(2)
    with col_estilo1:
      st.markdown("**🎨 Diseño y Formato Visual:**")
      st.markdown(
          "- **Fondo claro:** Utilizar preferiblemente **fondo blanco** para"
          " máxima legibilidad.\n"
          "- **Uniformidad:** Conservar el mismo encabezado, gama de colores,"
          " tipografía y estilo en todas las diapositivas."
      )
    with col_estilo2:
      st.markdown("**🔤 Tipografía y Recursos:**")
      st.markdown(
          "- **Tamaño de fuente:** Mínimo **28 puntos para títulos** y **24"
          " puntos para párrafos**.\n"
          "- **Recursos:** Evitar el exceso de animaciones y sonidos; emplear"
          " gráficos claros que faciliten la lectura de los resultados."
      )

    st.markdown("#### 🗂️ Estructura Lámina por Lámina")

    laminas = [
        (
            "Lámina 1: Portada",
            "Cintillo/membrete oficial UCS, Núcleo y Centro de Formación, Título"
            " del TEG (centrado y en MAYÚSCULAS), grado académico a optar,"
            " Autor(a) y Tutor(a) alineados a la derecha, y fecha centrada.",
        ),
        (
            "Lámina 2: Introducción",
            "Breve reseña de la temática, antecedentes, justificación e"
            " importancia, línea de investigación (MPPS/UCS), propósito general,"
            " postura teórica y enunciado de los aspectos a exponer (1 lámina).",
        ),
        (
            "Lámina 3: Resumen del Trabajo",
            "Síntesis de la temática, área y línea de investigación, referentes"
            " teóricos, objetivo principal y recorrido metodológico (1 lámina).",
        ),
        (
            "Láminas 4, 5 y 6: Marco Referencial, Legal y Bioético",
            "- **Antecedentes (1 lámina):** Estudios relevantes nacionales e"
            " internacionales (autor, año, objetivo, metodología, resultados y"
            " relación con la investigación).\n"
            "- **Bases Teóricas y Legales (máx. 1 lámina):** Sustento teórico,"
            " leyes, reglamentos y normas técnicas.\n"
            "- **Bases Éticas y Bioéticas (máx. 1 lámina):** Principios éticos"
            " aplicados y aval del Comité de Bioética.",
        ),
        (
            "Lámina 7: Marco Metodológico",
            "Área y tipo de diseño, población/muestra o informantes clave,"
            " criterios de inclusión/exclusión, procedimientos, técnicas,"
            " instrumentos, aspectos bioéticos y tipo de análisis (1 lámina).",
        ),
        (
            "Láminas 8, 9 y 10: Resultados y Análisis",
            "Resultados procesados (tabulados y/o graficados) por ítem/objetivo"
            " con su interpretación y análisis frente a las interrogantes (3"
            " láminas).",
        ),
        (
            "Lámina 11: Conclusiones",
            "Respuesta al objeto de estudio, verificación del logro de los"
            " objetivos, resolución de interrogantes, deducciones principales y"
            " limitaciones confrontadas (1 lámina).",
        ),
        (
            "Lámina 12: Recomendaciones",
            "Sugerencias concretas derivadas de los resultados para fortalecer"
            " los servicios de salud, el Buen Vivir y superar las limitaciones"
            " del estudio (1 lámina).",
        ),
    ]

    for titulo_lam, detalle_lam in laminas:
      with st.container(border=True):
        st.markdown(f"**{titulo_lam}**")
        st.markdown(detalle_lam)

    st.caption(
        "*Nota: En los Trabajos de Grado de Maestría se incluyen hasta 3"
        " láminas adicionales para presentar la Propuesta.*"
    )

  # ------------------------------------------------------------------------------
  # 3. CONSIGNACIÓN, PLAZOS Y CRITERIOS DEL JURADO
  # ------------------------------------------------------------------------------
  with sub_tramites:
    st.markdown("#### ⏱️ Proceso de Consignación y Plazos")
    st.markdown(
        "1. **Entrega Digital:** Consignar el TEG en **formato PDF no"
        " encriptado** ante la Coordinación Académica del PNFA, junto con la"
        " **Carta de Autorización firmada por el Tutor(a)**.\n"
        "2. **Revisión por el Jurado:** El jurado (3 miembros: Tutor + 2"
        " especialistas) cuenta con **15 días hábiles** para emitir su"
        " veredicto y observaciones escritas.\n"
        "3. **Incorporación de Observaciones:** El participante dispone de"
        " **15 días hábiles** para corregir y reenviar el PDF.\n"
        "4. **Defensa Pública:** Se realiza dentro de los **15 días hábiles**"
        " siguientes a la entrega corregida (plazo máximo total de aprobación:"
        " **1 año** tras culminar las unidades curriculares)."
    )

    st.markdown("#### ✅ Criterios de Evaluación del Jurado (Anexo N° 12)")
    c_eval1, c_eval2 = st.columns(2)
    with c_eval1:
      st.markdown("**Evaluación del Documento Escrito:**")
      st.markdown(
          "- Coherencia entre título, interrogantes y objetivos.\n"
          "- Claridad del objeto de estudio y aportes institucionales/sociales.\n"
          "- Vigencia de antecedentes y sustento teórico.\n"
          "- Correspondencia de fundamentos bioéticos y legales.\n"
          "- Coherencia entre objetivos, variables, tablas y gráficos.\n"
          "- Conclusiones/recomendaciones alineadas y referencias bajo Normas APA."
      )
    with c_eval2:
      st.markdown("**Evaluación de la Sustentación Oral:**")
      st.markdown(
          "- **Dominio del tema** durante la exposición y ciclo de preguntas.\n"
          "- **Uso adecuado de recursos audiovisuales** (cumpliendo Anexo N° 15).\n"
          "- **Lenguaje técnico y científico** acorde al nivel de postgrado."
      )


def render():
  inyectar_estilos_pubmed()

  if not db_conectada:
    st.error("⚠️ No hay conexión con la base de datos MongoDB.")
    return

  db = get_db()
  teg_col = db["trabajos_especiales"]

  # Banner Superior Estilo PubMed
  st.markdown(
      """
      <div class="pubmed-header">
          <h1>📚 Repositorio Institucional de Trabajos Especiales de Grado (TEG)</h1>
          <p>Motor de búsqueda académica, indexación científica, guía metodológica y consulta abierta para egresados e investigadores.</p>
      </div>
      """,
      unsafe_allow_html=True,
  )

  # Pestañas principales: Buscador + Guía Oficial TEG y Diapositivas
  tab_buscador, tab_guia_teg = st.tabs([
      "🔎 Buscador Científico & Catálogo",
      "🎓 Guía: Elaboración del TEG y Diapositivas",
  ])

  # ==============================================================================
  # PESTAÑA 1: BUSCADOR ESTILO PUBMED + CARRUSELES
  # ==============================================================================
  with tab_buscador:
    # Obtener valores únicos para filtros facetados
    todos_docs = list(teg_col.find({}, {"_id": 0}))
    carreras_unicas = sorted(
        list({
            str(d.get("carrera", "")).strip()
            for d in todos_docs
            if d.get("carrera")
        })
    )
    especialidades_unicas = sorted(
        list({
            str(d.get("especialidad", "")).strip()
            for d in todos_docs
            if d.get("especialidad")
        })
    )
    anios_unicos = sorted(
        list({
            str(d.get("anio", "")).strip() for d in todos_docs if d.get("anio")
        }),
        reverse=True,
    )

    # Barra principal de búsqueda estilo PubMed
    with st.container(border=True):
      col_q, col_btn = st.columns([5, 1])
      with col_q:
        query_texto = st.text_input(
            "Buscar por título, palabras clave, tema o autor",
            placeholder=(
                "Ej: Rehabilitación neuromuscular, Fisioterapia respiratoria,"
                " Pérez..."
            ),
            label_visibility="collapsed",
        )
      with col_btn:
        buscar_click = st.button(
            "🔍 Buscar", type="primary", use_container_width=True
        )

      # Filtros Facetados (Año, Carrera, Especialidad)
      col_f1, col_f2, col_f3, col_f4 = st.columns([1.2, 1.5, 1.5, 1])
      with col_f1:
        filtro_anio = st.selectbox(
            "Año de publicación", ["Todos"] + anios_unicos
        )
      with col_f2:
        filtro_carrera = st.selectbox(
            "Carrera / PNF", ["Todas"] + carreras_unicas
        )
      with col_f3:
        filtro_especialidad = st.selectbox(
            "Especialidad / Línea", ["Todas"] + especialidades_unicas
        )
      with col_f4:
        orden_por = st.selectbox(
            "Ordenar por",
            ["Más relevantes (Votos)", "Más recientes (Año)", "Título (A-Z)"],
        )

    hay_filtro_activo = bool(
        query_texto.strip()
        or filtro_anio != "Todos"
        or filtro_carrera != "Todas"
        or filtro_especialidad != "Todas"
    )

    # Si no hay búsqueda activa, mostramos los Carruseles Destacados primero
    if not hay_filtro_activo:
      mas_buscados = list(
          teg_col.find({}, {"_id": 0}).sort("votos", -1).limit(9)
      )
      mas_nuevos = list(
          teg_col.find({}, {"_id": 0}).sort([("anio", -1), ("id", -1)]).limit(9)
      )

      render_carrusel(
          "Trabajos Más Buscados y Valorados", "🔥", mas_buscados, "populares"
      )
      st.markdown("---")
      render_carrusel(
          "Incorporaciones Más Recientes", "🆕", mas_nuevos, "nuevos"
      )
      st.markdown("---")

    # Construcción dinámica de la consulta MongoDB
    mongo_query = {}
    and_conditions = []

    if query_texto.strip():
      # Búsqueda por palabras específicas en título, descripción (tema) y autor
      palabras = [p.strip() for p in query_texto.strip().split() if p.strip()]
      for palabra in palabras:
        and_conditions.append({
            "$or": [
                {"titulo": {"$regex": palabra, "$options": "i"}},
                {"descripcion": {"$regex": palabra, "$options": "i"}},
                {"autor": {"$regex": palabra, "$options": "i"}},
                {"especialidad": {"$regex": palabra, "$options": "i"}},
            ]
        })

    if filtro_anio != "Todos":
      and_conditions.append({
          "$or": [
              {"anio": filtro_anio},
              {
                  "anio": (
                      int(filtro_anio) if filtro_anio.isdigit() else filtro_anio
                  )
              },
          ]
      })

    if filtro_carrera != "Todas":
      and_conditions.append({"carrera": filtro_carrera})

    if filtro_especialidad != "Todas":
      and_conditions.append({"especialidad": filtro_especialidad})

    if and_conditions:
      mongo_query["$and"] = and_conditions

    # Ordenamiento
    sort_criteria = [("votos", -1)]
    if orden_por == "Más recientes (Año)":
      sort_criteria = [("anio", -1)]
    elif orden_por == "Título (A-Z)":
      sort_criteria = [("titulo", 1)]

    resultados = list(teg_col.find(mongo_query, {"_id": 0}).sort(sort_criteria))

    # Registrar métrica de búsqueda si el usuario presionó Buscar o aplicó filtros
    if buscar_click or hay_filtro_activo:
      registrar_busqueda_analitica(
          db,
          {
              "query": query_texto.strip(),
              "carrera": filtro_carrera,
              "especialidad": filtro_especialidad,
              "anio": filtro_anio,
          },
          len(resultados),
      )

    # Mostrar listado de resultados estilo PubMed
    st.subheader(f"📑 Resultados en el Índice ({len(resultados)} documentos)")

    if not resultados:
      st.warning(
          "No se encontraron trabajos especiales de grado con los criterios"
          " seleccionados."
      )
    else:
      for idx, item in enumerate(resultados):
        teg_id = item.get("id", f"TEG-{idx}")
        titulo = item.get("titulo", "Sin título")
        autor = item.get("autor", "Autor desconocido")
        anio = item.get("anio", "S/A")
        carrera = item.get("carrera", "N/A")
        especialidad = item.get("especialidad", "General")
        descripcion = item.get("descripcion", "Sin resumen disponible.")
        votos = int(item.get("votos", 0))
        url_doc = str(item.get("url_documento", "")).strip()
        url_img = str(item.get("url_imagen", "")).strip()

        with st.container(border=True):
          col_img, col_info, col_acciones = st.columns([1.2, 5.5, 1.8])

          with col_img:
            if url_img and url_img.startswith("http"):
              st.image(url_img, use_container_width=True)
            else:
              st.markdown(
                  "<div"
                  " style='height:125px;background:#f1f5f9;border:1px solid"
                  " #cbd5e1;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:2.2rem;'>📄</div>",
                  unsafe_allow_html=True,
              )
            st.caption(f"ID: `{teg_id}`")

          with col_info:
            st.markdown(
                f"<div class='teg-title'>{titulo}</div>", unsafe_allow_html=True
            )
            st.markdown(
                f"<div class='teg-meta'><b>Autor(es):</b> {autor}"
                f" &nbsp;|&nbsp; <b>Año:</b> {anio}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span class='teg-badge'>🏛️ {carrera}</span>"
                f"<span class='teg-badge'>🔬 {especialidad}</span>",
                unsafe_allow_html=True,
            )
            with st.expander(
                "📖 Ver Resumen / Abstract",
                expanded=(idx < 2 and hay_filtro_activo),
            ):
              st.write(descripcion)

          with col_acciones:
            st.metric("Relevancia / Votos", votos)

            # Botón de voto (incrementa relevancia y popularidad)
            voto_key = f"votado_{teg_id}"
            ya_voto = st.session_state.get(voto_key, False)
            if st.button(
                "✅ Votado" if ya_voto else "👍 Votar útil",
                key=f"btn_vote_{teg_id}_{idx}",
                disabled=ya_voto,
                use_container_width=True,
            ):
              teg_col.update_one({"id": teg_id}, {"$inc": {"votos": 1}})
              st.session_state[voto_key] = True
              st.rerun()

            if url_doc and url_doc.startswith("http"):
              st.link_button(
                  "📥 Consultar PDF",
                  url_doc,
                  type="primary",
                  use_container_width=True,
              )
            else:
              st.button(
                  "Sin enlace PDF",
                  disabled=True,
                  key=f"nodoc_{teg_id}_{idx}",
                  use_container_width=True,
              )

  # ==============================================================================
  # PESTAÑA 2: GUÍA DE ELABORACIÓN DEL TEG Y DIAPOSITIVAS (GOOGLE DRIVE)
  # ==============================================================================
  with tab_guia_teg:
    render_guia_teg()
