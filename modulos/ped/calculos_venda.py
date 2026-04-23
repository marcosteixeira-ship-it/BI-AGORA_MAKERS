"""
modulos/ped/calculos_venda.py
Fórmulas de venda e tempo da aba PED:
  [Y]  ANO CADASTRO  ANO(W)
  [Z]  VALOR DA VENDA  SE(IC;""; (H-I)*K)
  [AA] MÊS  MÊS(A) por extenso em PT-BR
"""

import pandas as pd
import numpy as np
from modulos.ped.config import (
    COLUNAS, MESES_PT, NOMES_INTERCOMPANY,
    COL_INTERCOMPANY, COL_ANO_CAD, COL_VALOR_VENDA, COL_MES,
)


def _excluir_ic(razao: str, flag: str) -> bool:
    """IC only — sem testar $E$2 (igual ao Excel para PED)."""
    r = str(razao).strip().upper()
    f = str(flag).strip().upper()
    return f == "SIM" and r in ("METALCO DO BRASIL LTDA", "OMP DO BRASIL LTDA")


def _get(row, chave: str, default: float = 0.0) -> float:
    nome = COLUNAS.get(chave, chave)
    v = row.get(nome, default)
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return default
    try:
        return float(v)
    except (ValueError, TypeError):
        return default


def aplicar_flag_intercompany(df: pd.DataFrame, valor_flag: str = "NAO") -> pd.DataFrame:
    """Adiciona COL_INTERCOMPANY em todas as linhas."""
    df = df.copy()
    v = str(valor_flag).strip().upper().replace("NÃO", "NAO")
    if v not in ("SIM", "NAO"):
        raise ValueError(f"Flag inválida: '{valor_flag}'.")
    df[COL_INTERCOMPANY] = v
    return df


# ── [Y] ANO CADASTRO ─────────────────────────────────────────────────────────

def calcular_ano_cadastro(df: pd.DataFrame) -> pd.DataFrame:
    """
    =ANO(W3)
    W = Cliente - Data de cadastro
    """
    col_data = COLUNAS["dt_cadastro"]
    if col_data not in df.columns:
        raise ValueError(f"Coluna '{col_data}' ausente.")
    df = df.copy()
    try:
        df[COL_ANO_CAD] = df[col_data].dt.year.where(df[col_data].notna(), other=np.nan)
    except Exception:
        df[COL_ANO_CAD] = np.nan
    return df


# ── [Z] VALOR DA VENDA ────────────────────────────────────────────────────────

def calcular_valor_venda(df: pd.DataFrame) -> pd.DataFrame:
    """
    =SE(E(IC; C="METALCO");""; SE(E(IC; C="OMP");""; (H-I)*K))
    H = Qtde. solicitada  |  I = Qtde. cancelada  |  K = Valor unitário
    """
    if COL_INTERCOMPANY not in df.columns:
        raise ValueError("Execute aplicar_flag_intercompany() antes.")

    df = df.copy()
    res = []
    col_razao = COLUNAS["razao_social"]

    for _, row in df.iterrows():
        if _excluir_ic(row[col_razao], row[COL_INTERCOMPANY]):
            res.append(None)
            continue
        h = _get(row, "qtde_solicitada")
        i = _get(row, "qtde_cancelada")
        k = _get(row, "valor_unit")
        res.append((h - i) * k)

    df[COL_VALOR_VENDA] = pd.to_numeric(res, errors="coerce")
    return df


# ── [AA] MÊS ─────────────────────────────────────────────────────────────────

def calcular_mes(df: pd.DataFrame) -> pd.DataFrame:
    """
    =MÊS(A3) → convertido para nome por extenso PT-BR
    A = Data de emissão
    """
    col_data = COLUNAS["data_emissao"]
    if col_data not in df.columns:
        raise ValueError(f"Coluna '{col_data}' ausente.")
    df = df.copy()
    df[COL_MES] = df[col_data].dt.month.map(MESES_PT)
    return df
