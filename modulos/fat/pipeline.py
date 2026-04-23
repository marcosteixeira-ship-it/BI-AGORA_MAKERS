"""
modulos/fat/pipeline.py
Entry point do módulo FAT.
Chama leitura → processamento → retorna dict pronto para a UI.
"""

import os
import pandas as pd
from modulos.fat.leitura import ler_ambos, diagnosticar
from modulos.fat.processamento import processar, diagnosticar_processamento
from modulos.fat.config import ARQUIVO_OMP, ARQUIVO_MTC


def executar(
    pasta: str = ".",
    flag_intercompany_omp: str = "NAO",
    flag_intercompany_mtc: str = "NAO",
    verbose: bool = True,
) -> dict:
    """
    Executa leitura + processamento do FAT para OMP e MTC.

    Retorna
    -------
    {
        'omp'        : DataFrame My City processado
        'mtc'        : DataFrame Metalco processado
        'consolidado': OMP + MTC juntos
        'flags'      : {'omp': ..., 'mtc': ...}
    }
    """
    if verbose:
        print(f"\n{'='*55}")
        print("  PIPELINE FAT — Iniciando")
        print(f"  Pasta: {os.path.abspath(pasta)}")
        print(f"{'='*55}\n")

    brutos = ler_ambos(pasta=pasta)
    if verbose:
        for nome, df in brutos.items():
            diagnosticar(df, nome.upper())

    flags = {"omp": flag_intercompany_omp, "mtc": flag_intercompany_mtc}
    processados = {}

    for sufixo, df_bruto in brutos.items():
        df_proc = processar(df_bruto, flag_intercompany=flags[sufixo])
        processados[sufixo] = df_proc
        if verbose:
            diagnosticar_processamento(df_proc)

    frames = list(processados.values())
    consolidado = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    if verbose:
        print(f"{'='*55}")
        print(f"  PIPELINE FAT — Concluído  ({len(consolidado):,} linhas totais)")
        print(f"{'='*55}\n")

    return {
        "omp":         processados.get("omp", pd.DataFrame()),
        "mtc":         processados.get("mtc", pd.DataFrame()),
        "consolidado": consolidado,
        "flags":       flags,
    }


def arquivos_disponiveis(pasta: str = ".") -> dict:
    return {
        "omp": os.path.exists(os.path.join(pasta, ARQUIVO_OMP)),
        "mtc": os.path.exists(os.path.join(pasta, ARQUIVO_MTC)),
    }
