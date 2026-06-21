from __future__ import annotations

import pandas as pd
import streamlit as st

from biomedical_discovery.extraction import analyze_articles
from biomedical_discovery.graphing import build_relations, relation_rows, to_graphviz_dot
from biomedical_discovery.hypothesis import generate_hypotheses
from biomedical_discovery.pubmed import PubMedError, search_and_fetch
from biomedical_discovery.sample_data import SAMPLE_ARTICLES


st.set_page_config(
    page_title="Busqueda Bioedica",
    page_icon="B",
    layout="wide",
)

st.title("Busqueda Bioedica")
st.caption("Explorador de literatura publica para genes, sindromes, tratamientos y resultados.")

with st.sidebar:
    st.header("Busqueda")
    query = st.text_area(
        "Tema biomedico",
        value="genetic syndromes childhood leukemia treatment outcomes",
        height=90,
    )
    max_results = st.slider("Articulos maximos", min_value=3, max_value=50, value=12, step=1)
    email = st.text_input("Email NCBI opcional", placeholder="tu@email.com")
    use_sample = st.toggle("Usar datos demo sin internet", value=True)
    run_search = st.button("Analizar", type="primary", use_container_width=True)

st.info(
    "Uso investigativo: organiza literatura publica y genera hipotesis para revision humana. "
    "No diagnostica ni recomienda tratamientos."
)

if "analyses" not in st.session_state:
    st.session_state.analyses = analyze_articles(SAMPLE_ARTICLES)

if run_search:
    if use_sample:
        articles = SAMPLE_ARTICLES
    else:
        try:
            with st.spinner("Consultando PubMed..."):
                articles = search_and_fetch(query, max_results=max_results, email=email or None)
        except PubMedError as exc:
            st.error(str(exc))
            articles = []

    if articles:
        st.session_state.analyses = analyze_articles(articles)
    else:
        st.warning("No se encontraron articulos para analizar.")

analyses = st.session_state.analyses
relations = build_relations(analyses)

summary_cols = st.columns(4)
summary_cols[0].metric("Articulos", len(analyses))
summary_cols[1].metric("Genes", len({gene for item in analyses for gene in item.genes}))
summary_cols[2].metric("Condiciones", len({disease for item in analyses for disease in item.diseases}))
summary_cols[3].metric("Relaciones", len(relation_rows(relations)))

tab_articles, tab_relations, tab_graph, tab_hypotheses = st.tabs(["Articulos", "Relaciones", "Grafo", "Hipotesis"])

with tab_articles:
    article_rows = []
    for analysis in analyses:
        article_rows.append(
            {
                "pmid": analysis.article.pmid,
                "year": analysis.article.year,
                "title": analysis.article.title,
                "genes": ", ".join(analysis.genes),
                "diseases": ", ".join(analysis.diseases),
                "treatments": ", ".join(analysis.treatments),
                "outcome_sentences": " | ".join(analysis.outcomes),
                "url": analysis.article.url,
            }
        )
    st.dataframe(pd.DataFrame(article_rows), use_container_width=True, hide_index=True)

with tab_relations:
    rows = relation_rows(relations)
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.warning("Todavia no hay relaciones detectadas.")

with tab_graph:
    if relations:
        st.graphviz_chart(to_graphviz_dot(relations), use_container_width=True)
    else:
        st.warning("Todavia no hay suficientes entidades para construir el grafo.")

with tab_hypotheses:
    hypotheses = generate_hypotheses(relations)
    if hypotheses:
        for index, hypothesis in enumerate(hypotheses, start=1):
            st.write(f"{index}. {hypothesis}")
    else:
        st.warning("No hay hipotesis generadas con los datos actuales.")
