"""
ui/abas/aba_logica.py
Aba de documentação das fórmulas (referência para o usuário).
"""

import streamlit as st


def renderizar() -> None:
    st.markdown("""
### 🔎 Lógica das Fórmulas — Referência Completa

---

#### Regra de exclusão comum (fórmulas [1]–[5], [7]–[8])
```
Razão Social == própria empresa ($E$2)          → vazio (não contabiliza)
IC == "SIM"  E  cliente == "METALCO DO BRASIL"  → vazio
IC == "SIM"  E  cliente == "OMP DO BRASIL"      → vazio
```
> **RL, CPV, CPV%, Margem, Margem%** usam apenas as condições IC (sem $E$2).

---

#### ABA FAT — Faturamento

| # | Coluna | Fórmula Excel | Componentes |
|---|--------|--------------|-------------|
| AI | Qtde Dev. | `PROCV(CONCAT(C,"-",F); ESC!Q:R; 2; 0)` | Lookup ESC pelo par nota-item |
| 1 | Qtde Líquida | `I − AI` | Qtde. faturada − Qtde Dev. |
| AJ | RB Dev. | `(J+K+L−M)/I × AI` | RB proporcional à devolução |
| 2 | Receita Bruta | `J+K+L−M−AJ` | Val.total + Frete + Desp. − Desconto − RB Dev. |
| AK | Imp. Dev. | `(N+O+P+Q)/I × AI` | Impostos proporcionais à devolução |
| 3 | Impostos | `N+O+P+Q+AB−AK` | ICMS + COFINS + PIS + ISSQN + ICMS UF DEST − Imp. Dev. |
| AL | RL Dev. | `SE(AJ="";"";AJ−AK)` | RB Dev. − Imp. Dev. |
| 4 | Receita Líquida | `RB − Impostos` | Não testa $E$2 |
| AM | CPV Dev. | `(W+X+Y) × AI` | Custo unitário × Qtde Dev. |
| 5 | CPV | `(W+X+Y)×I − AM` | Custo Revenda + Terceiriz. + Custo MP × Qtde |
| 6 | CPV% | `CPV / RL` | — |
| 7 | Margem | `RL − CPV − Comissão` | — |
| 8 | Margem% | `Margem / RB` | — |
| 9 | Empresa-Cliente | `CONCAT(sufixo,"-",D)` | OMP-1222, METALCO-5734 |
| 10 | Ano de Cadastro | `ANO(AF)` | Ano da data de cadastro |

---

#### ABA ESC — Devoluções

| Col | Fórmula Excel | Descrição |
|-----|--------------|-----------|
| Q | `CONCAT(P,"-",E)` | Chave de lookup: Nota dev. + Item |
| T | `J+K+L` | Impostos devolvidos (ICMS+PIS+COFINS) |
| U | `(N+O)×R` | CPV devolvido (Preço custo + Custo MP) × Qtde espelho |
| V | `PROCV(MÊS(A); META_FAT!A:B; 2; 0)` | Nome do mês em PT-BR |
| W | `PROCV(P; FAT_DEV!B:D; 3; 0)` | Representante da nota original |

---

#### ABA PED — Pedidos

| Col | Fórmula Excel | Descrição |
|-----|--------------|-----------|
| Y | `ANO(W)` | Ano de cadastro do cliente |
| Z | `(H−I)×K` | Valor da venda (qtde líquida × valor unitário) |
| AA | `MÊS(A)` por extenso | Janeiro, Fevereiro... |
| AD | `CONCAT(C,"-",Y)` | Chave de unicidade para clientes |
| AB | `1/CONT.SES(C,C,V,V)` | Peso por (cliente, representante) |
| AC | `SE(Y=ano_atual; 1/CONT.SE(AD,AD); "")` | Peso novos clientes |

---

#### Mapeamento de colunas Excel → CSV (ABA FAT)

| Col Excel | Coluna CSV | Uso |
|-----------|-----------|-----|
| A | `_sufixo` (OMP/METALCO) | Empresa, IC |
| D / $E$2 | `Cliente` / `Razão Social` | [9], exclusão |
| AZ | `Intercompany` | Exclusão IC |
| I | `Qtde. faturada` | [1][2][3][5] |
| J | `Valor total` | [2] |
| K | `Valor do frete` | [2] |
| L | `Despesas acessórias` | [2] |
| M | `Desconto` | [2] |
| N–Q, AB | `ICMS`, `COFINS`, `PIS`, `ISSQN`, `ICMS UF DEST` | [3] |
| AA | `Comissão` | [7] |
| AF | `Data de cad. clie.` | [10] |
| W, X, Y | `Custo Revenda`, `Terceirizacao`, `Custo MP` | [5] |

---

#### Estrutura de arquivos

```
painel_executivo/
├── app.py                    ← ponto de entrada Streamlit
├── core/
│   ├── constantes.py         · empresas, metas, meses
│   └── helpers.py            · parse_numero_br, brl()
├── modulos/
│   ├── fat/
│   │   ├── config.py         · colunas + COL_* calculadas
│   │   ├── leitura.py        · ler_omp(), ler_mtc()
│   │   ├── calculos_base.py  · ESC lookup, flag IC, QTDE
│   │   ├── calculos_receita.py · RB, Impostos, RL
│   │   ├── calculos_resultado.py · CPV, Margem, Empresa-CLI, Ano Cad.
│   │   ├── processamento.py  · processar() — orquestra tudo
│   │   └── pipeline.py       · executar() — entry point
│   ├── esc/
│   │   ├── config.py
│   │   ├── leitura.py
│   │   ├── calculos_q_t_u.py · Concatenar, Imp Dev, CPV Dev
│   │   ├── calculos_v_w.py   · Mês, Representante (PROCV)
│   │   ├── processamento.py
│   │   └── pipeline.py
│   └── ped/
│       ├── config.py
│       ├── leitura.py
│       ├── calculos_venda.py   · Ano Cad., Valor Venda, Mês
│       ├── calculos_contagem.py · Concatenar, CONT.SES
│       ├── processamento.py
│       └── pipeline.py
└── ui/
    ├── estilos.py            · CSS completo (tema claro/escuro)
    ├── sidebar.py            · barra lateral
    ├── componentes/
    │   └── cards.py          · métricas, badges, seções
    └── abas/
        ├── aba_faturamento.py
        ├── aba_devolucoes.py
        ├── aba_pedidos.py
        └── aba_logica.py     (este arquivo)
```
""")
