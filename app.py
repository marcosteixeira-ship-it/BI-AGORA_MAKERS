"""
app.py — Painel Executivo · BI GRUPO AGORA MAKERS
Executa com: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import sys, os
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="BI GRUPO AGORA MAKERS",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "tema_escuro" not in st.session_state:
    st.session_state.tema_escuro = False
if "sidebar_visivel" not in st.session_state:
    st.session_state.sidebar_visivel = True

DARK = st.session_state.tema_escuro

from ui.estilos import aplicar_css
aplicar_css(dark=DARK)

# Ocultar sidebar quando usuário fechou
if not st.session_state.sidebar_visivel:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        display: none !important;
        width: 0 !important;
        visibility: hidden !important;
        min-width: 0 !important;
    }
    [data-testid="stMain"], section[data-testid="stMain"] {
        margin-left: 0 !important;
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

PASTA_DADOS = os.path.join(os.path.dirname(__file__), "data")

from ui.sidebar import renderizar_sidebar
from modulos.fat.pipeline import arquivos_disponiveis as fat_arquivos

cfg            = renderizar_sidebar(PASTA_DADOS, arquivos_fn=fat_arquivos)
flag_ic        = cfg["flag_ic"]
mostrar_vazios = cfg["mostrar_vazios"]
n_linhas       = cfg["n_linhas"]
data_inicio    = cfg["data_inicio"]
data_fim       = cfg["data_fim"]

from modulos.esc.pipeline import executar as exec_esc, build_esc_lookup
from modulos.fat.pipeline import executar as exec_fat
from modulos.fat.calculos_base import set_esc_lookup
from modulos.ped.pipeline import executar as exec_ped
from modulos.ped.config import ANO_REFERENCIA
from modulos.fat.config import COL_RB, COL_IMPOSTOS, COL_RL, COL_CPV, COL_MARGEM


@st.cache_data(ttl=120, show_spinner=False)
def _load_esc(pasta):
    return exec_esc(pasta=pasta, verbose=False)

@st.cache_data(ttl=120, show_spinner=False)
def _load_fat(pasta, fi, _key):
    return exec_fat(pasta=pasta, flag_intercompany_omp=fi, flag_intercompany_mtc=fi, verbose=False)

@st.cache_data(ttl=120, show_spinner=False)
def _load_ped(pasta, fi):
    return exec_ped(pasta=pasta, flag_intercompany_omp=fi, flag_intercompany_mtc=fi,
                    ano_ref=ANO_REFERENCIA, verbose=False)

_erro = ""
d_esc = d_fat = d_ped = None

with st.spinner("Carregando dados…"):
    try:
        d_esc = _load_esc(PASTA_DADOS)
        lo, lm = build_esc_lookup(d_esc)
        set_esc_lookup(lo, lm)
        _key = f"{flag_ic}_{len(lo)}_{len(lm)}"
        d_fat = _load_fat(PASTA_DADOS, flag_ic, _key)
        d_ped = _load_ped(PASTA_DADOS, flag_ic)
    except Exception as e:
        _erro = str(e)


def _filtrar(df: pd.DataFrame, col: str) -> pd.DataFrame:
    if df.empty or col not in df.columns:
        return df
    dt = pd.to_datetime(df[col], errors="coerce")
    m  = pd.Series(True, index=df.index)
    if data_inicio:
        m &= dt >= pd.Timestamp(data_inicio)
    if data_fim:
        m &= dt <= pd.Timestamp(data_fim) + pd.Timedelta(hours=23, minutes=59, seconds=59)
    return df[m]


_vz   = pd.DataFrame()
fat_f = {k: _filtrar(d_fat.get(k, _vz) if d_fat else _vz, "Data de emissão")
         for k in ("omp", "mtc", "consolidado")}
ped_f = {k: _filtrar(d_ped.get(k, _vz) if d_ped else _vz, "Data de emissão")
         for k in ("omp", "mtc")}
fat_raw = {k: (d_fat.get(k, _vz) if d_fat else _vz) for k in ("omp", "mtc")}

# ── Masthead ──────────────────────────────────────────────────────────────────
_ic_label   = "IC ativo" if flag_ic == "SIM" else "IC desativado"
_per = (f"Até {data_fim.strftime('%d/%m/%Y')}" if not data_inicio
        else f"{data_inicio.strftime('%d/%m/%Y')} → {data_fim.strftime('%d/%m/%Y')}")
_linhas_omp = f"{len(fat_f['omp']):,}" if not fat_f["omp"].empty else "0"
_linhas_mtc = f"{len(fat_f['mtc']):,}" if not fat_f["mtc"].empty else "0"

_col_btn, _col_mast = st.columns([1, 11])
with _col_btn:
    _label_btn = "✕ Fechar" if st.session_state.sidebar_visivel else "⚙️ Config"
    if st.button(_label_btn, key="app_btn_toggle_sidebar",
                 help="Mostrar / ocultar configurações", use_container_width=True):
        st.session_state.sidebar_visivel = not st.session_state.sidebar_visivel
        st.rerun()

with _col_mast:
    st.markdown(f"""
    <div class="masthead">
      <div class="masthead-rule"></div>
      <div class="masthead-body">
        <div class="masthead-left">
          <div class="masthead-logo-wrap">
            <svg viewBox="0 0 16 16" fill="white">
              <rect x="2" y="2" width="5" height="5" rx="1"/>
              <rect x="9" y="2" width="5" height="5" rx="1"/>
              <rect x="2" y="9" width="5" height="5" rx="1"/>
              <rect x="9" y="9" width="5" height="5" rx="1"/>
            </svg>
          </div>
          <div>
            <div class="masthead-eyebrow">Grupo Agora Makers</div>
            <div class="masthead-brand">Painel Executivo</div>
            <div class="masthead-chips">
              <span class="mchip"><span class="live-dot"></span>ao vivo</span>
              <span class="mchip">📅 {_per}</span>
              <span class="mchip">🔀 {_ic_label}</span>
            </div>
          </div>
        </div>
        <div class="masthead-right">
          <div class="mstat-group">
            <div class="mstat">
              <div class="mstat-val">{_linhas_omp}</div>
              <div class="mstat-lbl">My City</div>
            </div>
            <div class="mstat">
              <div class="mstat-val">{_linhas_mtc}</div>
              <div class="mstat-lbl">Metalco</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── KPI Header ────────────────────────────────────────────────────────────────
