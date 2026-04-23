"""
leitura_ped.py — Etapa 1: Leitura do arquivo pdc002omp.csv.

Responsabilidade:
  - Ler o arquivo pdc002omp.csv (pedidos OMP)
  - Converter tipos (números BR, datas)
  - Retornar DataFrame limpo, sem nenhum cálculo de negócio

Nota sobre o CSV:
  O arquivo pdc002omp.csv é gerado pelo ERP com separador por tabulação
  e encoding latin-1. Não possui coluna "Empresa" — o cabeçalho real
  começa na primeira linha.
"""

import pandas as pd
import numpy as np
import os
from modulos.ped.config import (
    ARQUIVO_PDC_OMP, ARQUIVO_PDC_MTC, ENCODING, SEPARADOR,
    COLUNAS_NUMERICAS, COLUNAS_DATA, COLUNAS,
    NOME_EMPRESA, COLUNAS_RENAME_MTC_PED,
)


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers de conversão
# ─────────────────────────────────────────────────────────────────────────────

def _parse_numero_br(valor) -> float:
    """
    Converte string no formato brasileiro para float.
      '1.234,56' → 1234.56
      '12,0000'  → 12.0
      NaN / ''   → 0.0
    """
    if pd.isna(valor):
        return 0.0
    try:
        # Se já vier como número (Excel lê direto como float)
        return float(valor)
    except (ValueError, TypeError):
        pass
    try:
        return float(str(valor).strip().replace(".", "").replace(",", "."))
    except (ValueError, AttributeError):
        return 0.0


def _parse_data(valor) -> pd.Timestamp:
    """
    Converte para Timestamp.
    Aceita: datetime já parseado (Excel), string 'dd/mm/yyyy', serial Excel.
    """
    if pd.isna(valor):
        return pd.NaT
    if isinstance(valor, (pd.Timestamp, pd.DatetimeTZDtype)):
        return pd.Timestamp(valor)
    if hasattr(valor, 'date'):        # datetime.datetime
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


# ─────────────────────────────────────────────────────────────────────────────
#  Leitura principal
# ─────────────────────────────────────────────────────────────────────────────

def _ler_pdc(pasta: str, sufixo: str) -> pd.DataFrame:
    """
    Lê um arquivo PDC (OMP ou MTC) e retorna DataFrame limpo.

    Parâmetros
    ----------
    pasta  : pasta onde está o arquivo
    sufixo : 'omp' ou 'mtc'
    """
    arquivo = ARQUIVO_PDC_OMP if sufixo == "omp" else ARQUIVO_PDC_MTC
    caminho = os.path.join(pasta, arquivo)

    if not os.path.exists(caminho):
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}\n"
            f"Coloque '{arquivo}' na pasta '{os.path.abspath(pasta)}'."
        )

    df = pd.read_csv(caminho, encoding=ENCODING, sep=SEPARADOR,
                     low_memory=False, dtype=str)

    # Limpa nomes de colunas
    df.columns = [str(c).strip() for c in df.columns]

    # Normaliza colunas MTC para o padrão OMP
    if sufixo == "mtc":
        df.rename(columns=COLUNAS_RENAME_MTC_PED, inplace=True)

    # Remove linhas completamente vazias
    df = df.dropna(how="all").reset_index(drop=True)

    # ── Conversão de tipos ────────────────────────────────────────────────────
    for col in COLUNAS_NUMERICAS:
        if col in df.columns:
            df[col] = df[col].apply(_parse_numero_br)

    for col in COLUNAS_DATA:
        if col in df.columns:
            df[col] = df[col].apply(_parse_data)

    # ── Metadados ─────────────────────────────────────────────────────────────
    mapa_empresa = {"omp": "My City", "mtc": "Metalco"}
    df["_sufixo"]       = sufixo
    df["_empresa"]      = mapa_empresa.get(sufixo, sufixo)
    df["_nome_empresa"] = NOME_EMPRESA.get(sufixo, "")

    return df


def ler_pdc_omp(pasta: str = ".") -> pd.DataFrame:
    """Lê o arquivo pdc002omp.csv."""
    return _ler_pdc(pasta, "omp")


def ler_pdc_mtc(pasta: str = ".") -> pd.DataFrame:
    """Lê o arquivo pdc002mtc.csv."""
    return _ler_pdc(pasta, "mtc")


def ler_ambos_pdc(pasta: str = ".") -> dict:
    """
    Lê OMP e MTC separadamente.

    Retorna
    -------
    {'omp': DataFrame, 'mtc': DataFrame}
    Omite a chave se o arquivo não existir.
    """
    resultado = {}
    for sufixo in ("omp", "mtc"):
        try:
            resultado[sufixo] = _ler_pdc(pasta, sufixo)
            arquivo = ARQUIVO_PDC_OMP if sufixo == "omp" else ARQUIVO_PDC_MTC
            print(f"[OK] PDC {sufixo.upper()} carregado - {len(resultado[sufixo]):,} linhas")
        except FileNotFoundError as e:
            print(f"[!] PDC {sufixo.upper()} não encontrado: {e}")
    return resultado


# ─────────────────────────────────────────────────────────────────────────────
#  Diagnóstico
# ─────────────────────────────────────────────────────────────────────────────

def diagnosticar(df: pd.DataFrame) -> None:
    """Imprime resumo básico para conferência."""
    col_data  = COLUNAS["data_emissao"]
    col_razao = COLUNAS["razao_social"]
    sep = "─" * 52

    print(f"\n{sep}")
    print("  pdc002omp — Leitura")
    print(sep)
    print(f"  Linhas    : {len(df):,}")
    print(f"  Colunas   : {len(df.columns)}")
    print(f"  Empresa   : {df['_empresa'].iloc[0] if '_empresa' in df.columns else 'N/A'}")

    if col_data in df.columns:
        dmin = df[col_data].min()
        dmax = df[col_data].max()
        print(f"  Período   : {dmin:%d/%m/%Y} → {dmax:%d/%m/%Y}")

    if col_razao in df.columns:
        print(f"  Clientes  : {df[col_razao].nunique():,} distintos")

    col_qtde = COLUNAS["qtde_solicitada"]
    col_vunit = COLUNAS["valor_unit"]
    if col_qtde in df.columns and col_vunit in df.columns:
        carteira = (
            (df[col_qtde] - df[COLUNAS["qtde_cancelada"]]) * df[col_vunit]
        ).sum()
        print(f"  Carteira  : R$ {carteira:,.2f} (sem filtro IC)")

    print(f"{sep}\n")
