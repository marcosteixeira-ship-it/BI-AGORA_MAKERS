"""
config_ped.py — Configurações do módulo ped_omp (Pedidos OMP).

Arquivo fonte: pdc002omp.csv (separado por tabulação, latin-1)

Referência de colunas Excel (aba PED_OMP — sem coluna extra de Empresa,
portanto Excel A = CSV idx 0):

  Excel A  (idx  0) → Data de emissão
  Excel B  (idx  1) → Pedido
  Excel C  (idx  2) → Razão social (Nome) - Cliente (Pedido)
  Excel D  (idx  3) → Item
  Excel E  (idx  4) → Descrição do item
  Excel F  (idx  5) → Subgrupo (Código) - Item
  Excel G  (idx  6) → Descrição - Família de itens (Item)
  Excel H  (idx  7) → Qtde. solicitada
  Excel I  (idx  8) → Qtde. cancelada
  Excel J  (idx  9) → Qtde. faturada
  Excel K  (idx 10) → Valor unitário
  Excel L  (idx 11) → Data de previsão de faturamento - Pedido
  Excel M  (idx 12) → Impostos - Valor ICMS destinatário
  Excel N  (idx 13) → Valor do ICMS
  Excel O  (idx 14) → Valor do PIS
  Excel P  (idx 15) → Valor de COFINS
  Excel Q  (idx 16) → Preço de custo - Item
  Excel R  (idx 17) → Custo de matéria-prima - Item
  Excel S  (idx 18) → Item - Gastos gerais de fabricação
  Excel T  (idx 19) → Custo da mão de obra - Item
  Excel U  (idx 20) → Cliente - Estado (Sigla)
  Excel V  (idx 21) → Representante - Razão social (Representante)
  Excel W  (idx 22) → Cliente - Data de cadastro          ← ANO CADASTRO
  Excel X  (idx 23) → Família de clientes
  ── Colunas calculadas (geradas pelo processamento) ──
  Excel Y  (idx 24) → Ano Cadastro                        ← ANO(W)
  Excel Z  (idx 25) → Valor da Venda                      ← (H-I)*K
  Excel AA (idx 26) → Mês                                 ← MÊS(A) por extenso
  Excel AB (idx 27) → CONT.SES CLIENTES                   ← 1/CONT.SES(C,C,V,V)
  Excel AC (idx 28) → CONT.SES NOVOS CLIENTES             ← SE(Y=ano_atual, 1/CONT.SE(AD,AD3), "")
  Excel AD (idx 29) → CONCATENAR                          ← CONCAT(C, "-", Y)
"""

import datetime

# ── Arquivos fonte ─────────────────────────────────────────────────────────────
ARQUIVO_PDC_OMP = "pdc002omp.csv"
ARQUIVO_PDC_MTC = "pdc002mtc.csv"
ENCODING        = "latin-1"
SEPARADOR       = "\t"

# ── Identificação das empresas ─────────────────────────────────────────────────
NOME_EMPRESA = {
    "omp": "OMP DO BRASIL LTDA",
    "mtc": "METALCO DO BRASIL LTDA",
}
PREFIXO_EMPRESA = {
    "omp": "OMP",
    "mtc": "METALCO",
}

# ── Ano de referência para novos clientes ($M$45 no Excel) ────────────────────
# Equivale ao ano corrente. Pode ser sobrescrito manualmente se necessário.
ANO_REFERENCIA = datetime.datetime.now().year

# ── Nomes intercompany (mesmo padrão do ftc002) ───────────────────────────────
NOMES_INTERCOMPANY = [
    "OMP DO BRASIL LTDA",
    "METALCO DO BRASIL LTDA",
]

