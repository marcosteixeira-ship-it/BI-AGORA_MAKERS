"""
ui/componentes/cards.py
Componentes de card, badge e seção.
"""

import streamlit as st


def fmt_rs(v: float) -> str:
    return f"R$ {v:,.2f}"


def fmt_pct(v: float) -> str:
    return f"{v * 100:.1f}%"


def titulo_secao(texto: str) -> None:
    st.markdown(
        f'<div class="titulo-sec">{texto}</div>',
        unsafe_allow_html=True,
    )


def badge(valor: str) -> str:
    cls = "badge-sim" if valor.upper() == "SIM" else "badge-nao"
    return f'<span class="{cls}">{valor}</span>'


def linha_metricas_fat(df, colunas: dict) -> None:
    """
    Renderiza 3 linhas de métricas para aba FAT.
    colunas: dict com chaves dos COL_* necessários
    """
    from modulos.fat.config import (
        COL_QTDE_LIQUIDA, COL_RB, COL_IMPOSTOS, COL_RL,
        COL_CPV, COL_MARGEM, COLUNAS,
    )

    col_fat = COLUNAS["qtde_faturada"]

    # Linha 1 — Quantidades
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Qtde. Faturada",     f"{df[col_fat].sum():,.2f}" if col_fat in df else "—")
    m2.metric("Qtde. Líquida",      f"{df[COL_QTDE_LIQUIDA].sum(skipna=True):,.2f}" if COL_QTDE_LIQUIDA in df else "—")
    m3.metric("Linhas excluídas",   f"{df[COL_QTDE_LIQUIDA].isna().sum():,}" if COL_QTDE_LIQUIDA in df else "—")
    m4.metric("Linhas contabiliz.", f"{df[COL_QTDE_LIQUIDA].notna().sum():,}" if COL_QTDE_LIQUIDA in df else "—")

    st.markdown("<br>", unsafe_allow_html=True)

    # Linha 2 — Receita
    m5, m6, m7 = st.columns(3)
    m5.metric("Receita Bruta",   fmt_rs(df[COL_RB].sum(skipna=True)) if COL_RB in df else "—")
    m6.metric("Impostos",        fmt_rs(df[COL_IMPOSTOS].sum(skipna=True)) if COL_IMPOSTOS in df else "—")
    m7.metric("Receita Líquida", fmt_rs(df[COL_RL].sum(skipna=True)) if COL_RL in df else "—")

    st.markdown("<br>", unsafe_allow_html=True)

    # Linha 3 — Resultado
    m8, m9, m10, m11 = st.columns(4)
    rl_tot       = df[COL_RL].sum(skipna=True) if COL_RL in df else 0
    rb_tot       = df[COL_RB].sum(skipna=True) if COL_RB in df else 0
    cpv_pct      = df[COL_CPV].sum(skipna=True) / rl_tot * 100 if rl_tot else 0
    mg_pct       = df[COL_MARGEM].sum(skipna=True) / rb_tot * 100 if rb_tot else 0

    m8.metric("CPV",      fmt_rs(df[COL_CPV].sum(skipna=True)) if COL_CPV in df else "—")
    m9.metric("CPV%",     f"{cpv_pct:.1f}%")
    m10.metric("Margem",  fmt_rs(df[COL_MARGEM].sum(skipna=True)) if COL_MARGEM in df else "—")
    m11.metric("Margem%", f"{mg_pct:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)
