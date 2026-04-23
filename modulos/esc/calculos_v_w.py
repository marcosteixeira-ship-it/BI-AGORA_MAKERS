"""
modulos/esc/calculos_v_w.py
Fórmulas V e W da aba ESC (Devoluções):
  [V] MÊS           PROCV(MÊS(A), META_FAT!A:B, 2, 0)
  [W] REPRESENTANTE PROCV(P, FAT_DEV!B:D, 3, 0)
"""

import pandas as pd
import numpy as np
from modulos.esc.config import (
    COLUNAS, MESES_PT,
    FAT_DEV_COL_NOTA, FAT_DEV_COL_REP,
    COL_V_MES, COL_W_REPR,
)


# ── [V] MÊS ──────────────────────────────────────────────────────────────────

def calcular_v_mes(df: pd.DataFrame, sufixo: str) -> pd.DataFrame:
    """
    =SEERRO(PROCV(MÊS(A3); META_FAT!A:B; 2; 0);"")
    A = Data de entrada
    META_FAT embutida em MESES_PT: {1..12 → nome PT-BR}
    """
    col_a = COLUNAS[sufixo]["data_entrada"]
    if col_a not in df.columns:
        raise ValueError(f"Coluna '{col_a}' ausente.")

    df = df.copy()

    def _mes(data):
        try:
            return MESES_PT.get(pd.Timestamp(data).month) if pd.notna(data) else None
        except Exception:
            return None

    df[COL_V_MES] = df[col_a].apply(_mes)
    return df


# ── [W] REPRESENTANTE ─────────────────────────────────────────────────────────

def calcular_w_representante(
    df: pd.DataFrame,
    sufixo: str,
    df_fat_dev: pd.DataFrame,
) -> pd.DataFrame:
    """
    =SEERRO(PROCV(P3; FAT_DEV!B:D; 3; 0);"")
    P  = Nota fiscal de devolução
    B  = Nota (Número) ← chave de busca
    D  = Representante  ← retorno (3ª coluna de B:D)

    df_fat_dev é carregado por leitura.ler_fat_dev().
    """
    col_p = COLUNAS[sufixo]["nota_dev"]
    if col_p not in df.columns:
        raise ValueError(f"Coluna '{col_p}' ausente.")

    df = df.copy()

    if df_fat_dev.empty or FAT_DEV_COL_NOTA not in df_fat_dev.columns:
        print(f"[!] FAT_DEV {sufixo.upper()} vazio — coluna W ficará NaN.")
        df[COL_W_REPR] = np.nan
        return df

    # Monta dict: Nota → Representante (primeiro match, como PROCV exato)
    lookup = (
        df_fat_dev
        .dropna(subset=[FAT_DEV_COL_NOTA, FAT_DEV_COL_REP])
        .drop_duplicates(subset=[FAT_DEV_COL_NOTA], keep="first")
        .set_index(FAT_DEV_COL_NOTA)[FAT_DEV_COL_REP]
        .to_dict()
    )

    def _procv(nota):
        try:
            return lookup.get(float(nota)) if pd.notna(nota) else None
        except Exception:
            return None

    df[COL_W_REPR] = df[col_p].apply(_procv)
    return df
