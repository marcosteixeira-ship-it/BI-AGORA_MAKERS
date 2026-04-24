# BI Agora Makers — HTML Dashboard + API Flask

## Estrutura dos arquivos

```
BI-AGORA_MAKERS/
├── api.py              ← API Flask (novo — copie aqui)
├── dashboard.html      ← Dashboard HTML (novo — copie aqui)
├── app.py              ← Streamlit original (mantém funcionando)
├── data/
│   ├── ftc002omp.csv
│   ├── ftc002mtc.csv
│   └── ...
└── modulos/ ...
```

---

## 1. Instalação

```bash
pip install flask flask-cors
```

Todas as outras dependências (pandas, plotly, etc.) já estão instaladas para o Streamlit.

---

## 2. Rodando no servidor local

```bash
# Navegue até a pasta do projeto
cd "C:\Users\marcos.teixeira\Desktop\BI DEFINITIVO\painel_executivo\BI-AGORA_MAKERS"

# Inicie a API
python api.py
```

Acesse o dashboard:
- Abra `dashboard.html` diretamente no navegador (duplo clique)
- Ou acesse via servidor: http://localhost:5000

---

## 3. Acesso de qualquer lugar (opções)

### Opção A — Ngrok (mais fácil, gratuito)
```bash
# 1. Instale ngrok em https://ngrok.com/download
# 2. Com a API rodando, em outro terminal:
ngrok http 5000

# Vai gerar uma URL como: https://abc123.ngrok.io
# Edite a linha no dashboard.html:
#   const API_BASE = 'https://abc123.ngrok.io';
```

### Opção B — Cloudflare Tunnel (gratuito, mais estável)
```bash
# 1. Instale cloudflared
# 2. Com a API rodando:
cloudflared tunnel --url http://localhost:5000

# Edite API_BASE no dashboard.html com a URL gerada
```

### Opção C — IP fixo na rede (acesso pela rede local)
```
# A API já roda em 0.0.0.0:5000
# Basta editar no dashboard.html:
const API_BASE = 'http://192.168.x.x:5000';  # IP do servidor
```

---

## 4. Conectando ao banco SQL (em vez de CSV)

No `api.py`, localize a função `_get_dados()` e substitua por leitura SQL.

### SQL Server (pyodbc)
```python
pip install pyodbc

import pyodbc
import pandas as pd

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=SEU_SERVIDOR\\INSTANCIA;"
    "DATABASE=SEU_BANCO;"
    "UID=usuario;PWD=senha"
)

def ler_do_sql():
    conn = pyodbc.connect(conn_str)
    df_omp = pd.read_sql("SELECT * FROM ftc002omp", conn)
    df_mtc = pd.read_sql("SELECT * FROM ftc002mtc", conn)
    conn.close()
    return df_omp, df_mtc
```

### MySQL / MariaDB
```python
pip install mysql-connector-python

import mysql.connector

def ler_do_sql():
    conn = mysql.connector.connect(
        host='localhost', database='bi_agora',
        user='usuario', password='senha'
    )
    df_omp = pd.read_sql("SELECT * FROM ftc002omp", conn)
    df_mtc = pd.read_sql("SELECT * FROM ftc002mtc", conn)
    conn.close()
    return df_omp, df_mtc
```

Depois do `ler_do_sql()`, passe os DataFrames para o processamento:
```python
from modulos.fat.processamento import processar

df_omp_proc = processar(df_omp, flag_intercompany='NAO')
df_mtc_proc = processar(df_mtc, flag_intercompany='NAO')
```

---

## 5. Produção (Windows)

Para rodar como serviço Windows (sempre ligado):

```bash
pip install waitress

# Substitua no final do api.py:
from waitress import serve
serve(app, host='0.0.0.0', port=5000)
```

Ou instale como serviço com NSSM: https://nssm.cc

---

## Endpoints da API

| Endpoint | Descrição |
|---|---|
| `GET /api/kpis` | KPIs principais (RB, RL, Margem, etc.) |
| `GET /api/faturamento/mensal` | Faturamento por mês |
| `GET /api/faturamento/familias` | Top famílias de produto |
| `GET /api/faturamento/estados` | Faturamento por UF |
| `GET /api/faturamento/top-clientes` | Top clientes por RB |
| `GET /api/faturamento/grupos` | Grupos de itens |
| `GET /api/pedidos/resumo` | KPIs de pedidos |
| `GET /api/pedidos/mensal` | Pedidos por mês |
| `GET /api/devolucoes/resumo` | KPIs de devoluções |
| `GET /api/metas` | Metas vs realizado |
| `POST /api/refresh` | Limpa cache (força reprocessamento) |

**Parâmetros comuns:**
- `start=YYYY-MM-DD` — data início
- `end=YYYY-MM-DD` — data fim
- `ic=NAO|SIM` — incluir intercompany
- `empresa=consolidado|omp|mtc` — filtrar empresa
