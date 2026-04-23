"""
config.py — Configurações centrais do módulo ftc002.

Todas as constantes, nomes de colunas e mapeamentos ficam aqui.
Altere este arquivo para adaptar a novos layouts de CSV.
"""

# ── Arquivos fonte ─────────────────────────────────────────────────────────────
ARQUIVO_OMP = "ftc002omp.csv"
ARQUIVO_MTC = "ftc002mtc.csv"
ENCODING    = "latin-1"
SEPARADOR   = "\t"

# ── Identificação das empresas ─────────────────────────────────────────────────
# Nome exato como aparece na coluna "Razão Social" do CSV
# Equivale à célula $E$2 da fórmula Excel (referência fixa da própria empresa)
NOME_EMPRESA = {
    "omp": "OMP DO BRASIL LTDA",     # Razão social — nome fantasia: My City
    "mtc": "METALCO DO BRASIL LTDA",
}

# Nome fantasia — usado na interface, relatórios e painel
NOME_FANTASIA = {
    "omp": "My City",
    "mtc": "Metalco",
}

# Prefixo que aparece na coluna A do Excel (ABA FAT) e em EMPRESA-CLIENTE
PREFIXO_EMPRESA = {
    "omp": "OMP",
    "mtc": "METALCO",
}

# Nomes que configuram operação intercompany quando flag_intercompany = "SIM"
NOMES_INTERCOMPANY = [
    "OMP DO BRASIL LTDA",
    "METALCO DO BRASIL LTDA",
]

# ── Mapeamento de colunas (chave_interna → nome_real_no_CSV) ──────────────────
# Referência de colunas Excel (considerando col A = Empresa, não existe no CSV):
#   Excel B  = Data de emissão       CSV idx  0
#   Excel C  = Nota                  CSV idx  1
#   Excel D  = Cliente               CSV idx  2
#   Excel E  = Razão Social          CSV idx  3
#   Excel F  = Item                  CSV idx  4
#   Excel G  = Descrição             CSV idx  5
#   Excel H  = Valor unitário        CSV idx  6
#   Excel I  = Qtde. faturada        CSV idx  7
#   Excel J  = Valor total           CSV idx  8
#   Excel K  = Valor do frete        CSV idx  9
#   Excel L  = Despesas acessórias   CSV idx 10
#   Excel M  = Desconto              CSV idx 11
#   Excel N  = ICMS                  CSV idx 12
#   Excel O  = COFINS                CSV idx 13
#   Excel P  = PIS                   CSV idx 14
#   Excel Q  = Valor do ISSQN        CSV idx 15
#   Excel R  = Grupo de itens        CSV idx 16
#   Excel S  = Subgrupo de itens     CSV idx 17
#   Excel T  = Família               CSV idx 18
#   Excel U  = Linha                 CSV idx 19
#   Excel V  = Custo MO              CSV idx 20
#   Excel W  = Custo Revenda         CSV idx 21  ← componente CPV
#   Excel X  = Terceirizacao         CSV idx 22  ← componente CPV
#   Excel Y  = Custo MP              CSV idx 23  ← componente CPV
#   Excel Z  = Estado                CSV idx 24
#   Excel AA = Comissão              CSV idx 25  ← usado em MARGEM
#   Excel AB = ICMS UF DEST          CSV idx 26
#   Excel AC = Data do Pedido        CSV idx 27
#   Excel AD = Grupo de clientes     CSV idx 28
#   Excel AE = Família de clientes   CSV idx 29
#   Excel AF = Data de cad. clie.    CSV idx 30  ← ANO DE CADASTRO
#   Excel AG = Representante         CSV idx 31
COLUNAS = {
    # Identificação
    "razao_social":     "Razão Social",
    "cliente":          "Cliente",
    "nota":             "Nota",
    "item":             "Item",
    "descricao":        "Descrição",
    # Datas
    "data_emissao":     "Data de emissão",
    "data_pedido":      "Data do Pedido",
    "data_cad_cli":     "Data de cad. clie.",       # Excel AF → ANO DE CADASTRO
    # Valores financeiros
    "valor_unit":       "Valor unitário",
    "qtde_faturada":    "Qtde. faturada",            # Excel I → CPV
    "valor_total":      "Valor total",               # Excel J → RB
    "frete":            "Valor do frete",            # Excel K → RB
    "desp_acess":       "Despesas acessórias",       # Excel L → RB
    "desconto":         "Desconto",                  # Excel M → RB
    # Impostos
    "icms":             "ICMS",                      # Excel N → Impostos
    "cofins":           "COFINS",                    # Excel O → Impostos
    "pis":              "PIS",                       # Excel P → Impostos
    "issqn":            "Valor do ISSQN",            # Excel Q → Impostos
    "icms_uf_dest":     "ICMS UF DEST",              # Excel AB → Impostos
    # Custos — componentes do CPV
    "custo_mo":         "Custo MO",                  # Excel V (informativo)
    "custo_revenda":    "Custo Revenda",              # Excel W → CPV
    "terceirizacao":    "Terceirizacao",              # Excel X → CPV
    "custo_mp":         "Custo MP",                  # Excel Y → CPV
    # Outros
    "comissao":         "Comissão",                  # Excel AA → MARGEM
    "estado":           "Estado",
    "grupo_itens":      "Grupo de itens",
    "subgrupo_itens":   "Subgrupo de itens",
    "familia":          "Família",
    "linha":            "Linha",
    "grupo_clientes":   "Grupo de clientes",
    "familia_clientes": "Família de clientes",
    "representante":    "Representante - Razão social (Representante)",
}

