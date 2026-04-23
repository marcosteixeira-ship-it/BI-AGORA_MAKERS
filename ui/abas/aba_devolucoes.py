"""
ui/abas/aba_devolucoes.py
Conteúdo da aba Devoluções (ESC).
"""

import streamlit as st
import pandas as pd
from modulos.esc.config import (
    COLUNAS, COL_Q_CONCATENAR, COL_T_IMPOSTOS,
    COL_U_CPV, COL_V_MES, COL_W_REPR,
)
from ui.componentes.cards import titulo_secao


def renderizar_empresa(df: pd.DataFrame, empresa: str, n_linhas: int) -> None:
    """Renderiza aba ESC de uma empresa."""
    if df.empty:
        st.warning(f"Sem dados de devoluções para {empresa}.")
        return

    sufixo = "omp" if "My City" in empresa else "mtc"
    col_vt = "Valor total"

    # ── Métricas ──────────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Linhas",        f"{len(df):,}")
    m2.metric("Valor Devolvido", f"R$ {df[col_vt].sum():,.2f}" if col_vt in df else "—")
    m3.metric("Impostos Dev.",  f"R$ {df[COL_T_IMPOSTOS].sum(skipna=True):,.2f}" if COL_T_IMPOSTOS in df else "—")
    m4.metric("CPV Dev.",       f"R$ {df[COL_U_CPV].sum(skipna=True):,.2f}" if COL_U_CPV in df else "—")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabela principal ──────────────────────────────────────────────────────
    cols = COLUNAS[sufixo]
    colunas_exib = [c for c in [
        cols["data_entrada"],
        cols["nota_entrada"],
        cols["nota_dev"],
        cols["item"],
        cols["descricao"],
        cols["qtde"],
        col_vt,
        COL_Q_CONCATENAR,
        COL_T_IMPOSTOS,
        COL_U_CPV,
        COL_V_MES,
        COL_W_REPR,
    ] if c in df.columns]

    titulo_secao(f"📋 Devoluções — {empresa} ({len(df):,} linhas)")
    st.dataframe(
        df[colunas_exib].head(n_linhas),
        use_container_width=True,
        hide_index=True,
        column_config={
            COL_Q_CONCATENAR: st.column_config.TextColumn("Q — Chave Nota-Item"),
            COL_T_IMPOSTOS:   st.column_config.NumberColumn("T — Impostos Dev.", format="R$ %.2f"),
            COL_U_CPV:        st.column_config.NumberColumn("U — CPV Dev.",       format="R$ %.2f"),
            COL_V_MES:        st.column_config.TextColumn("V — Mês"),
            COL_W_REPR:       st.column_config.TextColumn("W — Representante"),
        },
    )

    # ── Resumo por mês ────────────────────────────────────────────────────────
    if COL_V_MES in df.columns and col_vt in df.columns:
        titulo_secao("📅 Devoluções por Mês")
        grp = (
            df.groupby(COL_V_MES)
            .agg(
                Qtde      = (cols["qtde"],    "sum"),
                Valor_Dev = (col_vt,          "sum"),
                Impostos  = (COL_T_IMPOSTOS,  "sum"),
                CPV_Dev   = (COL_U_CPV,       "sum"),
                Notas     = (cols["nota_dev"], "nunique"),
            )
            .reset_index()
        )
        grp.columns = ["Mês", "Qtde", "Valor Devolvido", "Impostos Dev.", "CPV Dev.", "Notas"]
        st.dataframe(grp, use_container_width=True, hide_index=True)


def renderizar_consolidado(df_omp: pd.DataFrame, df_mtc: pd.DataFrame) -> None:
    """Renderiza visão consolidada OMP + MTC."""
    frames = [df for df in [df_omp, df_mtc] if not df.empty]
    if not frames:
        st.warning("Nenhum dado de devoluções carregado.")
        return

    col_vt = "Valor total"
    total_dev = sum(df[col_vt].sum() for df in frames if col_vt in df)
    total_imp = sum(df[COL_T_IMPOSTOS].sum(skipna=True) for df in frames if COL_T_IMPOSTOS in df)
    total_cpv = sum(df[COL_U_CPV].sum(skipna=True) for df in frames if COL_U_CPV in df)

    c1, c2, c3 = st.columns(3)
    c1.metric("Valor Total Devolvido", f"R$ {total_dev:,.2f}")
    c2.metric("Impostos Devolvidos",   f"R$ {total_imp:,.2f}")
    c3.metric("CPV Devolvido",         f"R$ {total_cpv:,.2f}")
