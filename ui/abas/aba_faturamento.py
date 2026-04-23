"""
ui/abas/aba_faturamento.py
Conteúdo das abas My City, Metalco e Consolidado — módulo FAT.
"""

import streamlit as st
import pandas as pd
from modulos.fat.config import (
    COLUNAS,
    COL_QTDE_LIQUIDA, COL_QTDE_DEVOLUCAO,
    COL_RB, COL_IMPOSTOS, COL_RL,
    COL_CPV, COL_CPV_PCT, COL_MARGEM, COL_MARGEM_PCT,
    COL_EMPRESA_CLI, COL_ANO_CAD, COL_INTERCOMPANY,
)
from ui.componentes.cards import titulo_secao, linha_metricas_fat


def _tabela_principal(df: pd.DataFrame, empresa: str, n_linhas: int,
                      mostrar_vazios: bool) -> None:
    """Renderiza tabela detalhada de faturamento."""
    col_fat   = COLUNAS["qtde_faturada"]
    col_razao = COLUNAS["razao_social"]

    df_exib = df if mostrar_vazios else df[df[COL_QTDE_LIQUIDA].notna()]

    colunas_exib = [c for c in [
        COL_EMPRESA_CLI, col_razao, "Nota", "Item", "Descrição",
        col_fat, COL_QTDE_DEVOLUCAO, COL_QTDE_LIQUIDA,
        COLUNAS["valor_total"], COL_RB, COL_IMPOSTOS, COL_RL,
        COL_CPV, COL_CPV_PCT, COL_MARGEM, COL_MARGEM_PCT,
        COL_INTERCOMPANY, "Data de emissão", COL_ANO_CAD,
        "Grupo de itens", "Estado",
    ] if c in df_exib.columns]

    titulo_secao(f"📋 Tabela — {empresa} ({len(df_exib):,} linhas)")
    st.dataframe(
        df_exib[colunas_exib].head(n_linhas),
        use_container_width=True,
        hide_index=True,
        column_config={
            COL_EMPRESA_CLI:    st.column_config.TextColumn("Empresa-Cliente"),
            COL_QTDE_LIQUIDA:   st.column_config.NumberColumn("Qtde Líquida",  format="%.4f"),
            COL_QTDE_DEVOLUCAO: st.column_config.NumberColumn("Qtde Dev.",      format="%.4f"),
            COL_RB:             st.column_config.NumberColumn("Rec. Bruta",     format="R$ %.2f"),
            COL_IMPOSTOS:       st.column_config.NumberColumn("Impostos",       format="R$ %.2f"),
            COL_RL:             st.column_config.NumberColumn("Rec. Líquida",   format="R$ %.2f"),
            COL_CPV:            st.column_config.NumberColumn("CPV",            format="R$ %.2f"),
            COL_CPV_PCT:        st.column_config.NumberColumn("CPV%",           format="%.2%%"),
            COL_MARGEM:         st.column_config.NumberColumn("Margem",         format="R$ %.2f"),
            COL_MARGEM_PCT:     st.column_config.NumberColumn("Margem%",        format="%.2%%"),
            COL_ANO_CAD:        st.column_config.NumberColumn("Ano Cad.",       format="%d"),
            COL_INTERCOMPANY:   st.column_config.TextColumn("IC"),
            col_fat:            st.column_config.NumberColumn(format="%.4f"),
        },
    )


def _resumo_por_cliente(df: pd.DataFrame) -> None:
    """Agrupamento por razão social."""
    col_razao = COLUNAS["razao_social"]
    col_fat   = COLUNAS["qtde_faturada"]

    agg = {k: v for k, v in {
        "Qtde Faturada":   (col_fat,          "sum"),
        "Qtde Líquida":    (COL_QTDE_LIQUIDA,  "sum"),
        "Receita Bruta":   (COL_RB,            "sum"),
        "Impostos":        (COL_IMPOSTOS,      "sum"),
        "Receita Líquida": (COL_RL,            "sum"),
        "CPV":             (COL_CPV,           "sum"),
        "Margem":          (COL_MARGEM,        "sum"),
        "Notas":           ("Nota",             "nunique"),
    }.items() if v[0] in df.columns}

    titulo_secao("📦 Resumo por Cliente")
    grp = (
        df.groupby(col_razao).agg(**agg).reset_index()
        .sort_values("Receita Líquida", ascending=False)
    )
    st.dataframe(grp, use_container_width=True, hide_index=True)


def renderizar_empresa(df: pd.DataFrame, empresa: str,
                       n_linhas: int, mostrar_vazios: bool) -> None:
    """Renderiza aba de uma empresa (OMP ou MTC)."""
    if df.empty:
        st.warning(f"Sem dados para {empresa} no período selecionado.")
        return

    linha_metricas_fat(df, {})
    _tabela_principal(df, empresa, n_linhas, mostrar_vazios)
    _resumo_por_cliente(df)


def renderizar_consolidado(df_cons: pd.DataFrame) -> None:
    """Renderiza aba Consolidado (OMP + MTC)."""
    if df_cons.empty:
        st.warning("Nenhum dado carregado para o período selecionado.")
        return

    col_fat_c = COLUNAS["qtde_faturada"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Receita Bruta",   f"R$ {df_cons[COL_RB].sum(skipna=True):,.2f}")
    c2.metric("Impostos",        f"R$ {df_cons[COL_IMPOSTOS].sum(skipna=True):,.2f}")
    c3.metric("Rec. Líquida",    f"R$ {df_cons[COL_RL].sum(skipna=True):,.2f}")
    c4.metric("Margem Total",    f"R$ {df_cons[COL_MARGEM].sum(skipna=True):,.2f}")

    st.markdown("<br>", unsafe_allow_html=True)

    grp_emp = (
        df_cons.groupby("_empresa").agg(
            Qtde_Fat  = (col_fat_c,              "sum"),
            Qtde_Liq  = (COL_QTDE_LIQUIDA,       "sum"),
            RB        = (COL_RB,                 "sum"),
            Impostos  = (COL_IMPOSTOS,           "sum"),
            RL        = (COL_RL,                 "sum"),
            CPV       = (COL_CPV,                "sum"),
            Margem    = (COL_MARGEM,             "sum"),
            Notas     = ("Nota",                  "nunique"),
            Clientes  = (COLUNAS["razao_social"], "nunique"),
        ).reset_index()
    )
    grp_emp.columns = [
        "Empresa", "Qtde Faturada", "Qtde Líquida",
        "Receita Bruta", "Impostos", "Receita Líquida",
        "CPV", "Margem", "Notas", "Clientes",
    ]
    titulo_secao("📊 Comparativo por Empresa")
    st.dataframe(grp_emp, use_container_width=True, hide_index=True)
