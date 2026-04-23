"""
modulos/fat/calculos_resultado.py
Fórmulas de resultado e identificação do módulo FAT:
  [5]  CPV       (W+X+Y)*I - AM
  [AM] CPV DEV   (W+X+Y) × AI
  [6]  CPV%      CPV / RL
  [7]  MARGEM    RL - CPV - Comissão
  [8]  MARGEM%   Margem / RB
  [9]  EMPRESA-CLIENTE  CONCAT(sufixo, "-", Cliente)
  [10] ANO DE CADASTRO  ANO(Data cad. clie.)
"""

import pandas as pd
import numpy as np
from modulos.fat.config import (
    COLUNAS, PREFIXO_EMPRESA, COL_INTERCOMPANY,
    COL_RL, COL_RB,
    COL_CPV, COL_CPV_DEVOLUCAO, COL_CPV_PCT,
    COL_MARGEM, COL_MARGEM_PCT,
    COL_EMPRESA_CLI, COL_ANO_CAD,
    COL_QTDE_DEVOLUCAO,
)
from modulos.fat.calculos_base import _excluir_ic_only, _checar, _get


# ── [5] CPV + [AM] CPV DEV ───────────────────────────────────────────────────

def calcular_cpv(df: pd.DataFrame) -> pd.DataFrame:
    """
    [5]  =SEERRO(SE(IC;""; (W+X+Y)*I - AM);"")
    [AM] =SE(W=$W$2;""; (W+X+Y) × AI)
    """
    _checar(df, ["razao_social", "custo_revenda", "terceirizacao", "custo_mp", "qtde_faturada"])
    if COL_QTDE_DEVOLUCAO not in df.columns:
        raise ValueError("Execute calcular_qtde() antes de calcular_cpv().")

    df = df.copy()
    res, res_am = [], []

    for _, row in df.iterrows():
        if _excluir_ic_only(row[COLUNAS["razao_social"]], row[COL_INTERCOMPANY]):
            res.append(None); res_am.append(0.0)
            continue
        try:
            w  = _get(row, "custo_revenda")
            x  = _get(row, "terceirizacao")
            y  = _get(row, "custo_mp")
            i  = _get(row, "qtde_faturada")
            ai = float(row.get(COL_QTDE_DEVOLUCAO, 0) or 0)
            am = (w + x + y) * ai if ai != 0 else 0.0
            res.append((w + x + y) * i - am)
            res_am.append(am)
        except Exception:
            res.append(None); res_am.append(0.0)

    df[COL_CPV]           = pd.to_numeric(res, errors="coerce")
    df[COL_CPV_DEVOLUCAO] = res_am
    return df


# ── [6] CPV% ─────────────────────────────────────────────────────────────────

def calcular_cpv_pct(df: pd.DataFrame) -> pd.DataFrame:
    """[6] =SEERRO(CPV/RL;"")"""
    for col in [COL_RL, COL_CPV]:
        if col not in df.columns:
            raise ValueError("Execute calcular_rl() e calcular_cpv() antes.")
    df = df.copy()
    res = []
    for _, row in df.iterrows():
        try:
            rl, cpv = row[COL_RL], row[COL_CPV]
            res.append(None if (pd.isna(rl) or pd.isna(cpv) or float(rl) == 0)
                       else float(cpv) / float(rl))
        except Exception:
            res.append(None)
    df[COL_CPV_PCT] = pd.to_numeric(res, errors="coerce")
    return df


# ── [7] MARGEM ────────────────────────────────────────────────────────────────

def calcular_margem(df: pd.DataFrame) -> pd.DataFrame:
    """[7] =SEERRO(RL - CPV - Comissão; 0)"""
    for col in [COL_RL, COL_CPV]:
        if col not in df.columns:
            raise ValueError("Execute calcular_rl() e calcular_cpv() antes.")
    _checar(df, ["comissao"])
    df = df.copy()
    res = []
    for _, row in df.iterrows():
        try:
            rl, cpv = row[COL_RL], row[COL_CPV]
            com = _get(row, "comissao")
            res.append(0.0 if (pd.isna(rl) or pd.isna(cpv))
                       else float(rl) - float(cpv) - com)
        except Exception:
            res.append(0.0)
    df[COL_MARGEM] = pd.Series(pd.to_numeric(res, errors="coerce")).fillna(0.0).values
    return df


# ── [8] MARGEM% ───────────────────────────────────────────────────────────────

def calcular_margem_pct(df: pd.DataFrame) -> pd.DataFrame:
    """[8] =SEERRO(Margem/RB;"")"""
    for col in [COL_MARGEM, COL_RB]:
        if col not in df.columns:
            raise ValueError("Execute calcular_margem() e calcular_rb() antes.")
    df = df.copy()
    res = []
    for _, row in df.iterrows():
        try:
            mg, rb = row[COL_MARGEM], row[COL_RB]
            res.append(None if (pd.isna(mg) or pd.isna(rb) or float(rb) == 0)
                       else float(mg) / float(rb))
        except Exception:
            res.append(None)
    df[COL_MARGEM_PCT] = pd.to_numeric(res, errors="coerce")
    return df


# ── [9] EMPRESA-CLIENTE ───────────────────────────────────────────────────────

def calcular_empresa_cliente(df: pd.DataFrame) -> pd.DataFrame:
    """[9] =CONCATENAR(A, "-", D)   A=sufixo, D=código Cliente"""
    if "_sufixo" not in df.columns:
        raise ValueError("Coluna '_sufixo' ausente.")
    col_cli = COLUNAS["cliente"]
    df = df.copy()
    pref = df["_sufixo"].map(PREFIXO_EMPRESA).fillna(df["_sufixo"].str.upper())
    df[COL_EMPRESA_CLI] = pref + "-" + df[col_cli].astype(str)
    return df


# ── [10] ANO DE CADASTRO ─────────────────────────────────────────────────────

def calcular_ano_cadastro(df: pd.DataFrame) -> pd.DataFrame:
    """[10] =SEERRO(ANO(AF);"")   AF = Data de cad. clie."""
    col_data = COLUNAS["data_cad_cli"]
    if col_data not in df.columns:
        raise ValueError(f"Coluna '{col_data}' ausente.")
    df = df.copy()
    try:
        df[COL_ANO_CAD] = df[col_data].dt.year.where(df[col_data].notna(), other=np.nan)
    except Exception:
        df[COL_ANO_CAD] = np.nan
    return df
