"""
ui/abas/aba_pedidos.py
Conteúdo da aba Pedidos (PED).
"""

import streamlit as st
import pandas as pd
from modulos.ped.config import (
    COLUNAS, ANO_REFERENCIA,
    COL_ANO_CAD, COL_VALOR_VENDA, COL_MES,
    COL_CONT_CLI, COL_CONT_NOVOS, COL_CONCATENAR, COL_INTERCOMPANY,
)
from ui.componentes.cards import titulo_secao


def renderizar_empresa(
    df: pd.DataFrame,
    empresa: str,
    n_linhas: int,
    ano_ref: int = ANO_REFERENCIA,
) -> None:
    """Renderiza aba PED de uma empresa."""
    if df.empty:
        st.warning(f"Sem dados de pedidos para {empresa}.")
        return

    col_razao = COLUNAS["razao_social"]

    # ── Métricas ──────────────────────────────────────────────────────────────
    df_inc = df[df[COL_VALOR_VENDA].notna()]
    cli_unicos = df_inc[COL_CONT_CLI].sum(skipna=True) if COL_CONT_CLI in df_inc else 0
    novos      = df[COL_CONT_NOVOS].sum(skipna=True) if COL_CONT_NOVOS in df else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Valor Carteira",    f"R$ {df_inc[COL_VALOR_VENDA].sum():,.2f}" if COL_VALOR_VENDA in df_inc else "—")
    m2.metric("Linhas incluídas",  f"{len(df_inc):,}")
    m3.metric("Clientes únicos",   f"{cli_unicos:.0f}")
    m4.metric(f"Novos ({ano_ref})", f"{novos:.0f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabela principal ──────────────────────────────────────────────────────
    colunas_exib = [c for c in [
        col_razao,
        COLUNAS["pedido"],
        COLUNAS["item"],
        COLUNAS["descricao"],
        COLUNAS["qtde_solicitada"],
        COLUNAS["qtde_cancelada"],
        COLUNAS["valor_unit"],
        COL_VALOR_VENDA,
        COL_MES,
        COL_ANO_CAD,
        COL_CONCATENAR,
        COL_CONT_CLI,
        COL_CONT_NOVOS,
        COLUNAS["representante"],
        COLUNAS["estado"],
        COL_INTERCOMPANY,
    ] if c in df.columns]

    titulo_secao(f"📋 Pedidos — {empresa} ({len(df):,} linhas)")
    st.dataframe(
        df[colunas_exib].head(n_linhas),
        use_container_width=True,
        hide_index=True,
        column_config={
            COL_VALOR_VENDA: st.column_config.NumberColumn("Valor Venda", format="R$ %.2f"),
            COL_CONT_CLI:    st.column_config.NumberColumn("CONT.SES CLI", format="%.4f"),
            COL_CONT_NOVOS:  st.column_config.NumberColumn("CONT.SES Novos", format="%.4f"),
            COL_ANO_CAD:     st.column_config.NumberColumn("Ano Cad.", format="%d"),
        },
    )

    # ── Resumo por mês ────────────────────────────────────────────────────────
    if COL_MES in df.columns and COL_VALOR_VENDA in df.columns:
        titulo_secao("📅 Carteira por Mês")
        grp = (
            df.groupby(COL_MES)
            .agg(
                Valor_Venda = (COL_VALOR_VENDA, "sum"),
                Pedidos     = (COLUNAS["pedido"], "nunique"),
                Clientes    = (col_razao,          "nunique"),
            )
            .reset_index()
        )
        grp.columns = ["Mês", "Valor da Carteira", "Pedidos", "Clientes"]
        st.dataframe(grp, use_container_width=True, hide_index=True)

    # ── Resumo por representante ──────────────────────────────────────────────
    col_rep = COLUNAS["representante"]
    if col_rep in df.columns and COL_VALOR_VENDA in df.columns:
        titulo_secao("👤 Carteira por Representante")
        grp_rep = (
            df.groupby(col_rep)
            .agg(
                Valor_Venda  = (COL_VALOR_VENDA, "sum"),
                CLI_Unicos   = (COL_CONT_CLI,     "sum"),
                Pedidos      = (COLUNAS["pedido"], "nunique"),
            )
            .reset_index()
            .sort_values("Valor_Venda", ascending=False)
        )
        grp_rep.columns = ["Representante", "Valor Carteira", "Clientes Únicos", "Pedidos"]
        st.dataframe(grp_rep, use_container_width=True, hide_index=True)
