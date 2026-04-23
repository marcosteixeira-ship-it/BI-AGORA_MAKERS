"""
core/helpers.py
Funções utilitárias de parsing e formatação compartilhadas por todos os módulos.
"""

import pandas as pd
import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
#  Parsing de tipos
# ─────────────────────────────────────────────────────────────────────────────

def parse_numero_br(valor) -> float:
    """
    Converte string em formato brasileiro para float.
      '12,0000'  → 12.0
      '1.234,56' → 1234.56
      NaN / ''   → 0.0
    """
    if pd.isna(valor):
        return 0.0
    try:
        return float(valor)
    except (ValueError, TypeError):
        pass
    try:
        return float(str(valor).strip().replace(".", "").replace(",", "."))
    except Exception:
        return 0.0


def parse_data(valor) -> pd.Timestamp:
    """
    Converte para Timestamp.
    Aceita: datetime, string 'dd/mm/yyyy', serial numérico Excel.
    """
    if pd.isna(valor):
        return pd.NaT
    if hasattr(valor, "date"):
        return pd.Timestamp(valor)
    if isinstance(valor, (int, float)):
        try:
            return pd.Timestamp("1899-12-30") + pd.Timedelta(days=int(valor))
        except Exception:
            return pd.NaT
    try:
        return pd.to_datetime(str(valor).strip(), format="%d/%m/%Y", errors="coerce")
    except Exception:
        return pd.NaT


def formatar_item(valor) -> str:
    """
    Formata código de item removendo '.0' desnecessário.
      200449.0      → '200449'
      501926.0001   → '501926.0001'
    """
    if pd.isna(valor):
        return ""
    s = str(valor).strip()
    if s.endswith(".0") and s[:-2].isdigit():
        return s[:-2]
    return s


# ─────────────────────────────────────────────────────────────────────────────
#  Formatação de saída
# ─────────────────────────────────────────────────────────────────────────────

def brl(v: float, compact: bool = True) -> str:
    """Formata valor em Real Brasileiro."""
    if compact:
        if abs(v) >= 1_000_000:
            return f"R$ {v / 1_000_000:.2f}M"
        if abs(v) >= 1_000:
            return f"R$ {v / 1_000:.1f}K"
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(v: float) -> str:
    return f"{v:.1f}%"
