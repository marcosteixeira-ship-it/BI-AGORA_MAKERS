"""
api.py — API Flask para o Painel Executivo BI · Agora Makers
Expõe os dados processados pelos pipelines Python como endpoints REST.

Como rodar:
    pip install flask flask-cors
    python api.py

Para produção:
    gunicorn -w 4 -b 0.0.0.0:5000 api.py:app

Acesso externo (opções):
    - Ngrok:            ngrok http 5000
    - Cloudflare Tunnel: cloudflared tunnel --url http://localhost:5000
    - IP fixo:          Abrir porta 5000 no firewall do servidor

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONECTAR AO BANCO SQL (em vez de CSV):
Substitua as funções _load_* abaixo para ler do seu banco.
Exemplo com pyodbc (SQL Server):

    import pyodbc
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=SEU_SERVIDOR;"
        "DATABASE=SEU_BANCO;"
        "UID=usuario;PWD=senha"
    )
    df = pd.read_sql("SELECT * FROM ftc002omp", conn)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import sys
import json
import math
import threading
from datetime import datetime, timedelta
from functools import wraps

import pandas as pd
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS

# ── Caminho para o projeto ────────────────────────────────────────────────────
# Ajuste BASE_DIR para o caminho real no seu servidor
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJETO_DIR = os.path.join(BASE_DIR, "BI-AGORA_MAKERS")  # pasta raiz do projeto
PASTA_DADOS = os.path.join(PROJETO_DIR, "data")

sys.path.insert(0, PROJETO_DIR)

# ── Importa os pipelines do projeto ──────────────────────────────────────────
from modulos.fat.pipeline  import executar as exec_fat
from modulos.esc.pipeline  import executar as exec_esc, build_esc_lookup
from modulos.fat.calculos_base import set_esc_lookup
from modulos.ped.pipeline  import executar as exec_ped
from modulos.ped.config    import ANO_REFERENCIA
from modulos.fat.config    import (
    COL_RB, COL_IMPOSTOS, COL_RL, COL_CPV, COL_MARGEM,
    COL_MARGEM_PCT, COL_CPV_PCT,
)
from core.constantes import METAS_MENSAIS

# ── Flask app ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)  # Permite acesso do HTML de qualquer origem

# ── Cache simples em memória (evita reprocessar a cada requisição) ─────────────
_cache: dict = {}
_cache_lock = threading.Lock()
CACHE_TTL = 120  # segundos


def _cache_key(pasta: str, flag_ic: str) -> str:
    return f"{pasta}|{flag_ic}"


def _get_dados(flag_ic: str = "NAO") -> dict | None:
    key = _cache_key(PASTA_DADOS, flag_ic)
    with _cache_lock:
        if key in _cache:
            entry = _cache[key]
            if (datetime.now() - entry["ts"]).seconds < CACHE_TTL:
                return entry["data"]

    try:
        d_esc = exec_esc(pasta=PASTA_DADOS, verbose=False)
        lo, lm = build_esc_lookup(d_esc)
        set_esc_lookup(lo, lm)
        d_fat = exec_fat(
            pasta=PASTA_DADOS,
            flag_intercompany_omp=flag_ic,
            flag_intercompany_mtc=flag_ic,
            verbose=False,
        )
        d_ped = exec_ped(
            pasta=PASTA_DADOS,
            flag_intercompany_omp=flag_ic,
            flag_intercompany_mtc=flag_ic,
            ano_ref=ANO_REFERENCIA,
            verbose=False,
        )
        result = {"fat": d_fat, "esc": d_esc, "ped": d_ped}
        with _cache_lock:
            _cache[key] = {"ts": datetime.now(), "data": result}
        return result
    except Exception as e:
        print(f"[ERRO] _get_dados: {e}")
        return None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_dates(start_str: str | None, end_str: str | None):
    """Converte strings ISO para Timestamp, com defaults."""
    if start_str:
        try:
            start = pd.Timestamp(start_str)
        except Exception:
            start = None
    else:
        start = None

    if end_str:
        try:
            end = pd.Timestamp(end_str) + pd.Timedelta(hours=23, minutes=59, seconds=59)
        except Exception:
            end = None
    else:
        end = None

    return start, end


def _filtrar_datas(df: pd.DataFrame, col: str, start, end) -> pd.DataFrame:
    if df is None or df.empty or col not in df.columns:
        return pd.DataFrame()
    dt = pd.to_datetime(df[col], errors="coerce")
    mask = pd.Series(True, index=df.index)
    if start:
        mask &= dt >= start
    if end:
        mask &= dt <= end
    return df[mask]


def _safe_float(v) -> float:
    """Converte para float, retorna 0 se NaN/Inf."""
    try:
        f = float(v)
        return 0.0 if (math.isnan(f) or math.isinf(f)) else f
    except Exception:
        return 0.0


def _df_to_records(df: pd.DataFrame) -> list[dict]:
    """Converte DataFrame para lista de dicts, limpando NaN."""
    if df is None or df.empty:
        return []
    records = df.where(pd.notnull(df), None).to_dict(orient="records")
    cleaned = []
    for row in records:
        clean_row = {}
        for k, v in row.items():
            if isinstance(v, (pd.Timestamp,)):
                clean_row[k] = v.isoformat() if not pd.isnull(v) else None
            elif isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                clean_row[k] = None
            elif isinstance(v, (np.integer,)):
                clean_row[k] = int(v)
            elif isinstance(v, (np.floating,)):
                clean_row[k] = float(v)
            else:
                clean_row[k] = v
        cleaned.append(clean_row)
    return cleaned


def _empresa_df(dados: dict, modulo: str, empresa: str) -> pd.DataFrame:
    """Retorna DataFrame do módulo/empresa pedido."""
    if dados is None:
        return pd.DataFrame()
    mod_data = dados.get(modulo, {})
    if empresa in ("omp", "mtc"):
        return mod_data.get(empresa, pd.DataFrame())
    # consolidado
    omp = mod_data.get("omp", pd.DataFrame())
    mtc = mod_data.get("mtc", pd.DataFrame())
    frames = [f for f in [omp, mtc] if not f.empty]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


# ── Rota raiz ─────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return jsonify({
        "status": "ok",
        "app": "BI Agora Makers API",
        "version": "1.0.0",
        "endpoints": [
            "/api/status",
            "/api/kpis",
            "/api/faturamento/mensal",
            "/api/faturamento/familias",
            "/api/faturamento/estados",
            "/api/faturamento/top-clientes",
            "/api/faturamento/grupos",
            "/api/pedidos/resumo",
            "/api/pedidos/mensal",
            "/api/devolucoes/resumo",
            "/api/metas",
        ],
    })


@app.route("/api/status")
def status():
    dados = _get_dados()
    ok = dados is not None
    return jsonify({"ok": ok, "ts": datetime.now().isoformat()})


# ── KPIs Principais ───────────────────────────────────────────────────────────
@app.route("/api/kpis")
def kpis():
    """
    Retorna os KPIs principais do faturamento consolidado.
    Query params:
        start  : YYYY-MM-DD (opcional)
        end    : YYYY-MM-DD (opcional)
        ic     : NAO | SIM  (intercompany, opcional, default NAO)
        empresa: consolidado | omp | mtc (opcional, default consolidado)
    """
    start, end = _parse_dates(request.args.get("start"), request.args.get("end"))
    ic = request.args.get("ic", "NAO").upper()
    empresa = request.args.get("empresa", "consolidado")

    dados = _get_dados(ic)
    if dados is None:
        return jsonify({"error": "Falha ao carregar dados"}), 500

    df = _empresa_df(dados, "fat", empresa)
    df = _filtrar_datas(df, "Data de emissão", start, end)

    if df.empty:
        return jsonify({
            "rb": 0, "impostos": 0, "rl": 0, "cpv": 0, "margem": 0,
            "margem_pct": 0, "cpv_pct": 0, "imp_pct": 0,
            "notas": 0, "clientes": 0, "periodo": {"start": None, "end": None},
        })

    rb  = _safe_float(df[COL_RB].sum()       if COL_RB       in df.columns else 0)
    imp = _safe_float(df[COL_IMPOSTOS].sum() if COL_IMPOSTOS in df.columns else 0)
    rl  = _safe_float(df[COL_RL].sum()       if COL_RL       in df.columns else 0)
    cpv = _safe_float(df[COL_CPV].sum()      if COL_CPV      in df.columns else 0)
    mg  = _safe_float(df[COL_MARGEM].sum()   if COL_MARGEM   in df.columns else 0)

    return jsonify({
        "rb":        rb,
        "impostos":  imp,
        "rl":        rl,
        "cpv":       cpv,
        "margem":    mg,
        "margem_pct":  round(mg  / rl  * 100, 2) if rl  else 0,
        "cpv_pct":     round(cpv / rl  * 100, 2) if rl  else 0,
        "imp_pct":     round(imp / rb  * 100, 2) if rb  else 0,
        "notas":    int(df["Nota"].nunique())    if "Nota"    in df.columns else 0,
        "clientes": int(df["Cliente"].nunique()) if "Cliente" in df.columns else 0,
        "periodo": {
            "start": str(df["Data de emissão"].min()) if "Data de emissão" in df.columns else None,
            "end":   str(df["Data de emissão"].max()) if "Data de emissão" in df.columns else None,
        },
    })


# ── Faturamento Mensal ────────────────────────────────────────────────────────
@app.route("/api/faturamento/mensal")
def fat_mensal():
    """Faturamento agrupado por mês. Inclui RB, RL, Margem e N° Notas."""
    start, end = _parse_dates(request.args.get("start"), request.args.get("end"))
    ic = request.args.get("ic", "NAO").upper()
    empresa = request.args.get("empresa", "consolidado")

    dados = _get_dados(ic)
    if dados is None:
        return jsonify([])

    df = _empresa_df(dados, "fat", empresa)
    df = _filtrar_datas(df, "Data de emissão", start, end)

    if df.empty:
        return jsonify([])

    df = df.copy()
    dt = pd.to_datetime(df["Data de emissão"], errors="coerce")
    df["_mes_per"] = dt.dt.to_period("M").astype(str)
    df["_mes_num"] = dt.dt.year * 100 + dt.dt.month

    agg = df.groupby(["_mes_per", "_mes_num"]).agg(
        rb     = (COL_RB,      "sum") if COL_RB      in df.columns else ("Valor total", "sum"),
        rl     = (COL_RL,      "sum") if COL_RL      in df.columns else ("Valor total", "sum"),
        margem = (COL_MARGEM,  "sum") if COL_MARGEM  in df.columns else ("Valor total", "sum"),
        cpv    = (COL_CPV,     "sum") if COL_CPV     in df.columns else ("Valor total", "sum"),
        notas  = ("Nota",      "nunique") if "Nota"  in df.columns else ("Valor total", "count"),
    ).reset_index().sort_values("_mes_num")

    result = []
    for _, row in agg.iterrows():
        rb = _safe_float(row.get("rb", 0))
        rl = _safe_float(row.get("rl", 0))
        mg = _safe_float(row.get("margem", 0))
        result.append({
            "mes":      str(row["_mes_per"]),
            "rb":       rb,
            "rl":       rl,
            "margem":   mg,
            "cpv":      _safe_float(row.get("cpv", 0)),
            "mg_pct":   round(mg / rb * 100, 2) if rb else 0,
            "notas":    int(row.get("notas", 0)),
        })

    return jsonify(result)


# ── Faturamento por Famílias ──────────────────────────────────────────────────
@app.route("/api/faturamento/familias")
def fat_familias():
    """Top famílias de produto por faturamento."""
    start, end = _parse_dates(request.args.get("start"), request.args.get("end"))
    ic = request.args.get("ic", "NAO").upper()
    empresa = request.args.get("empresa", "consolidado")
    n = int(request.args.get("n", 12))

    dados = _get_dados(ic)
    if dados is None:
        return jsonify([])

    df = _empresa_df(dados, "fat", empresa)
    df = _filtrar_datas(df, "Data de emissão", start, end)

    if df.empty or "Família" not in df.columns or COL_RB not in df.columns:
        return jsonify([])

    agg = (df.groupby("Família")[COL_RB]
             .sum()
             .reset_index()
             .rename(columns={COL_RB: "rb", "Família": "familia"})
             .sort_values("rb", ascending=False)
             .head(n))

    total = agg["rb"].sum()
    result = []
    for _, row in agg.iterrows():
        rb = _safe_float(row["rb"])
        result.append({
            "familia": str(row["familia"]),
            "rb":      rb,
            "pct":     round(rb / total * 100, 2) if total else 0,
        })
    return jsonify(result)


# ── Faturamento por Estado ────────────────────────────────────────────────────
@app.route("/api/faturamento/estados")
def fat_estados():
    """Faturamento por UF."""
    start, end = _parse_dates(request.args.get("start"), request.args.get("end"))
    ic = request.args.get("ic", "NAO").upper()
    empresa = request.args.get("empresa", "consolidado")

    dados = _get_dados(ic)
    if dados is None:
        return jsonify([])

    df = _empresa_df(dados, "fat", empresa)
    df = _filtrar_datas(df, "Data de emissão", start, end)

    if df.empty or "Estado" not in df.columns or COL_RB not in df.columns:
        return jsonify([])

    agg = (df.groupby("Estado")[COL_RB]
             .sum()
             .reset_index()
             .rename(columns={COL_RB: "rb", "Estado": "estado"})
             .sort_values("rb", ascending=False))

    total = agg["rb"].sum()
    return jsonify([{
        "estado": str(row["estado"]),
        "rb":     _safe_float(row["rb"]),
        "pct":    round(_safe_float(row["rb"]) / total * 100, 2) if total else 0,
    } for _, row in agg.iterrows()])


# ── Top Clientes ──────────────────────────────────────────────────────────────
@app.route("/api/faturamento/top-clientes")
def fat_top_clientes():
    """Top N clientes por Receita Bruta."""
    start, end = _parse_dates(request.args.get("start"), request.args.get("end"))
    ic = request.args.get("ic", "NAO").upper()
    empresa = request.args.get("empresa", "consolidado")
    n = int(request.args.get("n", 15))

    dados = _get_dados(ic)
    if dados is None:
        return jsonify([])

    df = _empresa_df(dados, "fat", empresa)
    df = _filtrar_datas(df, "Data de emissão", start, end)

    if df.empty or "Cliente" not in df.columns or COL_RB not in df.columns:
        return jsonify([])

    cols_agg = {COL_RB: "sum"}
    if COL_MARGEM in df.columns:
        cols_agg[COL_MARGEM] = "sum"
    if "Nota" in df.columns:
        cols_agg["Nota"] = "nunique"

    agg = (df.groupby("Cliente")
             .agg(cols_agg)
             .reset_index()
             .sort_values(COL_RB, ascending=False)
             .head(n))

    total = agg[COL_RB].sum()
    result = []
    for _, row in agg.iterrows():
        rb = _safe_float(row[COL_RB])
        mg = _safe_float(row.get(COL_MARGEM, 0)) if COL_MARGEM in agg.columns else 0
        result.append({
            "cliente": str(row["Cliente"]),
            "rb":      rb,
            "margem":  mg,
            "mg_pct":  round(mg / rb * 100, 2) if rb else 0,
            "notas":   int(row.get("Nota", 0)) if "Nota" in agg.columns else 0,
            "pct":     round(rb / total * 100, 2) if total else 0,
        })
    return jsonify(result)


# ── Faturamento por Grupo de Itens ────────────────────────────────────────────
@app.route("/api/faturamento/grupos")
def fat_grupos():
    """Faturamento por grupo e subgrupo (treemap data)."""
    start, end = _parse_dates(request.args.get("start"), request.args.get("end"))
    ic = request.args.get("ic", "NAO").upper()
    empresa = request.args.get("empresa", "consolidado")

    dados = _get_dados(ic)
    if dados is None:
        return jsonify([])

    df = _empresa_df(dados, "fat", empresa)
    df = _filtrar_datas(df, "Data de emissão", start, end)

    if df.empty or "Grupo de itens" not in df.columns or COL_RB not in df.columns:
        return jsonify([])

    agg = (df.groupby("Grupo de itens")[COL_RB]
             .sum()
             .reset_index()
             .rename(columns={COL_RB: "rb", "Grupo de itens": "grupo"})
             .sort_values("rb", ascending=False)
             .head(20))

    total = agg["rb"].sum()
    return jsonify([{
        "grupo": str(row["grupo"]),
        "rb":    _safe_float(row["rb"]),
        "pct":   round(_safe_float(row["rb"]) / total * 100, 2) if total else 0,
    } for _, row in agg.iterrows()])


# ── Pedidos ───────────────────────────────────────────────────────────────────
@app.route("/api/pedidos/resumo")
def ped_resumo():
    """KPIs de pedidos."""
    start, end = _parse_dates(request.args.get("start"), request.args.get("end"))
    ic = request.args.get("ic", "NAO").upper()
    empresa = request.args.get("empresa", "consolidado")

    dados = _get_dados(ic)
    if dados is None:
        return jsonify({})

    df = _empresa_df(dados, "ped", empresa)
    df = _filtrar_datas(df, "Data de emissão", start, end)

    if df.empty:
        return jsonify({"total_pedidos": 0, "valor_venda": 0, "clientes": 0, "novos_clientes": 0})

    col_venda = "Valor da Venda"
    col_cli   = "Razão social (Nome) - Cliente (Pedido)"
    col_novos = "CONT.SES NOVOS CLIENTES"

    return jsonify({
        "total_pedidos":  int(df["Pedido"].nunique()) if "Pedido" in df.columns else 0,
        "valor_venda":    _safe_float(df[col_venda].sum()) if col_venda in df.columns else 0,
        "clientes":       int(df[col_cli].nunique()) if col_cli in df.columns else 0,
        "novos_clientes": _safe_float(df[col_novos].sum()) if col_novos in df.columns else 0,
    })


@app.route("/api/pedidos/mensal")
def ped_mensal():
    """Pedidos agrupados por mês."""
    start, end = _parse_dates(request.args.get("start"), request.args.get("end"))
    ic = request.args.get("ic", "NAO").upper()
    empresa = request.args.get("empresa", "consolidado")

    dados = _get_dados(ic)
    if dados is None:
        return jsonify([])

    df = _empresa_df(dados, "ped", empresa)
    df = _filtrar_datas(df, "Data de emissão", start, end)

    if df.empty or "Valor da Venda" not in df.columns:
        return jsonify([])

    df = df.copy()
    dt = pd.to_datetime(df["Data de emissão"], errors="coerce")
    df["_mes_per"] = dt.dt.to_period("M").astype(str)
    df["_mes_num"] = dt.dt.year * 100 + dt.dt.month

    agg = (df.groupby(["_mes_per", "_mes_num"])
             .agg(valor=("Valor da Venda", "sum"),
                  pedidos=("Pedido", "nunique") if "Pedido" in df.columns else ("Valor da Venda", "count"))
             .reset_index()
             .sort_values("_mes_num"))

    return jsonify([{
        "mes":     str(row["_mes_per"]),
        "valor":   _safe_float(row["valor"]),
        "pedidos": int(row["pedidos"]),
    } for _, row in agg.iterrows()])


# ── Devoluções ────────────────────────────────────────────────────────────────
@app.route("/api/devolucoes/resumo")
def dev_resumo():
    """KPIs de devoluções."""
    start, end = _parse_dates(request.args.get("start"), request.args.get("end"))
    empresa = request.args.get("empresa", "consolidado")

    dados = _get_dados()
    if dados is None:
        return jsonify({})

    df = _empresa_df(dados, "esc", empresa)
    if not df.empty and "Data de emissão" in df.columns:
        df = _filtrar_datas(df, "Data de emissão", start, end)

    if df.empty:
        return jsonify({"total_notas": 0, "valor_total": 0, "clientes": 0})

    col_valor = "Valor total"
    return jsonify({
        "total_notas": int(df["Nota"].nunique()) if "Nota" in df.columns else 0,
        "valor_total": _safe_float(df[col_valor].sum()) if col_valor in df.columns else 0,
        "clientes":    int(df["Cliente"].nunique()) if "Cliente" in df.columns else 0,
    })


# ── Metas ─────────────────────────────────────────────────────────────────────
@app.route("/api/metas")
def metas():
    """
    Retorna metas mensais vs realizado para My City e Metalco.
    Também lê metas_config.json se existir.
    """
    ic = request.args.get("ic", "NAO").upper()
    ano = int(request.args.get("ano", datetime.now().year))

    # Tenta carregar metas_config.json
    cfg_path = os.path.join(PASTA_DADOS, "metas_config.json")
    cfg = {}
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            pass

    dados = _get_dados(ic)
    result = {}

    for empresa_key, empresa_nome in [("omp", "My City"), ("mtc", "Metalco")]:
        metas_empresa = METAS_MENSAIS.get(empresa_nome, {})

        # Realizado do ano
        df = _empresa_df(dados, "fat", empresa_key) if dados else pd.DataFrame()

        realizado_por_mes: dict[int, float] = {}
        if not df.empty and "Data de emissão" in df.columns and COL_RB in df.columns:
            df = df.copy()
            dt = pd.to_datetime(df["Data de emissão"], errors="coerce")
            mask = dt.dt.year == ano
            df_ano = df[mask].copy()
            df_ano["_mes"] = dt[mask].dt.month
            agg = df_ano.groupby("_mes")[COL_RB].sum()
            realizado_por_mes = {int(k): _safe_float(v) for k, v in agg.items()}

        meses_result = []
        meses_nomes = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
        for m in range(1, 13):
            meta_val = float(metas_empresa.get(m, 0))
            real_val = realizado_por_mes.get(m, 0.0)
            ating = round(real_val / meta_val * 100, 2) if meta_val else 0
            meses_result.append({
                "mes":   meses_nomes[m - 1],
                "mes_n": m,
                "meta":  meta_val,
                "real":  real_val,
                "ating": ating,
            })

        result[empresa_key] = {
            "nome":   empresa_nome,
            "meses":  meses_result,
            "meta_anual":  sum(v for v in metas_empresa.values()),
            "real_anual":  sum(realizado_por_mes.values()),
        }

    return jsonify(result)


# ── Representantes ────────────────────────────────────────────────────────────
@app.route("/api/faturamento/representantes")
def fat_representantes():
    """Top representantes por Receita Bruta."""
    start, end = _parse_dates(request.args.get("start"), request.args.get("end"))
    ic = request.args.get("ic", "NAO").upper()
    empresa = request.args.get("empresa", "consolidado")
    n = int(request.args.get("n", 15))

    dados = _get_dados(ic)
    if dados is None:
        return jsonify([])

    df = _empresa_df(dados, "fat", empresa)
    df = _filtrar_datas(df, "Data de emissão", start, end)

    col_rep = "Representante - Razão social (Representante)"
    if df.empty or col_rep not in df.columns or COL_RB not in df.columns:
        return jsonify([])

    agg = (df.groupby(col_rep)[COL_RB]
             .sum()
             .reset_index()
             .rename(columns={COL_RB: "rb", col_rep: "representante"})
             .sort_values("rb", ascending=False)
             .head(n))

    total = agg["rb"].sum()
    return jsonify([{
        "representante": str(row["representante"]),
        "rb":  _safe_float(row["rb"]),
        "pct": round(_safe_float(row["rb"]) / total * 100, 2) if total else 0,
    } for _, row in agg.iterrows()])


# ── Invalidar cache ───────────────────────────────────────────────────────────
@app.route("/api/refresh", methods=["POST"])
def refresh_cache():
    """Força reprocessamento dos dados (limpa o cache)."""
    with _cache_lock:
        _cache.clear()
    return jsonify({"ok": True, "msg": "Cache limpo. Próxima requisição reprocessará os dados."})


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  BI Agora Makers — API Flask")
    print(f"  Projeto: {PROJETO_DIR}")
    print(f"  Dados:   {PASTA_DADOS}")
    print("  Acesse:  http://localhost:5000")
    print("=" * 55)
    app.run(host="0.0.0.0", port=5000, debug=False)