# ── Colunas a converter para número (formato BR: 1.234,56 → 1234.56) ──────────
COLUNAS_NUMERICAS = [
    "Qtde. faturada", "Valor unitário", "Valor total",
    "Valor do frete", "Despesas acessórias", "Desconto",
    "ICMS", "COFINS", "PIS", "Valor do ISSQN",
    "Custo MO", "Custo Revenda", "Terceirizacao", "Custo MP",
    "Comissão", "ICMS UF DEST",
]

# ── Colunas de data ────────────────────────────────────────────────────────────
COLUNAS_DATA = [
    "Data de emissão",
    "Data do Pedido",
    "Data de cad. clie.",
]

# ══════════════════════════════════════════════════════════════════════════════
#  NOMES DAS COLUNAS CALCULADAS
#  (todas as colunas geradas pelo processamento.py)
# ══════════════════════════════════════════════════════════════════════════════

# ── Flag ──────────────────────────────────────────────────────────────────────
COL_INTERCOMPANY    = "Intercompany"           # AZ — SIM / NAO

# ── Fórmula [1] QTDE ─────────────────────────────────────────────────────────
COL_QTDE_LIQUIDA    = "Qtde Líquida"           # I - AI
COL_QTDE_DEVOLUCAO  = "Qtde Devolvida"         # AI ⚠️ TODO: DEVOLUCOES

# ── Fórmula [2] RECEITA BRUTA ────────────────────────────────────────────────
COL_RB              = "Receita Bruta"          # J+K+L-M-AJ  (AO no Excel)
COL_RB_DEVOLUCAO    = "RB Devolvida"           # AJ ⚠️ TODO: DEVOLUCOES

# ── Fórmula [3] IMPOSTOS ─────────────────────────────────────────────────────
COL_IMPOSTOS        = "Impostos"               # N+O+P+Q+AB-AK  (AP no Excel)
COL_IMPOSTOS_DEV    = "Impostos Devolvidos"    # AK ⚠️ TODO: DEVOLUCOES

# ── Fórmula [4] RECEITA LÍQUIDA ──────────────────────────────────────────────
COL_RL              = "Receita Líquida"        # AO-AP  (AR no Excel)
COL_RL_DEV          = "RL Devolvida"           # AL = AJ-AK (RB Dev - Impostos Dev)

# ── Fórmula [5] CPV ──────────────────────────────────────────────────────────
COL_CPV             = "CPV"                    # (W+X+Y)*I-AM  (AQ no Excel)
COL_CPV_DEVOLUCAO   = "CPV Devolvido"          # AM ⚠️ TODO: DEVOLUCOES

# ── Fórmula [6] CPV% ─────────────────────────────────────────────────────────
COL_CPV_PCT         = "CPV%"                   # AQ/AR = CPV / RL

# ── Fórmula [7] MARGEM ───────────────────────────────────────────────────────
COL_MARGEM          = "Margem"                 # AQ-AR-AA = RL-CPV-Comissão

# ── Fórmula [8] MARGEM% ──────────────────────────────────────────────────────
COL_MARGEM_PCT      = "Margem%"                # AT/AO = Margem / RB

# ── Fórmula [9] EMPRESA-CLIENTE ──────────────────────────────────────────────
COL_EMPRESA_CLI     = "Empresa-Cliente"        # CONCAT(sufixo, "-", Cliente)

# ── Fórmula [10] ANO DE CADASTRO ─────────────────────────────────────────────
COL_ANO_CAD         = "Ano de Cadastro"        # ANO(AF) = ANO(Data cad. clie.)

# ── Renomeação de colunas do MTC para o padrão OMP ────────────────────────────
# O CSV do MTC usa nomes diferentes dos do OMP para várias colunas.
# Mapeamento: {nome_no_csv_mtc: nome_padrao_omp}
COLUNAS_RENAME_MTC: dict[str, str] = {
    # Data de emissão
    "Emissão":                                  "Data de emissão",
    # Razão Social (MTC usa 's' minúsculo)
    "Razão social":                             "Razão Social",
    # Despesas acessórias (MTC usa 'A' maiúsculo)
    "Despesas Acessórias":                      "Despesas acessórias",
    # Família (MTC inclui "de itens")
    "Família de itens":                         "Família",
    # Linha (MTC inclui descrição completa)
    "Linha de itens - Descrição (Linha)":       "Linha",
    # Custo Revenda (MTC chama de Preço de custo)
    "Preço de custo":                           "Custo Revenda",
    # ICMS UF DEST
    "ICMS UF Destino":                          "ICMS UF DEST",
    # Data do Pedido
    "Data de emissão pedido":                   "Data do Pedido",
    # Data de cadastro do cliente
    "Cliente - Data de cadastro":               "Data de cad. clie.",
}