# ── Mapeamento chave_interna → nome_real_no_CSV ───────────────────────────────
COLUNAS = {
    # Identificação
    "data_emissao":     "Data de emissão",                              # A → MÊS(A)
    "pedido":           "Pedido",                                       # B
    "razao_social":     "Razão social (Nome) - Cliente (Pedido)",       # C → IC / CONT.SES / CONCAT
    "item":             "Item",                                         # D
    "descricao":        "Descrição do item",                           # E
    "subgrupo_cod":     "Subgrupo (Código) - Item",                    # F
    "familia_item":     "Descrição - Família de itens (Item)",         # G
    "qtde_solicitada":  "Qtde. solicitada",                            # H → Valor da Venda
    "qtde_cancelada":   "Qtde. cancelada",                             # I → Valor da Venda
    "qtde_faturada":    "Qtde. faturada",                              # J
    "valor_unit":       "Valor unitário",                              # K → Valor da Venda
    "dt_prev_fat":      "Data de previsão de faturamento - Pedido",    # L
    "icms_dest":        "Impostos dos itens dos pedidos - Valor ICMS destinatário",  # M
    "icms":             "Valor do ICMS - Impostos dos itens dos pedidos",            # N
    "pis":              "Valor do PIS - Impostos dos itens dos pedidos",             # O
    "cofins":           "Valor de COFINS - Impostos dos itens dos pedidos",          # P
    "preco_custo":      "Preço de custo - Item",                       # Q
    "custo_mp":         "Custo de matéria-prima - Item",               # R
    "custo_ggf":        "Item - Gastos gerais de fabricação",          # S
    "custo_mo":         "Custo da mão de obra - Item",                 # T
    "estado":           "Cliente - Estado (Sigla)",                    # U
    "representante":    "Representante - Razão social (Representante)",# V → CONT.SES
    "dt_cadastro":      "Cliente - Data de cadastro",                  # W → ANO CADASTRO
    "familia_cli":      "Família de clientes",                         # X
}

# ── Colunas numéricas (serão convertidas de str → float se vierem como texto) ─
COLUNAS_NUMERICAS = [
    "Qtde. solicitada",
    "Qtde. cancelada",
    "Qtde. faturada",
    "Valor unitário",
    "Impostos dos itens dos pedidos - Valor ICMS destinatário",
    "Valor do ICMS - Impostos dos itens dos pedidos",
    "Valor do PIS - Impostos dos itens dos pedidos",
    "Valor de COFINS - Impostos dos itens dos pedidos",
    "Preço de custo - Item",
    "Custo de matéria-prima - Item",
    "Item - Gastos gerais de fabricação",
    "Custo da mão de obra - Item",
]

# ── Colunas de data ────────────────────────────────────────────────────────────
COLUNAS_DATA = [
    "Data de emissão",
    "Data de previsão de faturamento - Pedido",
    "Cliente - Data de cadastro",
]

# ── Nomes das colunas calculadas geradas pelo processamento ───────────────────
COL_ANO_CAD         = "Ano Cadastro"              # Y  → ANO(W)
COL_VALOR_VENDA     = "Valor da Venda"            # Z  → (H-I)*K
COL_MES             = "Mês"                       # AA → MÊS(A) por extenso
COL_CONT_CLI        = "CONT.SES CLIENTES"         # AB → 1/CONT.SES(C,C,V,V)
COL_CONT_NOVOS      = "CONT.SES NOVOS CLIENTES"   # AC → SE(Y=ano_ref, 1/CONT.SE(AD,AD), "")
COL_CONCATENAR      = "CONCATENAR"                # AD → CONCAT(C, "-", Y)

# Flag intercompany (mesma coluna do ftc002)
COL_INTERCOMPANY    = "Intercompany"

# ── Mapeamento de colunas MTC → nomes padrão OMP ─────────────────────────────
# Diferenças encontradas entre pdc002omp.csv e pdc002mtc.csv (idx 18 e 20).
COLUNAS_RENAME_MTC_PED = {
    "Gastos gerais de fabricação":          "Item - Gastos gerais de fabricação",
    "Estado (Sigla) - Cliente (Pedido)":    "Cliente - Estado (Sigla)",
}

# ── Mapeamento número do mês → nome em português ──────────────────────────────
MESES_PT = {
    1:  "JANEIRO",   2:  "FEVEREIRO", 3:  "MARÇO",
    4:  "ABRIL",     5:  "MAIO",      6:  "JUNHO",
    7:  "JULHO",     8:  "AGOSTO",    9:  "SETEMBRO",
    10: "OUTUBRO",   11: "NOVEMBRO",  12: "DEZEMBRO",
}
