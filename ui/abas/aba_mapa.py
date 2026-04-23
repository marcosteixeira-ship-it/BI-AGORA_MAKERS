"""
ui/abas/aba_mapa.py
Aba de mapa geográfico: bolhas por estado (América do Sul) e heatmaps regionais.
"""
import streamlit as st
import pandas as pd
from ui.charts import mapa_brasil, heatmap_estado_mes, heatmap_estado_produto
from ui.componentes.cards import titulo_secao

_EMPRESAS = ["Consolidado", "My City", "Metalco"]
_CP = {"My City": "#1A56DB", "Metalco": "#057A55", "Consolidado": "#7C3AED"}


def renderizar(df_omp: pd.DataFrame, df_mtc: pd.DataFrame,
               df_cons: pd.DataFrame) -> None:
    if df_cons.empty and df_omp.empty and df_mtc.empty:
        st.warning("Sem dados para gerar o mapa geográfico.")
        return

    empresa = st.radio("Empresa", _EMPRESAS, horizontal=True, key="mapa_empresa")
    df = {"My City": df_omp, "Metalco": df_mtc, "Consolidado": df_cons}[empresa]
    cp = _CP[empresa]

    if df.empty:
        st.warning(f"Sem dados para {empresa} no período selecionado.")
        return

    if "Estado" not in df.columns:
        st.info("Coluna 'Estado' não encontrada nos dados de faturamento.")
        return

    # ── Mapa de bolhas ────────────────────────────────────────────────────────
    titulo_secao("🌎 Distribuição Geográfica — América do Sul")
    st.caption(
        "Tamanho da bolha = volume de faturamento · "
        "Cor = Margem% · Use scroll para zoom"
    )
    fig = mapa_brasil(df, cp)
    if fig.data:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Não foi possível gerar o mapa — verifique a coluna 'Estado'.")

    # ── Heatmaps regionais ────────────────────────────────────────────────────
    titulo_secao("🗺️ Análise Regional Detalhada")
    tab_em, tab_ep = st.tabs(["Estado × Mês", "Estado × Produto"])

    with tab_em:
        fig = heatmap_estado_mes(df, cp)
        if fig.data:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Dados insuficientes para o heatmap Estado × Mês.")

    with tab_ep:
        fig = heatmap_estado_produto(df, cp)
        if fig.data:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Dados insuficientes para o heatmap Estado × Produto.")
