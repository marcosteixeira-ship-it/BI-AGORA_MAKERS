"""
modulos/ped/pipeline.py
Entry point do módulo PED (Pedidos).
"""

import os
import pandas as pd
from modulos.ped.leitura import ler_ambos_pdc
from modulos.ped.processamento import processar, diagnosticar_processamento
from modulos.ped.config import (
    ARQUIVO_PDC_OMP, ARQUIVO_PDC_MTC, ANO_REFERENCIA,
    COL_VALOR_VENDA, COL_CONT_CLI, COL_CONT_NOVOS,
)


def executar(
    pasta: str = ".",
    flag_intercompany_omp: str = "NAO",
    flag_intercompany_mtc: str = "NAO",
    ano_ref: int = ANO_REFERENCIA,
    verbose: bool = True,
) -> dict:
    """
    Executa leitura + processamento PED para OMP e MTC.

    Retorna
    -------
    {
        'omp'        : DataFrame OMP processado
        'mtc'        : DataFrame MTC processado
        'consolidado': OMP + MTC juntos
        'flags'      : {'omp': ..., 'mtc': ...}
        'resumos'    : {'omp': {...}, 'mtc': {...}}
        'ano_ref'    : ano usado
    }
    """
    if verbose:
        print(f"\n{'='*55}")
        print("  PIPELINE PED (Pedidos) — Iniciando")
        print(f"  Pasta: {os.path.abspath(pasta)}")
        print(f"  Ano ref.: {ano_ref}")
        print(f"{'='*55}\n")

    brutos = ler_ambos_pdc(pasta=pasta)
    flags  = {"omp": flag_intercompany_omp, "mtc": flag_intercompany_mtc}

    processados = {}
    resumos = {}

    for sufixo, df_bruto in brutos.items():
        df = processar(df_bruto, flag_intercompany=flags[sufixo], ano_ref=ano_ref)
        processados[sufixo] = df

        df_inc = df[df[COL_VALOR_VENDA].notna()]
        resumos[sufixo] = {
            "total_linhas":     len(df),
            "linhas_incluidas": len(df_inc),
            "linhas_excluidas": len(df) - len(df_inc),
            "valor_venda":      df_inc[COL_VALOR_VENDA].sum(),
            "clientes_unicos":  df_inc[COL_CONT_CLI].sum(skipna=True),
            "novos_clientes":   df[COL_CONT_NOVOS].sum(skipna=True),
        }

        if verbose:
            diagnosticar_processamento(df, ano_ref=ano_ref)

    frames = list(processados.values())
    consolidado = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    if verbose:
        total = sum(r["valor_venda"] for r in resumos.values())
        print(f"{'='*55}")
        print(f"  PIPELINE PED — Concluído  Carteira: R$ {total:,.2f}")
        print(f"{'='*55}\n")

    return {
        "omp":         processados.get("omp", pd.DataFrame()),
        "mtc":         processados.get("mtc", pd.DataFrame()),
        "consolidado": consolidado,
        "flags":       flags,
        "resumos":     resumos,
        "ano_ref":     ano_ref,
    }


def arquivos_disponiveis(pasta: str = ".") -> dict:
    return {
        "omp": os.path.exists(os.path.join(pasta, ARQUIVO_PDC_OMP)),
        "mtc": os.path.exists(os.path.join(pasta, ARQUIVO_PDC_MTC)),
    }
