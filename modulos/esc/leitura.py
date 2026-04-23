"""
leitura_esc.py — Etapa 1: Leitura dos arquivos de devolução.

Lê:
  esc002omp.csv  →  Devoluções My City
  esc002mtc.csv  →  Devoluções Metalco
  ftc001omp.csv  →  Tabela FAT_DEV OMP (referência para PROCV col W)
  ftc001mtc.csv  →  Tabela FAT_DEV MTC (referência para PROCV col W)
"""

import pandas as pd
import numpy as np
import os
from modulos.esc.config import (
    ARQUIVO_ESC, ARQUIVO_FAT_DEV,
    ENCODING, SEPARADOR, COLUNAS, COLUNAS_NUMERICAS, COLUNAS_DATA,
    EMPRESA_NOME, FAT_DEV_COL_NOTA, FAT_DEV_COL_REP,
)


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _parse_numero(valor) -> float:
    """Converte string BR ou float/int para float. NaN/vazio → 0.0."""
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


def _parse_data(valor) -> pd.Timestamp:
    """Converte para Timestamp. Aceita datetime, string dd/mm/yyyy, serial Excel."""
    if pd.isna(valor):
        return pd.NaT
    if hasattr(valor, "date"):         # datetime.datetime
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


def _formatar_item(valor) -> str:
    """
    Formata o código do Item para string sem '.0' desnecessário.
    Ex: 200449.0 → '200449', '501926.0001' → '501926.0001'
    """
    if pd.isna(valor):
        return ""
    s = str(valor).strip()
    # Remove .0 apenas quando é um número inteiro representado como float
    if s.endswith(".0") and s[:-2].isdigit():
        return s[:-2]
    return s


# ─────────────────────────────────────────────────────────────────────────────
#  Leitura ESC
# ─────────────────────────────────────────────────────────────────────────────

def ler_esc(sufixo: str, pasta: str = ".") -> pd.DataFrame:
    """
    Lê um arquivo esc002{sufixo}.csv e retorna DataFrame limpo.

    Parâmetros
    ----------
    sufixo : 'omp' ou 'mtc'
    pasta  : pasta onde está o arquivo

    Retorna
    -------
    pd.DataFrame com:
      - Colunas originais do CSV (A..P)
      - Colunas numéricas convertidas para float
      - Colunas de data convertidas para Timestamp
      - Coluna _item_fmt : Item formatado (sem .0 desnecessário)
      - Coluna _sufixo   : 'omp' ou 'mtc'
      - Coluna _empresa  : 'My City' ou 'Metalco'
    """
    if sufixo not in ("omp", "mtc"):
        raise ValueError(f"sufixo deve ser 'omp' ou 'mtc', recebeu: '{sufixo}'")

    arquivo = ARQUIVO_ESC[sufixo]
    caminho = os.path.join(pasta, arquivo)

    if not os.path.exists(caminho):
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}\n"
            f"Coloque '{arquivo}' na pasta '{os.path.abspath(pasta)}'."
        )

    # Leitura bruta — tudo como string
    df = pd.read_csv(caminho, encoding=ENCODING, sep=SEPARADOR,
                     low_memory=False, dtype=str)
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(how="all").reset_index(drop=True)

    # Converte numéricos
    for col in COLUNAS_NUMERICAS:
        if col in df.columns:
            df[col] = df[col].apply(_parse_numero)

    # Converte datas
    for col in COLUNAS_DATA:
        if col in df.columns:
            df[col] = df[col].apply(_parse_data)

    # Item formatado (para uso na fórmula Q)
    col_item = COLUNAS[sufixo]["item"]
    if col_item in df.columns:
        df["_item_fmt"] = df[col_item].apply(_formatar_item)
    else:
        df["_item_fmt"] = ""

    # Metadados
    df["_sufixo"]  = sufixo
    df["_empresa"] = EMPRESA_NOME[sufixo]

    return df


def ler_omp(pasta: str = ".") -> pd.DataFrame:
    """Lê esc002omp.csv."""
    return ler_esc("omp", pasta)


