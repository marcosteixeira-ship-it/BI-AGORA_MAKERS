"""
core/constantes.py
Constantes globais compartilhadas entre todos os módulos.
Identidade das empresas, metas mensais e mapeamentos de meses.
"""

# ── Identidade das empresas ───────────────────────────────────────────────────
NOME_EMPRESA = {
    "omp": "OMP DO BRASIL LTDA",     # Razão social — nome fantasia: My City
    "mtc": "METALCO DO BRASIL LTDA",
}

NOME_FANTASIA = {
    "omp": "My City",
    "mtc": "Metalco",
}

PREFIXO_EMPRESA = {
    "omp": "OMP",
    "mtc": "METALCO",
}

NOMES_INTERCOMPANY = [
    "OMP DO BRASIL LTDA",
    "METALCO DO BRASIL LTDA",
]

# ── Metas mensais 2026 (extraídas do Excel ANALISE_FATURAMENTO) ───────────────
METAS_MENSAIS = {
    "My City": {
        1: 1_420_350,    2: 1_538_712.5,  3: 1_657_075,
        4: 1_893_800,    5: 2_130_525,    6: 2_603_975,
        7: 2_485_612.5,  8: 2_367_250,    9: 2_130_525,
        10: 1_893_800,   11: 1_893_800,   12: 1_657_075,
    },
    "Metalco": {
        1: 2_922_150,    2: 3_165_662.5,  3: 3_409_175,
        4: 3_896_200,    5: 4_383_225,    6: 5_357_275,
        7: 5_113_762.5,  8: 4_870_250,    9: 4_383_225,
        10: 3_896_200,   11: 3_896_200,   12: 3_409_175,
    },
}

# ── Meses em português ────────────────────────────────────────────────────────
MESES_PT = {
    1: "JANEIRO",   2: "FEVEREIRO", 3: "MARÇO",
    4: "ABRIL",     5: "MAIO",      6: "JUNHO",
    7: "JULHO",     8: "AGOSTO",    9: "SETEMBRO",
    10: "OUTUBRO",  11: "NOVEMBRO", 12: "DEZEMBRO",
}

# ── Encodings e separadores ───────────────────────────────────────────────────
ENCODING  = "latin-1"
SEPARADOR = "\t"
