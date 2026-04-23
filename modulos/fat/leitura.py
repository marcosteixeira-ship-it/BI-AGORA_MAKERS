"""
leitura.py — Etapa 1: Leitura bruta dos arquivos CSV.

Responsabilidade:
  - Ler os arquivos ftc002omp.csv e ftc002mtc.csv
  - Converter tipos (números BR, datas)
  - Adicionar coluna de identificação da empresa
  - Retornar DataFrames limpos, sem nenhum cálculo de negócio

Não faz cálculos de KPI nem aplica regras de negócio.
"""

import pandas as pd
import numpy as np
import os
from modulos.fat.config import (
    ARQUIVO_OMP, ARQUIVO_MTC, ENCODING, SEPARADOR,
    COLUNAS_NUMERICAS, COLUNAS_DATA, NOME_EMPRESA, COLUNAS_RENAME_MTC,
)


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers de conversão
# ─────────────────────────────────────────────────────────────────────────────

def _converter_numero_br(valor) -> float:
    """
    Converte string em formato brasileiro para float.
    Exemplos:
      '12,0000'    → 12.0
      '1.234,56'   → 1234.56
      '0'          → 0.0
      NaN / ''     → 0.0
    """
    try:
        return float(str(valor).strip().replace(".", "").replace(",", "."))
    except (ValueError, AttributeError):
        return 0.0


def _converter_data(valor) -> pd.Timestamp:
    """
    Converte string 'dd/mm/yyyy' ou serial Excel para Timestamp.
    Retorna NaT se não conseguir converter.
    """
    # Serial numérico do Excel (ex: 46030)
    if isinstance(valor, (int, float)):
        try:
            if not np.isnan(float(valor)):
                return pd.Timestamp("1899-12-30") + pd.Timedelta(days=int(valor))
        except (ValueError, TypeError):
            pass
        return pd.NaT

    # String no formato brasileiro
    try:
        return pd.to_datetime(str(valor).strip(), format="%d/%m/%Y", errors="coerce")
    except Exception:
        return pd.NaT


# ─────────────────────────────────────────────────────────────────────────────
#  Leitura individual
# ─────────────────────────────────────────────────────────────────────────────

def ler_csv(caminho: str, sufixo_empresa: str) -> pd.DataFrame:
    """
    Lê um arquivo CSV de faturamento e retorna DataFrame limpo.

    Parâmetros
    ----------
    caminho         : caminho completo para o arquivo .csv
    sufixo_empresa  : 'omp' ou 'mtc' — usado para identificar a empresa

    Retorna
    -------
    pd.DataFrame com:
      - Todas as colunas originais do CSV
      - Colunas numéricas já convertidas para float
      - Colunas de data já convertidas para Timestamp
      - Coluna '_empresa'       : 'My City' ou 'Metalco'
      - Coluna '_sufixo'        : 'omp' ou 'mtc'
      - Coluna '_nome_empresa'  : nome da empresa conforme config.NOME_EMPRESA
    """
    if not os.path.exists(caminho):
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}\n"
            f"Coloque o arquivo na mesma pasta que este script."
        )

    # ── Leitura bruta ─────────────────────────────────────────────────────────
    df = pd.read_csv(
        caminho,
        encoding=ENCODING,
        sep=SEPARADOR,
        low_memory=False,
        dtype=str,          # tudo como string primeiro — convertemos abaixo
    )

    # Limpa espaços nos nomes de colunas
    df.columns = [c.strip() for c in df.columns]

    # Normaliza nomes de colunas específicos do MTC para o padrão OMP
    if sufixo_empresa == "mtc":
        df.rename(columns=COLUNAS_RENAME_MTC, inplace=True)

    # Remove linhas completamente vazias
    df = df.dropna(how="all").reset_index(drop=True)

    # ── Conversão de tipos ────────────────────────────────────────────────────
    for col in COLUNAS_NUMERICAS:
        if col in df.columns:
            df[col] = df[col].apply(_converter_numero_br)

    for col in COLUNAS_DATA:
        if col in df.columns:
            df[col] = df[col].apply(_converter_data)

    # ── Metadados da empresa ──────────────────────────────────────────────────
    mapa_empresa = {"omp": "My City", "mtc": "Metalco"}
    df["_empresa"]      = mapa_empresa.get(sufixo_empresa, sufixo_empresa)
    df["_sufixo"]       = sufixo_empresa
    df["_nome_empresa"] = NOME_EMPRESA.get(sufixo_empresa, "")

    return df


# ─────────────────────────────────────────────────────────────────────────────
#  Leitura combinada
# ─────────────────────────────────────────────────────────────────────────────

def ler_omp(pasta: str = ".") -> pd.DataFrame:
    """Lê o arquivo ftc002omp.csv."""
    caminho = os.path.join(pasta, ARQUIVO_OMP)
    return ler_csv(caminho, "omp")


def ler_mtc(pasta: str = ".") -> pd.DataFrame:
    """Lê o arquivo ftc002mtc.csv."""
    caminho = os.path.join(pasta, ARQUIVO_MTC)
    return ler_csv(caminho, "mtc")


def ler_ambos(pasta: str = ".") -> dict[str, pd.DataFrame]:
    """
    Lê OMP e MTC separadamente.

    Retorna
    -------
    {
        'omp': DataFrame com dados de My City,
        'mtc': DataFrame com dados de Metalco,
    }
    """
    resultado = {}

    try:
        resultado["omp"] = ler_omp(pasta)
        print(f"[OK] OMP carregado - {len(resultado['omp']):,} linhas")
    except FileNotFoundError as e:
        print(f"[!] OMP nao encontrado: {e}")

    try:
        resultado["mtc"] = ler_mtc(pasta)
        print(f"[OK] MTC carregado - {len(resultado['mtc']):,} linhas")
    except FileNotFoundError as e:
        print(f"[!] MTC nao encontrado: {e}")

    return resultado


def consolidar(dados: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Junta OMP e MTC em um único DataFrame consolidado.

    Parâmetros
    ----------
    dados : dict retornado por ler_ambos()

    Retorna
    -------
    DataFrame único com coluna '_empresa' para diferenciar origem.
    """
    frames = list(dados.values())
    if not frames:
        raise ValueError("Nenhum dado carregado para consolidar.")

    df = pd.concat(frames, ignore_index=True)
    print(f"[OK] Consolidado - {len(df):,} linhas no total")
    return df


# ─────────────────────────────────────────────────────────────────────────────
#  Diagnóstico rápido
# ─────────────────────────────────────────────────────────────────────────────

def diagnosticar(df: pd.DataFrame, nome: str = "DataFrame") -> None:
    """Imprime resumo básico do DataFrame para conferência."""
    print(f"\n{'-'*50}")
    print(f"  {nome}")
    print(f"{'-'*50}")
    print(f"  Linhas    : {len(df):,}")
    print(f"  Colunas   : {len(df.columns)}")
    print(f"  Empresas  : {df['_empresa'].unique().tolist() if '_empresa' in df.columns else 'N/A'}")
    if "Data de emissão" in df.columns:
        dmin = df["Data de emissão"].min()
        dmax = df["Data de emissão"].max()
        print(f"  Periodo   : {dmin:%d/%m/%Y} -> {dmax:%d/%m/%Y}")
    if "Valor total" in df.columns:
        print(f"  Fat. Total: R$ {df['Valor total'].sum():,.2f}")
    print(f"{'-'*50}\n")