def ler_mtc(pasta: str = ".") -> pd.DataFrame:
    """Lê esc002mtc.csv."""
    return ler_esc("mtc", pasta)


def ler_ambos(pasta: str = ".") -> dict:
    """
    Lê OMP e MTC. Retorna {'omp': df, 'mtc': df}.
    Ignora silenciosamente arquivos ausentes (imprime aviso).
    """
    resultado = {}
    for sufixo in ("omp", "mtc"):
        try:
            df = ler_esc(sufixo, pasta)
            resultado[sufixo] = df
            print(f"[OK] ESC {sufixo.upper()} carregado - {len(df):,} linhas")
        except FileNotFoundError as e:
            print(f"[!] {e}")
    return resultado


# ─────────────────────────────────────────────────────────────────────────────
#  Leitura FAT_DEV (tabela de referência para PROCV coluna W)
# ─────────────────────────────────────────────────────────────────────────────

def ler_fat_dev(sufixo: str, pasta: str = ".") -> pd.DataFrame:
    """
    Lê a tabela FAT_DEV usada como referência no PROCV da coluna W.

    Arquivos:
      ftc001omp.csv  →  FAT_DEV_OMP
      ftc001mtc.csv  →  FAT_DEV_MTC

    Estrutura esperada (colunas B:D do Excel → índices 1, 2, 3):
      col 'Nota (Número)'                         ← chave do PROCV
      col 'Cliente - Razão social (Cliente)'
      col 'Representante - Razão social (Representante)'  ← retorno

    Se o arquivo não existir, retorna DataFrame vazio com aviso.
    """
    arquivo = ARQUIVO_FAT_DEV[sufixo]
    caminho = os.path.join(pasta, arquivo)

    if not os.path.exists(caminho):
        print(
            f"[!] FAT_DEV {sufixo.upper()} não encontrado: {caminho}\n"
            f"    Coluna W (Representante) ficará vazia.\n"
            f"    Coloque '{arquivo}' na pasta '{os.path.abspath(pasta)}'."
        )
        return pd.DataFrame(columns=[FAT_DEV_COL_NOTA, FAT_DEV_COL_REP])

    df = pd.read_csv(caminho, encoding=ENCODING, sep=SEPARADOR,
                     low_memory=False, dtype=str)
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(how="all").reset_index(drop=True)

    # Garante que a coluna Nota é numérica (para merge com ESC)
    if FAT_DEV_COL_NOTA in df.columns:
        df[FAT_DEV_COL_NOTA] = pd.to_numeric(
            df[FAT_DEV_COL_NOTA], errors="coerce"
        )

    print(f"[OK] FAT_DEV {sufixo.upper()} carregado - {len(df):,} linhas")
    return df


def ler_fat_dev_ambos(pasta: str = ".") -> dict:
    """Lê FAT_DEV de ambas as empresas. Retorna {'omp': df, 'mtc': df}."""
    return {
        "omp": ler_fat_dev("omp", pasta),
        "mtc": ler_fat_dev("mtc", pasta),
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Diagnóstico
# ─────────────────────────────────────────────────────────────────────────────

def diagnosticar(df: pd.DataFrame, label: str = "") -> None:
    """Imprime resumo básico do DataFrame."""
    sep = "─" * 54
    print(f"\n{sep}")
    print(f"  {label or 'ESC'}")
    print(sep)
    print(f"  Linhas   : {len(df):,}")
    print(f"  Colunas  : {len(df.columns)}")
    if "_empresa" in df.columns:
        print(f"  Empresa  : {df['_empresa'].iloc[0]}")
    if "Data de entrada" in df.columns:
        dt = df["Data de entrada"]
        print(f"  Período  : {dt.min():%d/%m/%Y} → {dt.max():%d/%m/%Y}")
    if "Valor total" in df.columns:
        print(f"  Val. Dev.: R$ {df['Valor total'].sum():,.2f}")
    print(f"{sep}\n")