def _kv(v):
    a = abs(v)
    if a >= 1_000_000: return f"R$ {v/1_000_000:.1f}M"
    if a >= 1_000:     return f"R$ {v/1_000:.0f}K"
    return f"R$ {v:,.0f}"

def _ks(v):
    return f"R$ {v:,.0f}" if abs(v) >= 1_000 else "—"

_df_h = fat_f.get("consolidado", pd.DataFrame())
_rb   = _df_h[COL_RB].sum()       if not _df_h.empty and COL_RB       in _df_h else 0.0
_imp  = _df_h[COL_IMPOSTOS].sum() if not _df_h.empty and COL_IMPOSTOS in _df_h else 0.0
_rl   = _df_h[COL_RL].sum()       if not _df_h.empty and COL_RL       in _df_h else 0.0
_cpv  = _df_h[COL_CPV].sum()      if not _df_h.empty and COL_CPV      in _df_h else 0.0
_mg   = _df_h[COL_MARGEM].sum()   if not _df_h.empty and COL_MARGEM   in _df_h else 0.0
_nfs  = int(_df_h["Nota"].nunique())    if not _df_h.empty and "Nota"    in _df_h else 0
_clis = int(_df_h["Cliente"].nunique()) if not _df_h.empty and "Cliente" in _df_h else 0
_imp_p = f"{_imp/_rb*100:.1f}% da RB" if _rb else "—"
_cpv_p = f"{_cpv/_rl*100:.1f}% da RL" if _rl else "—"
_mg_p  = f"{_mg/_rb*100:.1f}% da RB"  if _rb else "—"

