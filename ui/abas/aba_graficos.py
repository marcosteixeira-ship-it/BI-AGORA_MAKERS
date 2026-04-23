"""
ui/abas/aba_graficos.py
Aba de análise visual: heatmaps de famílias, vendas semanais, treemap, clientes.
"""
import streamlit as st
import pandas as pd
from ui.charts import (
    heatmap_familia_mes, heatmap_semana_dia, treemap_grupos,
    top_clientes, scatter_fat_margem, fat_mensal, heatmap_margem_grupo,
)
from ui.componentes.cards import titulo_secao

_EMPRESAS = ["Consolidado", "My City", "Metalco"]
_CP = {"My City": "#1A56DB", "Metalco": "#057A55", "Consolidado": "#7C3AED"}


def renderizar(df_omp: pd.DataFrame, df_mtc: pd.DataFrame,
               df_cons: pd.DataFrame) -> None:
    if df_cons.empty and df_omp.empty and df_mtc.empty:
        st.warning("Sem dados de faturamento para gerar gráficos.")
        return

    empresa = st.radio("Empresa", _EMPRESAS, horizontal=True, key="grf_empresa")
    df = {"My City": df_omp, "Metalco": df_mtc, "Consolidado": df_cons}[empresa]
    cp = _CP[empresa]

    if df.empty:
        st.warning(f"Sem dados para {empresa} no período selecionado.")
        return

    # ── Mapas de calor ────────────────────────────────────────────────────────
    titulo_secao("🌡️ Mapas de Calor — Famílias de Produtos e Sazonalidade Semanal")
    c1, c2 = st.columns([3, 2], gap="medium")
    with c1:
        fig = heatmap_familia_mes(df, cp)
        if fig.data:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Coluna 'Família' não encontrada nos dados.")
    with c2:
        fig = heatmap_semana_dia(df, cp)
        if fig.data:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sem dados suficientes para o heatmap semanal.")

    # ── Faturamento mensal + Treemap ──────────────────────────────────────────
    titulo_secao("📊 Faturamento Mensal e Mix de Produtos")
    c3, c4 = st.columns([2, 3], gap="medium")
    with c3:
        fig = fat_mensal(df, cp)
        if fig.data:
            st.plotly_chart(fig, use_container_width=True)
    with c4:
        fig = treemap_grupos(df)
        if fig.data:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Coluna 'Grupo de itens' não encontrada.")

    # ── Margem por grupo ──────────────────────────────────────────────────────
    titulo_secao("💹 Margem% por Grupo de Produto × Mês")
    fig = heatmap_margem_grupo(df)
    if fig.data:
        st.plotly_chart(fig, use_container_width=True)

    # ── Clientes ──────────────────────────────────────────────────────────────
    titulo_secao("👥 Análise de Clientes")
    c5, c6 = st.columns(2, gap="medium")
    with c5:
        fig = top_clientes(df, cp)
        if fig.data:
            st.plotly_chart(fig, use_container_width=True)
    with c6:
        fig = scatter_fat_margem(df, cp)
        if fig.data:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sem dados de margem para o gráfico scatter.")
