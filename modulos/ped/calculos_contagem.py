"""
modulos/ped/calculos_contagem.py
Fórmulas de contagem e concatenação da aba PED:
  [AD] CONCATENAR           CONCAT(C, "-", Y)
  [AB] CONT.SES CLIENTES    1/CONT.SES(C,C,V,V)
  [AC] CONT.SES NOVOS       SE(Y=ano_ref; 1/CONT.SE(AD,AD); "")
"""

import pandas as pd
import numpy as np
from modulos.ped.config import (
    COLUNAS, ANO_REFERENCIA, COL_INTERCOMPANY,
    COL_ANO_CAD, COL_CONCATENAR, COL_CONT_CLI, COL_CONT_NOVOS,
)
from modulos.ped.calculos_venda import _excluir_ic


# ── [AD] CONCATENAR ───────────────────────────────────────────────────────────

def calcular_concatenar(df: pd.DataFrame) -> pd.DataFrame:
    """
    =CONCATENAR(C3;"-";Y3)
    C = Razão social  |  Y = Ano Cadastro
    """
    if COL_ANO_CAD not in df.columns:
        raise ValueError("Execute calcular_ano_cadastro() antes.")

    col_razao = COLUNAS["razao_social"]
    df = df.copy()
    ano_str = df[COL_ANO_CAD].apply(lambda x: str(int(x)) if pd.notna(x) else "")
    df[COL_CONCATENAR] = df[col_razao].astype(str) + "-" + ano_str
    return df


# ── [AB] CONT.SES CLIENTES ───────────────────────────────────────────────────

def calcular_cont_ses_clientes(df: pd.DataFrame) -> pd.DataFrame:
    """
    =SE(IC;""; SEERRO(1/CONT.SES(C:C;C3;V:V;V3);""))
    C = Razão social  |  V = Representante
    Resultado: 1 / (nº de linhas com mesmo par cliente+representante)
    Soma da coluna = nº de clientes únicos por representante.
    """
    if COL_INTERCOMPANY not in df.columns:
        raise ValueError("Execute aplicar_flag_intercompany() antes.")

    df = df.copy()
    col_c = COLUNAS["razao_social"]
    col_v = COLUNAS["representante"]

    # Conta apenas linhas não excluídas por IC
    mask_incluida = ~df.apply(
        lambda row: _excluir_ic(row[col_c], row[COL_INTERCOMPANY]), axis=1
    )
    contagem = (
        df[mask_incluida]
        .groupby([col_c, col_v])
        .size()
        .rename("_cnt_cv")
        .reset_index()
    )
    df = df.merge(contagem, on=[col_c, col_v], how="left")

    res = []
    for _, row in df.iterrows():
        if _excluir_ic(row[col_c], row[COL_INTERCOMPANY]):
            res.append(None)
            continue
        cnt = row.get("_cnt_cv", 0)
        try:
            res.append(1.0 / float(cnt) if (pd.notna(cnt) and cnt > 0) else None)
        except Exception:
            res.append(None)

    df[COL_CONT_CLI] = pd.to_numeric(res, errors="coerce")
    df.drop(columns=["_cnt_cv"], errors="ignore", inplace=True)
    return df


# ── [AC] CONT.SES NOVOS CLIENTES ─────────────────────────────────────────────

def calcular_cont_ses_novos(
    df: pd.DataFrame,
    ano_ref: int = ANO_REFERENCIA,
) -> pd.DataFrame:
    """
    =SE(Y=ano_ref; 1/CONT.SE(AD:AD;AD3); "")
    Y  = Ano Cadastro  |  AD = CONCATENAR
    Resultado: 1 / (nº de linhas com mesmo CONCATENAR, apenas no ano_ref)
    Soma da coluna = nº de novos clientes únicos.
    """
    for col in [COL_ANO_CAD, COL_CONCATENAR]:
        if col not in df.columns:
            raise ValueError(f"Execute calcular_ano_cadastro() e calcular_concatenar() antes.")

    df = df.copy()
    contagem_ad = df[COL_CONCATENAR].value_counts().rename("_cnt_ad")
    df["_cnt_ad"] = df[COL_CONCATENAR].map(contagem_ad)

    res = []
    for _, row in df.iterrows():
        ano_cad = row.get(COL_ANO_CAD, np.nan)
        if pd.isna(ano_cad) or int(ano_cad) != ano_ref:
            res.append(None)
            continue
        cnt = row.get("_cnt_ad", 0)
        try:
            res.append(1.0 / float(cnt) if (pd.notna(cnt) and cnt > 0) else None)
        except Exception:
            res.append(None)

    df[COL_CONT_NOVOS] = pd.to_numeric(res, errors="coerce")
    df.drop(columns=["_cnt_ad"], errors="ignore", inplace=True)
    return df
