"""
modulos/ped/processamento.py
Orquestra todas as fórmulas PED na ordem correta.
"""

import pandas as pd
from modulos.ped.calculos_venda import (
    aplicar_flag_intercompany,
    calcular_ano_cadastro,
    calcular_valor_venda,
    calcular_mes,
)
from modulos.ped.calculos_contagem import (
    calcular_concatenar,
    calcular_cont_ses_clientes,
    calcular_cont_ses_novos,
)
from modulos.ped.config import (
    ANO_REFERENCIA, COL_INTERCOMPANY,
    COL_ANO_CAD, COL_VALOR_VENDA, COL_MES,
    COL_CONCATENAR, COL_CONT_CLI, COL_CONT_NOVOS,
)


def processar(
    df: pd.DataFrame,
    flag_intercompany: str = "NAO",
    ano_ref: int = ANO_REFERENCIA,
) -> pd.DataFrame:
    """
    Executa as 6 fórmulas PED em sequência:
      1. aplicar_flag_intercompany
      2. calcular_ano_cadastro     [Y]  ANO(W)
      3. calcular_valor_venda      [Z]  (H-I)*K
      4. calcular_mes              [AA] MÊS(A) PT-BR
      5. calcular_concatenar       [AD] C+"-"+Y
      6. calcular_cont_ses_clientes [AB] 1/CONT.SES(C,V)
      7. calcular_cont_ses_novos    [AC] SE(Y=ano; 1/CONT.SE(AD); "")
    """
    df = aplicar_flag_intercompany(df, flag_intercompany)
    df = calcular_ano_cadastro(df)
    df = calcular_valor_venda(df)
    df = calcular_mes(df)
    df = calcular_concatenar(df)
    df = calcular_cont_ses_clientes(df)
    df = calcular_cont_ses_novos(df, ano_ref=ano_ref)
    return df


def diagnosticar_processamento(
    df: pd.DataFrame,
    ano_ref: int = ANO_REFERENCIA,
) -> None:
    """Imprime resumo das colunas calculadas do PED."""
    sep = "─" * 55
    print(f"\n{sep}")
    print("  PED — Diagnóstico de Processamento")
    print(sep)

    if COL_INTERCOMPANY in df.columns:
        for val, cnt in df[COL_INTERCOMPANY].value_counts().items():
            print(f"  Intercompany '{val}': {cnt:,}")

    if COL_ANO_CAD in df.columns:
        anos = sorted(df[COL_ANO_CAD].dropna().astype(int).unique())
        print(f"\n  [ANO CAD]  {anos[:8]}{'...' if len(anos)>8 else ''}")

    if COL_VALOR_VENDA in df.columns:
        s = df[COL_VALOR_VENDA]
        print(f"\n  [VALOR VENDA]  calculadas:{s.notna().sum():>6,}  excluídas:{s.isna().sum():>5,}")
        print(f"    Total: R$ {s.sum(skipna=True):,.2f}")

    if COL_MES in df.columns:
        meses = ["JANEIRO","FEVEREIRO","MARÇO","ABRIL","MAIO","JUNHO",
                 "JULHO","AGOSTO","SETEMBRO","OUTUBRO","NOVEMBRO","DEZEMBRO"]
        dist = df[COL_MES].value_counts()
        print(f"\n  [MÊS]")
        for m in meses:
            if m in dist.index:
                print(f"    {m:<12}: {dist[m]:,}")

    if COL_CONCATENAR in df.columns:
        ex = df[COL_CONCATENAR].dropna().unique()[:3].tolist()
        print(f"\n  [CONCATENAR]  ex: {ex}")

    if COL_CONT_CLI in df.columns:
        soma = df[COL_CONT_CLI].sum(skipna=True)
        print(f"\n  [CONT.SES CLI]   soma = {soma:.1f} clientes únicos por rep.")

    if COL_CONT_NOVOS in df.columns:
        soma = df[COL_CONT_NOVOS].sum(skipna=True)
        print(f"  [CONT.SES NOVOS] soma = {soma:.1f} novos clientes únicos  (ano_ref={ano_ref})")

    print(f"{sep}\n")
