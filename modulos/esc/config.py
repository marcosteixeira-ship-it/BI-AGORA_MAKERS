"""
config_esc.py — Configurações do módulo esc002 (Devoluções).

Arquivos fonte:
  esc002omp.csv  →  Devoluções My City   (sufixo omp)
  esc002mtc.csv  →  Devoluções Metalco   (sufixo mtc)

Tabelas de referência (CSV também):
  ftc001omp.csv  →  FAT_DEV_OMP  (notas de faturamento OMP)
  ftc001mtc.csv  →  FAT_DEV_MTC  (notas de faturamento MTC)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Mapeamento de colunas ESC (header na linha 1 dos CSVs):

  Excel A  (idx  0) → Data de entrada
  Excel B  (idx  1) → Nota de entrada
  Excel C  (idx  2) → Série
  Excel D  (idx  3) → Fornecedor (código)
  Excel E  (idx  4) → Item                        ← usada em Q
  Excel F  (idx  5) → Descrição do item
  Excel G  (idx  6) → Qtde
  Excel H  (idx  7) → Valor unitário
  Excel I  (idx  8) → Valor total
  Excel J  (idx  9) → Valor ICMS                  ← usada em T
  Excel K  (idx 10) → Valor PIS                   ← usada em T
  Excel L  (idx 11) → Valor COFINS                ← usada em T
  Excel M  (idx 12) → Custo da MO
  Excel N  (idx 13) → Preço de custo              ← usada em U
  Excel O  (idx 14) → Custo de MP                 ← usada em U
  Excel P  (idx 15) → Nota fiscal de devolução (Número)  ← usada em Q e W
  ── Colunas calculadas ──
  Excel Q  (idx 16) → CONCATENAR          ← CONCAT(P, "-", E)
  Excel R  (idx 17) → Qtde (repetida)     ← linha espelho da NF original
  Excel S  (idx 18) → Valor total (rep.)  ← linha espelho
  Excel T  (idx 19) → Impostos Dev.       ← J+K+L
  Excel U  (idx 20) → CPV Dev.            ← (N+O)*R
  Excel V  (idx 21) → Mês                 ← PROCV(MÊS(A), META_FAT!A:B, 2, 0)
  Excel W  (idx 22) → Representante       ← PROCV(P, FAT_DEV!B:D, 3, 0)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  PROCV coluna W:
    Chave: Nota fiscal de devolução (P)
    Tabela: FAT_DEV (col B = Nota, col C = Cliente, col D = Representante)
    Resultado: col D = Representante  (índice 3 no PROCV → 3ª coluna de B:D)

  PROCV coluna V:
    Chave: MÊS(A) → número do mês (1..12)
    Tabela: META_FAT col A:B (A=número, B=nome)
    Resultado: nome do mês em português

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ── Arquivos fonte ────────────────────────────────────────────────────────────
ARQUIVO_ESC = {
    "omp": "esc002omp.csv",
    "mtc": "esc002mtc.csv",
}

# Arquivos FAT_DEV — tabela de referência para PROCV da coluna W
ARQUIVO_FAT_DEV = {
    "omp": "ftc001omp.csv",   # FAT_DEV_OMP no Excel
    "mtc": "ftc001mtc.csv",   # FAT_DEV_MTC no Excel
}

ENCODING  = "latin-1"
SEPARADOR = "\t"

# ── Nomes de empresa ──────────────────────────────────────────────────────────
EMPRESA_NOME = {
    "omp": "My City",
    "mtc": "Metalco",
}

# ── Mapeamento coluna_interna → nome_real_no_CSV ──────────────────────────────
# OMP e MTC têm pequenas diferenças nos nomes de colunas — mapeadas aqui.
# Use COLUNAS["omp"] ou COLUNAS["mtc"] conforme o arquivo.
COLUNAS = {
    "omp": {
        "data_entrada":  "Data de entrada",
        "nota_entrada":  "Nota de entrada",
        "serie":         "Série",
        "fornecedor":    "Fornecedor",
        "item":          "Item",                                # E → Q e W
        "descricao":     "Descrição do item",
        "qtde":          "Qtde",                               # G
        "valor_unit":    "Valor unitário",
        "valor_total":   "Valor total",
        "icms":          "Valor ICMS",                         # J → T
        "pis":           "Valor PIS",                          # K → T
        "cofins":        "Valor COFINS",                       # L → T
        "custo_mo":      "Custo da MO",
        "preco_custo":   "Preço de custo",                     # N → U
        "custo_mp":      "Custo de MP",                        # O → U
        "nota_dev":      "Nota fiscal de devolução (Número)",  # P → Q e W
    },
    "mtc": {
        "data_entrada":  "Data de entrada",
        "nota_entrada":  "Nota de entrada",
        "serie":         "Série",
        "fornecedor":    "Fornecedor (Código)",
        "item":          "Item",
        "descricao":     "Descrição do item",
        "qtde":          "Qtde",
        "valor_unit":    "Valor unitário",
        "valor_total":   "Valor total",
        "icms":          "Valor ICMS",
        "pis":           "Valor PIS",
        "cofins":        "Valor COFINS",
        "custo_mo":      "Custo da mão de obra - Item",
        "preco_custo":   "Preço de custo - Item",
        "custo_mp":      "Custo de matéria-prima - Item",
        "nota_dev":      "Nota fiscal de devolução (Número)",
    },
}

# ── Colunas numéricas ─────────────────────────────────────────────────────────
COLUNAS_NUMERICAS = [
    "Qtde", "Valor unitário", "Valor total",
    "Valor ICMS", "Valor PIS", "Valor COFINS",
    "Custo da MO", "Custo da mão de obra - Item",
    "Preço de custo", "Preço de custo - Item",
    "Custo de MP", "Custo de matéria-prima - Item",
]

# ── Colunas de data ───────────────────────────────────────────────────────────
COLUNAS_DATA = ["Data de entrada"]

# ── Colunas da tabela FAT_DEV ─────────────────────────────────────────────────
# Estrutura igual para OMP e MTC:
#   col B (idx 1) = Nota (Número)                    ← chave do PROCV
#   col C (idx 2) = Cliente - Razão social
#   col D (idx 3) = Representante - Razão social     ← retorno do PROCV
FAT_DEV_COL_NOTA = "Nota (Número)"
FAT_DEV_COL_REP  = "Representante - Razão social (Representante)"

# ── Tabela de meses (META_FAT A:B) ───────────────────────────────────────────
MESES_PT = {
    1: "JANEIRO",   2: "FEVEREIRO", 3: "MARÇO",
    4: "ABRIL",     5: "MAIO",      6: "JUNHO",
    7: "JULHO",     8: "AGOSTO",    9: "SETEMBRO",
    10: "OUTUBRO",  11: "NOVEMBRO", 12: "DEZEMBRO",
}

# ── Nomes das colunas calculadas ──────────────────────────────────────────────
COL_Q_CONCATENAR  = "Q_Concatenar"       # Q  CONCAT(P, "-", E)
COL_T_IMPOSTOS    = "T_Impostos Dev."    # T  J+K+L
COL_U_CPV         = "U_CPV Dev."         # U  (N+O)*R
COL_V_MES         = "V_Mês"             # V  nome do mês
COL_W_REPR        = "W_Representante"    # W  PROCV(P, FAT_DEV!B:D, 3, 0)
