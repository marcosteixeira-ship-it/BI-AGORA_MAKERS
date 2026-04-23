"""
modulos/fat/processamento.py
Orquestra todas as fórmulas FAT na ordem correta.
Importa funções de calculos_base, calculos_receita e calculos_resultado.
"""

import pandas as pd
from modulos.fat.calculos_base import (
    set_esc_lookup, aplicar_flag_intercompany, calcular_qtde,
)
from modulos.fat.calculos_receita import (
    calcular_rb, calcular_impostos, calcular_rl,
)
from modulos.fat.calculos_resultado import (
    calcular_cpv, calcular_cpv_pct, calcular_margem,
    calcular_margem_pct, calcular_empresa_cliente, calcular_ano_cadastro,
)
from modulos.fat.config import COLUNAS


def adicionar_colunas_tempo(df: pd.DataFrame) -> pd.DataFrame:
    """Adiciona _mes, _mes_per, _ano, _semana, _dia_sem para agrupamentos."""
    col_data = COLUNAS["data_emissao"]
    if col_data not in df.columns:
        return df
    df = df.copy()
    dt = df[col_data]
    df["_mes"]      = dt.dt.month
    df["_mes_nome"] = dt.dt.strftime("%b/%Y")
    df["_mes_per"]  = dt.dt.to_period("M").astype(str)
    df["_ano"]      = dt.dt.year
    df["_semana"]   = dt.dt.isocalendar().week.astype("Int64")
    df["_dia_sem"]  = dt.dt.day_name()
    return df


def processar(df: pd.DataFrame, flag_intercompany: str = "NAO") -> pd.DataFrame:
    """
    Executa as 10 fórmulas FAT em sequência.

    Ordem obrigatória:
      1.  aplicar_flag_intercompany  → Intercompany
      2.  calcular_qtde              → Qtde Líquida + Qtde Devolvida (AI)
      3.  calcular_rb                → Receita Bruta + RB Devolvida (AJ)
      4.  calcular_impostos          → Impostos + Impostos Dev. (AK)
      5.  calcular_rl                → Receita Líquida + RL Dev. (AL)
      6.  calcular_cpv               → CPV + CPV Dev. (AM)
      7.  calcular_cpv_pct           → CPV%
      8.  calcular_margem            → Margem
      9.  calcular_margem_pct        → Margem%
      10. calcular_empresa_cliente   → Empresa-Cliente
      11. calcular_ano_cadastro      → Ano de Cadastro
      12. adicionar_colunas_tempo    → _mes, _mes_per, etc.
    """
    df = aplicar_flag_intercompany(df, flag_intercompany)
    df = calcular_qtde(df)
    df = calcular_rb(df)
    df = calcular_impostos(df)
    df = calcular_rl(df)
    df = calcular_cpv(df)
    df = calcular_cpv_pct(df)
    df = calcular_margem(df)
    df = calcular_margem_pct(df)
    df = calcular_empresa_cliente(df)
    df = calcular_ano_cadastro(df)
    df = adicionar_colunas_tempo(df)
    return df


def diagnosticar_processamento(df: pd.DataFrame) -> None:
    """Imprime resumo de todas as colunas calculadas."""
    from modulos.fat.config import (
        COL_QTDE_LIQUIDA, COL_QTDE_DEVOLUCAO, COL_RB, COL_RB_DEVOLUCAO,
        COL_IMPOSTOS, COL_IMPOSTOS_DEV, COL_RL, COL_RL_DEV,
        COL_CPV, COL_CPV_DEVOLUCAO, COL_MARGEM, COL_EMPRESA_CLI, COL_ANO_CAD,
        COL_INTERCOMPANY,
    )
    sep = "─" * 60
    print(f"\n{sep}")
    print("  FAT — Diagnóstico de Processamento")
    print(sep)

    if COL_INTERCOMPANY in df.columns:
        for val, cnt in df[COL_INTERCOMPANY].value_counts().items():
            print(f"  Intercompany '{val}': {cnt:,}")

    pares = [
        (COL_QTDE_LIQUIDA,  "QTDE  (I-AI)"),
        (COL_RB,            "RB    (J+K+L-M-AJ)"),
        (COL_IMPOSTOS,      "IMP   (N+O+P+Q+AB-AK)"),
        (COL_RL,            "RL    (RB-IMP)"),
        (COL_CPV,           "CPV   ((W+X+Y)*I-AM)"),
        (COL_MARGEM,        "MARG  (RL-CPV-Com)"),
    ]
    devs = [
        (COL_QTDE_DEVOLUCAO, "  └─ Qtde Dev"),
        (COL_RB_DEVOLUCAO,   "  └─ RB Dev"),
        (COL_IMPOSTOS_DEV,   "  └─ Imp Dev"),
        (COL_RL_DEV,         "  └─ RL Dev"),
        (COL_CPV_DEVOLUCAO,  "  └─ CPV Dev"),
    ]

    for col, lbl in pares:
        if col in df.columns:
            s = df[col]
            print(f"\n  [{lbl}]  calculadas:{s.notna().sum():>6,}  excluídas:{s.isna().sum():>5,}  total: R$ {s.sum(skipna=True):>14,.2f}")

    linhas_dev = df[COL_QTDE_DEVOLUCAO].gt(0).sum() if COL_QTDE_DEVOLUCAO in df.columns else 0
    print(f"\n  [DEVOLUÇÕES] {linhas_dev:,} linhas com devolução vinculada")
    for col, lbl in devs:
        if col in df.columns:
            tot = df[col].sum(skipna=True) if df[col].dtype != object else 0
            print(f"  {lbl}: {tot:,.4f}")

    if COL_EMPRESA_CLI in df.columns:
        print(f"\n  [EMPRESA-CLI] ex: {df[COL_EMPRESA_CLI].dropna().head(3).tolist()}")
    if COL_ANO_CAD in df.columns:
        anos = sorted(df[COL_ANO_CAD].dropna().astype(int).unique())
        print(f"  [ANO CAD]    : {anos[:8]}{'...' if len(anos)>8 else ''}")
    if "_mes_per" in df.columns:
        print(f"  [MESES]      : {sorted(df['_mes_per'].dropna().unique())}")
    print(f"{sep}\n")