st.markdown(f"""
<div class="kpi-hdr">
  <div class="kha-card">
    <div class="kha-icon" style="background:#EBF1FF">
      <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
        <path d="M2 12 L6 8 L10 10 L14 4" stroke="#1A6BF5" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <div class="kha-label">Receita Bruta</div>
    <div class="kha-value">{_kv(_rb)}</div>
    <div class="kha-sub">{_ks(_rb)}</div>
  </div>
  <div class="kha-card">
    <div class="kha-icon" style="background:#FFE4EC">
      <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
        <circle cx="8" cy="8" r="5" stroke="#E11D48" stroke-width="1.5"/>
        <path d="M8 5v3l2 2" stroke="#E11D48" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
    </div>
    <div class="kha-label">Impostos</div>
    <div class="kha-value">{_kv(_imp)}</div>
    <div class="kha-sub">{_imp_p}</div>
  </div>
  <div class="kha-card">
    <div class="kha-icon" style="background:#E0F5F0">
      <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
        <rect x="2" y="9" width="3" height="5" rx="1" fill="#0E9F7E"/>
        <rect x="6.5" y="6" width="3" height="8" rx="1" fill="#0E9F7E"/>
        <rect x="11" y="3" width="3" height="11" rx="1" fill="#0E9F7E"/>
      </svg>
    </div>
    <div class="kha-label">Rec. Líquida</div>
    <div class="kha-value">{_kv(_rl)}</div>
    <div class="kha-sub">{_ks(_rl)}</div>
  </div>
  <div class="kha-card">
    <div class="kha-icon" style="background:#FEF3C7">
      <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
        <path d="M3 13 L8 3 L13 13 Z" stroke="#D97706" stroke-width="1.5" stroke-linejoin="round"/>
      </svg>
    </div>
    <div class="kha-label">CPV</div>
    <div class="kha-value">{_kv(_cpv)}</div>
    <div class="kha-sub">{_cpv_p}</div>
  </div>
  <div class="kha-card">
    <div class="kha-icon" style="background:#E6F4EC">
      <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
        <path d="M2 11 L6 7 L10 9 L14 4" stroke="#3D6B56" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <div class="kha-label">Margem</div>
    <div class="kha-value">{_kv(_mg)}</div>
    <div class="kha-sub">{_mg_p}</div>
  </div>
  <div class="kha-card">
    <div class="kha-icon" style="background:#F0F2F5">
      <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
        <path d="M2 14V6M6 14V4M10 14V8M14 14V2" stroke="#6B7280" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
    </div>
    <div class="kha-label">Notas Fiscais</div>
    <div class="kha-value">{_nfs:,}</div>
    <div class="kha-sub">{_per}</div>
  </div>
  <div class="kha-card">
    <div class="kha-icon" style="background:#EDE9FE">
      <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
        <circle cx="6" cy="6.5" r="2.5" stroke="#7C3AED" stroke-width="1.5"/>
        <circle cx="11" cy="10.5" r="2.5" stroke="#7C3AED" stroke-width="1.5"/>
      </svg>
    </div>
    <div class="kha-label">Clientes</div>
    <div class="kha-value">{_clis:,}</div>
    <div class="kha-sub">únicos · período</div>
  </div>
</div>
""", unsafe_allow_html=True)

if _erro:
    st.error(f"❌ Erro ao carregar dados: {_erro}")
    st.info("Verifique se os CSVs estão na pasta `data/` e clique em **Reprocessar**.")

tab_bi, tab_dados = st.tabs(["◈  BI GRUPO AGORA MAKERS", "⚙  Dados & Cálculos"])

with tab_bi:
    from ui.abas.aba_dashboard import renderizar as _dashboard
    _dashboard(df_omp=fat_f["omp"], df_mtc=fat_f["mtc"], df_cons=fat_f["consolidado"],
               data_inicio=data_inicio, data_fim=data_fim, dark=DARK)

with tab_dados:
    from ui.abas.aba_faturamento import renderizar_empresa as _fat_emp, renderizar_consolidado as _fat_cons
    from ui.abas.aba_devolucoes  import renderizar_empresa as _esc_emp, renderizar_consolidado as _esc_cons
    from ui.abas.aba_pedidos  import renderizar_empresa as _ped_emp
    from ui.abas.aba_metas    import renderizar as _metas
    from ui.abas.aba_logica   import renderizar as _log
    from ui.abas.aba_exportar import renderizar as _exportar

    sub = st.tabs([
        "🏙️ FAT My City", "⚙️ FAT Metalco", "📊 FAT Consolidado",
        "↩️ DEV My City", "↩️ DEV Metalco", "↩️ DEV Consolidado",
        "📋 PED My City", "📋 PED Metalco",
        "🎯 Metas", "🔎 Fórmulas", "📥 Exportar",
    ])
    (s_fo, s_fm, s_fc, s_eo, s_em, s_ec, s_po, s_pm, s_met, s_log, s_exp) = sub

    with s_fo:  _fat_emp(fat_f["omp"],  "My City", n_linhas, mostrar_vazios)
    with s_fm:  _fat_emp(fat_f["mtc"],  "Metalco", n_linhas, mostrar_vazios)
    with s_fc:  _fat_cons(fat_f["consolidado"])
    with s_eo:  _esc_emp(d_esc["omp"] if d_esc else _vz, "My City", n_linhas)
    with s_em:  _esc_emp(d_esc["mtc"] if d_esc else _vz, "Metalco", n_linhas)
    with s_ec:  _esc_cons(d_esc["omp"] if d_esc else _vz, d_esc["mtc"] if d_esc else _vz)
    with s_po:  _ped_emp(ped_f["omp"], "My City", n_linhas)
    with s_pm:  _ped_emp(ped_f["mtc"], "Metalco", n_linhas)
    with s_met: _metas(fat_raw["omp"], fat_raw["mtc"])
    with s_log: _log()
    with s_exp: _exportar(d_fat, d_esc, d_ped)
