"""
modulos/esc/processamento.py
Orquestra as 5 fórmulas ESC na ordem correta:
  Q → T → U → V → W
"""

import pandas as pd
from modulos.esc.calculos_q_t_u import (
    calcular_q_concatenar,
    calcular_t_impostos,
    calcular_u_cpv,
)
from modulos.esc.calculos_v_w import (
    calcular_v_mes,
    calcular_w_representante,
)
from modulos.esc.config import (
    COLUNAS,
    COL_Q_CONCATENAR, COL_T_IMPOSTOS, COL_U_CPV,
    COL_V_MES, COL_W_REPR,
)


def processar(
    df: pd.DataFrame,
    sufixo: str,
    df_fat_dev: pd.DataFrame,
) -> pd.DataFrame:
    """
    Executa Q → T → U → V → W em sequência.

    Parâmetros
    ----------
    df         : DataFrame bruto de leitura.ler_esc()
    sufixo     : 'omp' ou 'mtc'
    df_fat_dev : DataFrame de leitura.ler_fat_dev() (para fórmula W)
    """
    df = calcular_q_concatenar(df, sufixo)
    df = calcular_t_impostos(df, sufixo)
    df = calcular_u_cpv(df, sufixo)
    df = calcular_v_mes(df, sufixo)
    df = calcular_w_representante(df, sufixo, df_fat_dev)
    return df


def diagnosticar_processamento(df: pd.DataFrame, sufixo: str) -> None:
    """Imprime resumo das colunas calculadas do ESC."""
    sep = "─" * 55
    print(f"\n{sep}")
    print(f"  ESC {sufixo.upper()} — Diagnóstico de Processamento")
    print(sep)

    if COL_Q_CONCATENAR in df.columns:
        ex = df[COL_Q_CONCATENAR].replace("", None).dropna().head(3).tolist()
        print(f"\n  [Q] CONCATENAR  ex: {ex}")

    for col, lbl, formula in [
        (COL_T_IMPOSTOS, "T", "J+K+L"),
        (COL_U_CPV,      "U", "(N+O)*R"),
    ]:
        if col in df.columns:
            s = df[col]
            print(f"\n  [{lbl}] {formula}")
            print(f"    Calculadas: {s.notna().sum():>5,}  |  Total: R$ {s.sum(skipna=True):>12,.2f}")

    if COL_V_MES in df.columns:
        print(f"\n  [V] Mês — distribuição:")
        for mes in ["JANEIRO","FEVEREIRO","MARÇO","ABRIL","MAIO","JUNHO",
                    "JULHO","AGOSTO","SETEMBRO","OUTUBRO","NOVEMBRO","DEZEMBRO"]:
            cnt = (df[COL_V_MES] == mes).sum()
            if cnt:
                print(f"    {mes:<12}: {cnt:,}")

    if COL_W_REPR in df.columns:
        n_ok  = df[COL_W_REPR].notna().sum()
        n_nok = df[COL_W_REPR].isna().sum()
        print(f"\n  [W] Representante  encontrados:{n_ok:>5,}  sem match:{n_nok:>4,}")

    print(f"{sep}\n")
