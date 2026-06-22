"""
Dashboard COVID-19 (ES) — Exercício 5
Painel com: (a) série temporal de notificações, (b) mapa de calor por município,
(c) pirâmide etária dos óbitos, (d) top-5 comorbidades em óbitos.

Executar com: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from database_connector import BancoDeDados

st.set_page_config(
    page_title="Dashboard COVID-19 — ES",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# Conexão com o banco (cacheada — não reconecta a cada interação)
# ============================================================
@st.cache_resource
def get_db():
    return BancoDeDados()


def executar_query_do_arquivo(caminho_arquivo, db_connector):
    """Lê um arquivo .sql e retorna um DataFrame do Pandas."""
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        query = f.read()
    return db_connector.ler_tabela_query(query)


# Cacheia o resultado das queries por 10 minutos — evita bater no banco
# a cada interação do usuário com o painel (ex.: redimensionar a tela)
@st.cache_data(ttl=600)
def carregar_dados(caminho_sql):
    db = get_db()
    return executar_query_do_arquivo(caminho_sql, db)


# ============================================================
# Funções de plot (mesma lógica do notebook, retornando a figure
# em vez de chamar plt.show(), para o Streamlit poder renderizar)
# ============================================================
def fig_serie_temporal(df):
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df["data_completa"], df["total_notificacoes"], color="#3A86FF")
    ax.set_title("Série Temporal de Notificações")
    ax.set_xlabel("Data")
    ax.set_ylabel("Notificações")
    fig.tight_layout()
    return fig


def fig_mapa_calor(df):
    fig, ax = plt.subplots(figsize=(10, 8))
    pivot = df.pivot(index="municipio", columns="mes", values="total")
    sns.heatmap(pivot, annot=False, cmap="YlGnBu", ax=ax)
    ax.set_title("Mapa de Calor por Município")
    fig.tight_layout()
    return fig


def fig_piramide_etaria(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    df.set_index("faixa_etaria").plot(kind="barh", stacked=True, ax=ax)
    ax.set_title("Pirâmide Etária dos Óbitos")
    fig.tight_layout()
    return fig


def fig_top_comorbidades(df):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(df["comorbidade"], df["total"], color="salmon")
    ax.set_title("Top 5 Comorbidades em Óbitos")
    fig.tight_layout()
    return fig


# ============================================================
# Layout do dashboard
# ============================================================
st.title("📊 Dashboard COVID-19 — Espírito Santo")
st.caption("Dados do Data Warehouse `dw_covid` (modelo Floco de Neve)")

with st.spinner("Carregando dados do banco..."):
    df_serie = carregar_dados("sql/serie_temporal.sql")
    df_heatmap = carregar_dados("sql/mapa_de_calor.sql")
    df_piramide = carregar_dados("sql/piramide_etaria.sql")
    df_comorb = carregar_dados("sql/top_comorbidades.sql")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Série Temporal de Notificações")
    if df_serie.empty:
        st.warning("Sem dados retornados para esta consulta.")
    else:
        st.pyplot(fig_serie_temporal(df_serie))

with col2:
    st.subheader("Mapa de Calor por Município")
    if df_heatmap.empty:
        st.warning("Sem dados retornados para esta consulta.")
    else:
        st.pyplot(fig_mapa_calor(df_heatmap))

col3, col4 = st.columns(2)

with col3:
    st.subheader("Pirâmide Etária dos Óbitos")
    if df_piramide.empty:
        st.warning("Sem dados retornados para esta consulta.")
    else:
        st.pyplot(fig_piramide_etaria(df_piramide))

with col4:
    st.subheader("Top 5 Comorbidades em Óbitos")
    if df_comorb.empty:
        st.warning("Sem dados retornados para esta consulta.")
    else:
        st.pyplot(fig_top_comorbidades(df_comorb))

st.divider()
if st.button("🔄 Atualizar dados"):
    st.cache_data.clear()
    st.rerun()