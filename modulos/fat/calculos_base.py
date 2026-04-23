"""
modulos/fat/calculos_base.py
Funções base do módulo FAT:
  - Registro do lookup ESC (devoluções)
  - Helpers internos de exclusão e validação
  - Flag Intercompany
  - Fórmula [AI] QTDE DEV + [1] QTDE LÍQUIDA
"""

import pandas as pd
import numpy as np
from modulos.fat.config import (
    COLUNAS, COL_INTERCOMPANY,
    COL_QTDE_LIQUIDA, COL_QTDE_DEVOLUCAO,
)

# ── Lookup ESC ────────────────────────────────────────────────────────────────
_ESC_LOOKUP: dict = {}


def set_esc_lookup(lookup_omp: dict, lookup_mtc: dict) -> None:
    """
    Registra lookups do ESC para as fórmulas de devolução.
    Chamar antes de processar().
    """
    global _ESC_LOOKUP
    _ESC_LOOKUP = {"omp": lookup_omp, "mtc": lookup_mtc}


# ── Helpers internos ──────────────────────────────────────────────────────────

def _get(row, chave: str, default: float = 0.0) -> float:
    nome = COLUNAS.get(chave, chave)
    v = row.get(nome, default)
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return default
    try:
        return float(v)
    except (ValueError, TypeError):
        return default


def _excluir(razao: str, empresa_ref: str, flag: str) -> bool:
    """True → linha excluída (própria empresa ou IC)."""
    r, e, f = (str(x).strip().upper() for x in (razao, empresa_ref, flag))
    if r == e:
        return True
    if f == "SIM" and r in ("METALCO DO BRASIL LTDA", "OMP DO BRASIL LTDA"):
        return True
    return False


def _excluir_ic_only(razao: str, flag: str) -> bool:
    """IC only — sem testar $E$2 (usado em RL e CPV)."""
    r, f = str(razao).strip().upper(), str(flag).strip().upper()
    return f == "SIM" and r in ("METALCO DO BRASIL LTDA", "OMP DO BRASIL LTDA")


def _checar(df: pd.DataFrame, chaves: list) -> None:
    ausentes = [
        f"'{COLUNAS.get(c,c)}' (chave '{c}')"
        for c in chaves if COLUNAS.get(c, c) not in df.columns
    ] + [
        f"'{col}'"
        for col in ["_nome_empresa", "_sufixo", COL_INTERCOMPANY]
        if col not in df.columns
    ]
    if ausentes:
        raise ValueError(f"Colunas ausentes: {ausentes}")


# ── Flag Intercompany ─────────────────────────────────────────────────────────

def aplicar_flag_intercompany(df: pd.DataFrame, valor_flag: str = "NAO") -> pd.DataFrame:
    """Adiciona COL_INTERCOMPANY em todas as linhas."""
    df = df.copy()
    v = str(valor_flag).strip().upper().replace("NÃO", "NAO")
    if v not in ("SIM", "NAO"):
        raise ValueError(f"Flag inválida: '{valor_flag}'. Use 'SIM' ou 'NAO'.")
    df[COL_INTERCOMPANY] = v
    return df


# ── [AI] QTDE DEV + [1] QTDE LÍQUIDA ─────────────────────────────────────────

def calcular_qtde(df: pd.DataFrame) -> pd.DataFrame:
    """
    [AI] Qtde Devolvida = SEERRO(PROCV(CONCAT(Nota,"-",Item); ESC!Q:R; 2; 0); 0)
    [1]  Qtde Líquida   =
         SE(E=$E$2; "";
         SE(E(AZ="SIM"; E="METALCO DO BRASIL LTDA"); "";
         SE(E(AZ="SIM"; E="OMP DO BRASIL LTDA"); "";
         I - AI)))
    """
    _checar(df, ["razao_social", "qtde_faturada"])
    df = df.copy()
    res_liq, res_dev = [], []

    col_razao = COLUNAS["razao_social"]
    col_nota  = COLUNAS["nota"]
    col_item  = COLUNAS["item"]

    def _chave(row):
        nota = str(row.get(col_nota, "")).strip()
        item = str(row.get(col_item, "")).strip()
        if item.endswith(".0") and item[:-2].isdigit():
            item = item[:-2]
        return f"{nota}-{item}"

    for _, row in df.iterrows():
        razao   = str(row[col_razao]).strip().upper()
        empresa = str(row["_nome_empresa"]).strip().upper()
        ic_flag = str(row[COL_INTERCOMPANY]).strip().upper()

        # SE(E=$E$2; "")
        if razao == empresa:
            res_liq.append(None); res_dev.append(0.0)
            continue

        # SE(E(AZ="SIM"; E="METALCO DO BRASIL LTDA"); "")
        if ic_flag == "SIM" and razao == "METALCO DO BRASIL LTDA":
            res_liq.append(None); res_dev.append(0.0)
            continue

        # SE(E(AZ="SIM"; E="OMP DO BRASIL LTDA"); "")
        if ic_flag == "SIM" and razao == "OMP DO BRASIL LTDA":
            res_liq.append(None); res_dev.append(0.0)
            continue

        # I - AI
        sufixo   = str(row.get("_sufixo", "omp")).lower()
        qtde_dev = float(_ESC_LOOKUP.get(sufixo, {}).get(_chave(row), 0) or 0)
        qtde_fat = _get(row, "qtde_faturada")
        res_liq.append(qtde_fat - qtde_dev)
        res_dev.append(qtde_dev)

    df[COL_QTDE_LIQUIDA]   = pd.to_numeric(res_liq, errors="coerce")
    df[COL_QTDE_DEVOLUCAO] = res_dev
    return df
