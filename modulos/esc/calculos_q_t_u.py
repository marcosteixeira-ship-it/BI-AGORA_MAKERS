"""
modulos/esc/calculos_q_t_u.py
Fórmulas Q, T e U da aba ESC (Devoluções):
  [Q] CONCATENAR         CONCAT(P, "-", E)
  [T] IMPOSTOS DEV       J + K + L
  [U] CPV DEV            (N+O) × R
"""

import pandas as pd
import numpy as np
from modulos.esc.config import COLUNAS, COL_Q_CONCATENAR, COL_T_IMPOSTOS, COL_U_CPV


def _get(row, nome_col: str, default: float = 0.0) -> float:
    v = row.get(nome_col, default)
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return default
    try:
        return float(v)
    except (ValueError, TypeError):
        return default


def _idx_col(df: pd.DataFrame, idx: int):
    """Retorna nome da coluna por índice (para colunas 'Unnamed')."""
    try:
        return df.columns[idx]
    except IndexError:
        return None


# ── [Q] CONCATENAR ────────────────────────────────────────────────────────────

def calcular_q_concatenar(df: pd.DataFrame, sufixo: str) -> pd.DataFrame:
    """
    =CONCATENAR(P3;"-";E3)
    P = Nota fiscal de devolução
    E = Item (via _item_fmt)
    """
    col_p = COLUNAS[sufixo]["nota_dev"]
    if col_p not in df.columns:
        raise ValueError(f"Coluna '{col_p}' ausente.")
    if "_item_fmt" not in df.columns:
        raise ValueError("'_item_fmt' ausente. Execute leitura.ler_esc() antes.")

    df = df.copy()

    def _concat(row):
        p = str(row.get(col_p, "")).strip()
        e = str(row.get("_item_fmt", "")).strip()
        if not p or not e:
            return ""
        if p.endswith(".0") and p[:-2].isdigit():
            p = p[:-2]
        return f"{p}-{e}"

    df[COL_Q_CONCATENAR] = df.apply(_concat, axis=1)
    return df


# ── [T] IMPOSTOS DEV ──────────────────────────────────────────────────────────

def calcular_t_impostos(df: pd.DataFrame, sufixo: str) -> pd.DataFrame:
    """
    =SEERRO(J3+K3+L3;"")
    J = Valor ICMS  |  K = Valor PIS  |  L = Valor COFINS
    """
    cols = COLUNAS[sufixo]
    for chave in ["icms", "pis", "cofins"]:
        if cols[chave] not in df.columns:
            raise ValueError(f"Coluna '{cols[chave]}' ausente.")

    df = df.copy()
    res = []
    for _, row in df.iterrows():
        try:
            j = _get(row, cols["icms"])
            k = _get(row, cols["pis"])
            l = _get(row, cols["cofins"])
            res.append(j + k + l)
        except Exception:
            res.append(None)

    df[COL_T_IMPOSTOS] = pd.to_numeric(res, errors="coerce")
    return df


# ── [U] CPV DEV ───────────────────────────────────────────────────────────────

def calcular_u_cpv(df: pd.DataFrame, sufixo: str) -> pd.DataFrame:
    """
    =SEERRO((N3+O3)*R3;"")
    N = Preço de custo  |  O = Custo de MP  |  R = Qtde (col idx 17, espelho)
    """
    cols = COLUNAS[sufixo]
    for chave in ["preco_custo", "custo_mp"]:
        if cols[chave] not in df.columns:
            raise ValueError(f"Coluna '{cols[chave]}' ausente.")

    df = df.copy()
    col_r = _idx_col(df, 6)
    if col_r is None:
        print(f"[!] Col R (idx 17) não encontrada em ESC {sufixo.upper()}. U será NaN.")

    res = []
    for _, row in df.iterrows():
        try:
            n = _get(row, cols["preco_custo"])
            o = _get(row, cols["custo_mp"])
            r = _get(row, col_r) if col_r else 0.0
            res.append((n + o) * r)
        except Exception:
            res.append(None)

    df[COL_U_CPV] = pd.to_numeric(res, errors="coerce")
    return df
