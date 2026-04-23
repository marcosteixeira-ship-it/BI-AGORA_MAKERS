"""
modulos/esc/pipeline.py
Entry point do módulo ESC (Devoluções).
"""

import os
import pandas as pd
from modulos.esc.leitura import ler_ambos, ler_fat_dev_ambos, diagnosticar
from modulos.esc.processamento import processar, diagnosticar_processamento
from modulos.esc.config import (
    ARQUIVO_ESC, ARQUIVO_FAT_DEV,
    COL_T_IMPOSTOS, COL_U_CPV, COLUNAS,
)


def executar(pasta: str = ".", verbose: bool = True) -> dict:
    """
    Executa leitura + processamento ESC para OMP e MTC.

    Retorna
    -------
    {
        'omp'        : DataFrame OMP processado
        'mtc'        : DataFrame MTC processado
        'consolidado': OMP + MTC juntos
        'resumo'     : {'omp': {...}, 'mtc': {...}}
    }
    """
    if verbose:
        print(f"\n{'='*55}")
        print("  PIPELINE ESC (Devoluções) — Iniciando")
        print(f"  Pasta: {os.path.abspath(pasta)}")
        print(f"{'='*55}\n")

    dados_brutos = ler_ambos(pasta=pasta)
    fat_devs     = ler_fat_dev_ambos(pasta=pasta)

    if verbose:
        for suf, df in dados_brutos.items():
            diagnosticar(df, f"ESC {suf.upper()}")

    processados = {}
    for sufixo, df_bruto in dados_brutos.items():
        df_proc = processar(df_bruto, sufixo, fat_devs.get(sufixo, pd.DataFrame()))
        processados[sufixo] = df_proc
        if verbose:
            diagnosticar_processamento(df_proc, sufixo)

    frames = list(processados.values())
    consolidado = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    resumo = {}
    for suf, df in processados.items():
        col_nota = COLUNAS[suf]["nota_dev"]
        resumo[suf] = {
            "linhas":          len(df),
            "valor_total_dev": df["Valor total"].sum() if "Valor total" in df.columns else 0,
            "impostos_dev":    df[COL_T_IMPOSTOS].sum(skipna=True) if COL_T_IMPOSTOS in df.columns else 0,
            "cpv_dev":         df[COL_U_CPV].sum(skipna=True) if COL_U_CPV in df.columns else 0,
            "notas_distintas": df[col_nota].nunique() if col_nota in df.columns else 0,
        }

    if verbose:
        print(f"{'='*55}")
        print("  PIPELINE ESC — Concluído")
        for suf, r in resumo.items():
            print(f"\n  [{suf.upper()}]")
            print(f"    Linhas          : {r['linhas']:,}")
            print(f"    Valor devolvido : R$ {r['valor_total_dev']:,.2f}")
            print(f"    Impostos dev.   : R$ {r['impostos_dev']:,.2f}")
            print(f"    CPV dev.        : R$ {r['cpv_dev']:,.2f}")
        print(f"{'='*55}\n")

    return {
        "omp":         processados.get("omp", pd.DataFrame()),
        "mtc":         processados.get("mtc", pd.DataFrame()),
        "consolidado": consolidado,
        "resumo":      resumo,
    }


def arquivos_disponiveis(pasta: str = ".") -> dict:
    resultado = {}
    for suf in ("omp", "mtc"):
        resultado[f"esc_{suf}"]     = os.path.exists(os.path.join(pasta, ARQUIVO_ESC[suf]))
        resultado[f"fat_dev_{suf}"] = os.path.exists(os.path.join(pasta, ARQUIVO_FAT_DEV[suf]))
    return resultado


def build_esc_lookup(dados_esc: dict) -> tuple[dict, dict]:
    """
    Constrói os lookups {chave_nota_item: qtde_devolvida} para OMP e MTC.
    Usado pelo pipeline FAT para registrar set_esc_lookup().

    Parâmetros
    ----------
    dados_esc : resultado de executar()

    Retorna
    -------
    (lookup_omp, lookup_mtc)
    """
    from modulos.esc.config import COL_Q_CONCATENAR, COLUNAS

    def _build(df: pd.DataFrame, sufixo: str) -> dict:
        if df.empty or COL_Q_CONCATENAR not in df.columns:
            return {}
        col_qtde = COLUNAS[sufixo]["qtde"]   # "Qtde" — coluna G do CSV (R no Excel)
        if col_qtde not in df.columns:
            return {}
        return dict(zip(
            df[COL_Q_CONCATENAR].astype(str),
            pd.to_numeric(df[col_qtde], errors="coerce").fillna(0),
        ))

    return (
        _build(dados_esc.get("omp", pd.DataFrame()), "omp"),
        _build(dados_esc.get("mtc", pd.DataFrame()), "mtc"),
    )
