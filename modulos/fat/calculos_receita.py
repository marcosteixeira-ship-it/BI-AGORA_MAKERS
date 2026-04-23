"""
modulos/fat/calculos_receita.py
Fórmulas de receita do módulo FAT:
  [2]  RB        J+K+L-M-AJ
  [AJ] RB DEV    (J+K+L-M)/I × AI
  [3]  IMPOSTOS  N+O+P+Q+AB-AK
  [AK] IMP DEV   (N+O+P+Q)/I × AI
  [4]  RL        RB - Impostos
  [AL] RL DEV    AJ - AK
"""

import pandas as pd
import numpy as np
from modulos.fat.config import (
    COLUNAS, COL_INTERCOMPANY,
    COL_RB, COL_RB_DEVOLUCAO,
    COL_IMPOSTOS, COL_IMPOSTOS_DEV,
    COL_RL, COL_RL_DEV,
    COL_QTDE_DEVOLUCAO,
)
from modulos.fat.calculos_base import _excluir, _excluir_ic_only, _checar, _get


# ── [2] RB + [AJ] RB DEV ─────────────────────────────────────────────────────

def calcular_rb(df: pd.DataFrame) -> pd.DataFrame:
    """
    [2]  =SE(E=$E$2;"";SE(IC;"";J+K+L-M-AJ))
    [AJ] =SE(I=$I$2;""; (J+K+L-M)/I × AI)
    """
    _checar(df, ["razao_social", "valor_total", "frete", "desconto"])
    if COL_QTDE_DEVOLUCAO not in df.columns:
        raise ValueError("Execute calcular_qtde() antes de calcular_rb().")

    df = df.copy()
    res, res_aj = [], []

    for _, row in df.iterrows():
        if _excluir(row[COLUNAS["razao_social"]], row["_nome_empresa"], row[COL_INTERCOMPANY]):
            res.append(None); res_aj.append(0.0)
            continue

        j = _get(row, "valor_total")
        k = _get(row, "frete")
        l = _get(row, "desp_acess")
        m = _get(row, "desconto")
        i = _get(row, "qtde_faturada")
        ai = float(row.get(COL_QTDE_DEVOLUCAO, 0) or 0)

        aj = (j + k + l - m) / i * ai if (i != 0 and ai != 0) else 0.0
        res.append(j + k + l - m - aj)
        res_aj.append(aj)

    df[COL_RB]           = pd.to_numeric(res, errors="coerce")
    df[COL_RB_DEVOLUCAO] = res_aj
    return df


# ── [3] IMPOSTOS + [AK] IMP DEV ──────────────────────────────────────────────

def calcular_impostos(df: pd.DataFrame) -> pd.DataFrame:
    """
    [3]  =SE(E=$E$2;"";SE(IC;"";N+O+P+Q+AB-AK))
    [AK] =SE(I=$I$2;""; (N+O+P+Q)/I × AI)
    """
    _checar(df, ["razao_social", "icms", "cofins", "pis", "issqn"])
    if COL_QTDE_DEVOLUCAO not in df.columns:
        raise ValueError("Execute calcular_qtde() antes de calcular_impostos().")

    df = df.copy()
    res, res_ak = [], []

    for _, row in df.iterrows():
        if _excluir(row[COLUNAS["razao_social"]], row["_nome_empresa"], row[COL_INTERCOMPANY]):
            res.append(None); res_ak.append(0.0)
            continue

        n  = _get(row, "icms")
        o  = _get(row, "cofins")
        p  = _get(row, "pis")
        q  = _get(row, "issqn")
        ab = _get(row, "icms_uf_dest")
        i  = _get(row, "qtde_faturada")
        ai = float(row.get(COL_QTDE_DEVOLUCAO, 0) or 0)

        ak = (n + o + p + q) / i * ai if (i != 0 and ai != 0) else 0.0
        res.append(n + o + p + q + ab - ak)
        res_ak.append(ak)

    df[COL_IMPOSTOS]     = pd.to_numeric(res, errors="coerce")
    df[COL_IMPOSTOS_DEV] = res_ak
    return df


# ── [4] RL + [AL] RL DEV ─────────────────────────────────────────────────────

def calcular_rl(df: pd.DataFrame) -> pd.DataFrame:
    """
    [4]  =SEERRO(SE(IC;""; AO-AP);"")   — não testa $E$2
    [AL] =SE(AJ="";""; AJ-AK)
    """
    for col in [COL_RB, COL_IMPOSTOS, COL_RB_DEVOLUCAO, COL_IMPOSTOS_DEV]:
        if col not in df.columns:
            raise ValueError("Execute calcular_rb() e calcular_impostos() antes.")

    df = df.copy()
    res, res_rl_dev = [], []

    for _, row in df.iterrows():
        # RL principal
        if _excluir_ic_only(row[COLUNAS["razao_social"]], row[COL_INTERCOMPANY]):
            res.append(None)
        else:
            try:
                rb, imp = row[COL_RB], row[COL_IMPOSTOS]
                res.append(None if (pd.isna(rb) or pd.isna(imp))
                           else float(rb) - float(imp))
            except Exception:
                res.append(None)

        # RL DEV: SE(AJ="";""; AJ-AK)
        aj = float(row.get(COL_RB_DEVOLUCAO, 0) or 0)
        ak = float(row.get(COL_IMPOSTOS_DEV, 0) or 0)
        res_rl_dev.append(aj - ak if aj != 0 else None)

    df[COL_RL]     = pd.to_numeric(res, errors="coerce")
    df[COL_RL_DEV] = pd.to_numeric(res_rl_dev, errors="coerce")
    return df
