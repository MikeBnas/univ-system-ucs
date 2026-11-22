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
  """Guarda métricas de búsqueda en MongoDB para alimentar los tableros de Power BI."""
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
    if st.button("◀", key=f"prev_{key_prefix}", disabled=(st.session_state[state_key] == 0)):
      st.session_state[state_key] -= 1
      st.rerun()

  with col_next:
    st.write("")
    st.write("")
    if st.button("▶", key=f"next_{key_prefix}", disabled=(st.session_state[state_key] >= max_idx)):
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
                "<div style='height:110px;background:#e2e8f0;border-radius:6px;display:flex;align-items:center;justify-content:center;color:#475569;font-size:2rem;'>📘</div>",
                unsafe_allow_html=True,
            )

          st.markdown(
              f"<span class='carousel-tag'>{doc.get('carrera', 'General')} • {doc.get('anio', 'S/A')}</span>",
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


def render():
  inyectar_estilos_pubmed()

  if not db_conectada:
    st.error("⚠️ No hay conexión con la base de datos MongoDB.")
    return

  db = get_db()
  teg_col = db["trabajos_especiales"]
  rol_actual = st.session_state.get("rol", "Estudiante")

  # Banner Superior Estilo PubMed
  st.markdown(
      """
      <div class="pubmed-header">
          <h1>📚 Repositorio Institucional de Trabajos Especiales de Grado (TEG)</h1>
          <p>Motor de búsqueda académica, indexación científica y consulta abierta para egresados e investigadores.</p>
      </div>
      """,
      unsafe_allow_html=True,
  )

  # Pestañas principales: Buscador + Analítica Power BI
  tab_buscador, tab_powerbi = st.tabs([
      "🔎 Buscador Científico & Catálogo",
      "📊 Analítica de Índices Más Buscados (Power BI)",
  ])

  # ==============================================================================
  # PESTAÑA 1: BUSCADOR ESTILO PUBMED + CARRUSELES
  # ==============================================================================
  with tab_buscador:
    # Obtener valores únicos para filtros facetados
    todos_docs = list(teg_col.find({}, {"_id": 0}))
    carreras_unicas = sorted(list({str(d.get("carrera", "")).strip() for d in todos_docs if d.get("carrera")}))
    especialidades_unicas = sorted(list({str(d.get("especialidad", "")).strip() for d in todos_docs if d.get("especialidad")}))
    anios_unicos = sorted(list({str(d.get("anio", "")).strip() for d in todos_docs if d.get("anio")}), reverse=True)

    # Barra principal de búsqueda estilo PubMed
    with st.container(border=True):
      col_q, col_btn = st.columns([5, 1])
      with col_q:
        query_texto = st.text_input(
            "Buscar por título, palabras clave, tema o autor",
            placeholder="Ej: Rehabilitación neuromuscular, Fisioterapia respiratoria, Pérez...",
            label_visibility="collapsed",
        )
      with col_btn:
        buscar_click = st.button("🔍 Buscar", type="primary", use_container_width=True)

      # Filtros Facetados (Año, Carrera, Especialidad)
      col_f1, col_f2, col_f3, col_f4 = st.columns([1.2, 1.5, 1.5, 1])
      with col_f1:
        filtro_anio = st.selectbox("Año de publicación", ["Todos"] + anios_unicos)
      with col_f2:
        filtro_carrera = st.selectbox("Carrera / PNF", ["Todas"] + carreras_unicas)
      with col_f3:
        filtro_especialidad = st.selectbox("Especialidad / Línea", ["Todas"] + especialidades_unicas)
      with col_f4:
        orden_por = st.selectbox("Ordenar por", ["Más relevantes (Votos)", "Más recientes (Año)", "Título (A-Z)"])

    hay_filtro_activo = bool(
        query_texto.strip()
        or filtro_anio != "Todos"
        or filtro_carrera != "Todas"
        or filtro_especialidad != "Todas"
    )

    # Si no hay búsqueda activa, mostramos los Carruseles Destacados primero
    if not hay_filtro_activo:
      mas_buscados = list(teg_col.find({}, {"_id": 0}).sort("votos", -1).limit(9))
      mas_nuevos = list(teg_col.find({}, {"_id": 0}).sort([("anio", -1), ("id", -1)]).limit(9))

      render_carrusel("Trabajos Más Buscados y Valorados", "🔥", mas_buscados, "populares")
      st.markdown("---")
      render_carrusel("Incorporaciones Más Recientes", "🆕", mas_nuevos, "nuevos")
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
      and_conditions.append({"$or": [{"anio": filtro_anio}, {"anio": int(filtro_anio) if filtro_anio.isdigit() else filtro_anio}]})

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
      st.warning("No se encontraron trabajos especiales de grado con los criterios seleccionados.")
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
                  "<div style='height:125px;background:#f1f5f9;border:1px solid #cbd5e1;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:2.2rem;'>📄</div>",
                  unsafe_allow_html=True,
              )
            st.caption(f"ID: `{teg_id}`")

          with col_info:
            st.markdown(f"<div class='teg-title'>{titulo}</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='teg-meta'><b>Autor(es):</b> {autor} &nbsp;|&nbsp; <b>Año:</b> {anio}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span class='teg-badge'>🏛️ {carrera}</span>"
                f"<span class='teg-badge'>🔬 {especialidad}</span>",
                unsafe_allow_html=True,
            )
            with st.expander("📖 Ver Resumen / Abstract", expanded=(idx < 2 and hay_filtro_activo)):
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
              st.link_button("📥 Consultar PDF", url_doc, type="primary", use_container_width=True)
            else:
              st.button("Sin enlace PDF", disabled=True, key=f"nodoc_{teg_id}_{idx}", use_container_width=True)

  # ==============================================================================
  # PESTAÑA 2: INTEGRACIÓN POWER BI + MÉTRICAS NATIVAS DE RESPALDO
  # ==============================================================================
  with tab_powerbi:
    st.markdown("### 📊 Inteligencia Académica: Índices y Temas Más Buscados")
    st.caption("Visualización interactiva conectada a Microsoft Power BI y telemetría en tiempo real.")

    # Leer URL de Power BI desde secrets o permitir configurarla al Administrador
    powerbi_url = ""
    if "powerbi" in st.secrets and "teg_report_url" in st.secrets["powerbi"]:
      powerbi_url = st.secrets["powerbi"]["teg_report_url"]

    if rol_actual == "Administrador":
      with st.expander("⚙️ Configurar enlace de publicación Power BI (Publish to Web)", expanded=not bool(powerbi_url)):
        nueva_url_pbi = st.text_input(
            "URL pública de Power BI (Iframe Embed URL)",
            value=powerbi_url,
            placeholder="https://app.powerbi.com/view?r=eyJrIjoi...",
            help="En Power BI Service: Archivo > Insertar informe > Publicar en la web (público).",
        )
        if nueva_url_pbi:
          powerbi_url = nueva_url_pbi

    if powerbi_url and powerbi_url.startswith("http"):
      st.components.v1.iframe(powerbi_url, height=620, scrolling=True)
    else:
      st.info(
          "💡 **Modo Analítico Integrado:** Configura tu URL de `Power BI (Publish to Web)` en `.streamlit/secrets.toml` bajo `[powerbi] teg_report_url` para renderizar el dashboard corporativo aquí. Mientras tanto, visualiza los indicadores en vivo desde MongoDB:"
      )

    # Analítica en vivo desde MongoDB (también sirve para exportar dataset hacia Power BI)
    st.markdown("---")
    col_g1, col_g2 = st.columns(2)

    with col_g1:
      st.markdown("#### 🏆 Top Carreras / Especialidades por Votos")
      if todos_docs:
        df_teg = pd.DataFrame(todos_docs)
        df_teg["votos"] = pd.to_numeric(df_teg.get("votos", 0), errors="coerce").fillna(0)
        resumen_carrera = df_teg.groupby("carrera")["votos"].sum().sort_values(ascending=False)
        st.bar_chart(resumen_carrera)
      else:
        st.caption("Sin datos cargados en `trabajos_especiales`.")

    with col_g2:
      st.markdown("#### 🔍 Términos y Carreras Más Buscados por Usuarios")
      busquedas_docs = list(db["analitica_biblioteca"].find({}, {"_id": 0}))
      if busquedas_docs:
        df_busq = pd.DataFrame(busquedas_docs)
        top_carreras_busq = df_busq[df_busq["carrera"] != "Todas"]["carrera"].value_counts()
        if not top_carreras_busq.empty:
          st.bar_chart(top_carreras_busq)
        else:
          top_terms = df_busq[df_busq["termino_busqueda"] != ""]["termino_busqueda"].value_counts().head(10)
          st.bar_chart(top_terms)
      else:
        st.caption("Realiza búsquedas en el catálogo para generar telemetría.")

    # Exportación directa para conectar con Power BI Desktop
    if rol_actual == "Administrador" and todos_docs:
      st.markdown("---")
      df_export = pd.DataFrame(todos_docs)
      csv_data = df_export.to_csv(index=False).encode("utf-8")
      st.download_button(
          label="📥 Descargar Dataset Consolidado (CSV) para Power BI Desktop",
          data=csv_data,
          file_name=f"dataset_teg_powerbi_{datetime.now().strftime('%Y%m%d')}.csv",
          mime="text/csv",
      )
