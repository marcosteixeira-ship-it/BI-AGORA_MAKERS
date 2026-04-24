"""
ui/estilos.py — Design system · Agora Makers (warm editorial)
"""
import streamlit as st

# ── Paleta da marca ────────────────────────────────────────────────────────────
_OMP  = "#4A6D8C"   # azul My City
_MTC  = "#3D6B56"   # verde Metalco
_CONS = "#9E6D47"   # terracota Consolidado


def _css(dark: bool) -> str:
    if dark:
        bg      = "#0E0C0A"
        surf    = "#161412"
        border  = "#2A2520"
        border2 = "#342E28"
        txt     = "#EDE8E0"
        muted   = "#8A827A"
        faint   = "#5A534E"
        shadow  = "0 1px 3px rgba(0,0,0,.40), 0 4px 16px rgba(0,0,0,.35)"
        shadow_h = "0 8px 28px rgba(0,0,0,.55), 0 2px 6px rgba(0,0,0,.40)"
        btn_sec  = "background:#2A2520;color:#8A827A;border:1px solid #342E28;"
        input_bg = "#161412"
        badge_up_bg = "rgba(61,107,86,.15)"
        badge_up_c  = _MTC
    else:
        bg      = "#F5F1EB"
        surf    = "#FDFCF9"
        border  = "#E6E1D8"
        border2 = "#D8D2C8"
        txt     = "#1A1714"
        muted   = "#7A736B"
        faint   = "#B0A99F"
        shadow  = "0 1px 3px rgba(26,23,20,.05), 0 4px 16px rgba(26,23,20,.05)"
        shadow_h = "0 8px 28px rgba(26,23,20,.09), 0 2px 6px rgba(26,23,20,.05)"
        btn_sec  = f"background:{surf};color:{muted};border:1px solid {border};"
        input_bg = surf
        badge_up_bg = "rgba(61,107,86,.08)"
        badge_up_c  = _MTC

    _dark_chart = f"""
    .js-plotly-plot .xtick text,.js-plotly-plot .ytick text,
    .js-plotly-plot .g-xtitle text,.js-plotly-plot .g-ytitle text,
    .js-plotly-plot .legendtext,.js-plotly-plot .gtitle tspan {{
        fill: {txt} !important;
    }}
    .js-plotly-plot .xgrid,.js-plotly-plot .ygrid {{
        stroke: {border} !important; opacity:.7 !important;
    }}
    [data-testid="stPlotlyChart"] > div {{ background:{surf} !important; }}
    """ if dark else ""

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ── Base ─────────────────────────────────────────────────────────────────── */
*,html,body,[class*="css"] {{
    font-family:'Inter',-apple-system,sans-serif !important;
    box-sizing:border-box;
}}

/* ══════════════════════════════════════════════════════════════════════════
   TIRA BRANCA DO TOPO — stHeader nativo do Streamlit
   O <header data-testid="stHeader"> é renderizado fora do stMain com
   background branco fixo. Removê-lo elimina a faixa branca visível no
   topo mesmo quando o app tem fundo escuro ou colorido.
══════════════════════════════════════════════════════════════════════════ */
[data-testid="stHeader"],
header[data-testid="stHeader"],
.stAppHeader {{
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
    max-height: 0 !important;
    overflow: hidden !important;
    visibility: hidden !important;
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
}}
/* Remove o padding-top que o Streamlit injeta por conta do header */
[data-testid="stAppViewContainer"] > section[data-testid="stMain"],
[data-testid="stMain"] {{
    padding-top: 0 !important;
    margin-top: 0 !important;
}}

/* ══════════════════════════════════════════════════════════════════════════
   BOTÃO NATIVO DA SIDEBAR (keyboard_double_arrow_left)
   Matar todos os seletores possíveis para não aparecer o texto do ícone.
══════════════════════════════════════════════════════════════════════════ */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
button[data-testid="stBaseButton-headerNoPadding"],
[data-testid="stIconMaterial"] {{
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
    width: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
    position: absolute !important;
    clip: rect(0,0,0,0) !important;
}}

/* ══════════════════════════════════════════════════════════════════════════
   FILTROS DAS PLANILHAS EM PORTUGUÊS
   O Streamlit usa Glide Data Grid — partes do filtro são HTML acessíveis.
   Traduzimos via atributo placeholder, labels e botões do overlay.
══════════════════════════════════════════════════════════════════════════ */
/* Placeholder da caixa de busca */
[data-testid="stDataFrame"] input[placeholder="Filter..."],
[data-testid="stDataEditor"] input[placeholder="Filter..."] {{
    font-size: 0 !important;  /* esconde texto padrão */
}}
[data-testid="stDataFrame"] input[placeholder="Filter..."]::placeholder,
[data-testid="stDataEditor"] input[placeholder="Filter..."]::placeholder {{
    font-size: .84rem !important;
    content: "Filtrar...";
}}
/* Hack: substituir placeholder via attr */
[data-testid="stDataFrame"] input[placeholder="Filter..."],
[data-testid="stDataEditor"] input[placeholder="Filter..."] {{
    font-size: .84rem !important;
}}

/* Overlay de opções do filtro — botões de tipo de filtro */
[data-testid="stDataFrame"] [role="listbox"] [role="option"]:nth-child(1)  span,
[data-testid="stDataEditor"] [role="listbox"] [role="option"]:nth-child(1) span {{ font-size:0 !important; }}
[data-testid="stDataFrame"] [role="listbox"] [role="option"]:nth-child(1)::after,
[data-testid="stDataEditor"] [role="listbox"] [role="option"]:nth-child(1)::after  {{ content:"Contém"; font-size:.84rem; }}
[data-testid="stDataFrame"] [role="listbox"] [role="option"]:nth-child(2)  span,
[data-testid="stDataEditor"] [role="listbox"] [role="option"]:nth-child(2) span {{ font-size:0 !important; }}
[data-testid="stDataFrame"] [role="listbox"] [role="option"]:nth-child(2)::after,
[data-testid="stDataEditor"] [role="listbox"] [role="option"]:nth-child(2)::after  {{ content:"Não contém"; font-size:.84rem; }}
[data-testid="stDataFrame"] [role="listbox"] [role="option"]:nth-child(3)  span,
[data-testid="stDataEditor"] [role="listbox"] [role="option"]:nth-child(3) span {{ font-size:0 !important; }}
[data-testid="stDataFrame"] [role="listbox"] [role="option"]:nth-child(3)::after,
[data-testid="stDataEditor"] [role="listbox"] [role="option"]:nth-child(3)::after  {{ content:"Igual a"; font-size:.84rem; }}
[data-testid="stDataFrame"] [role="listbox"] [role="option"]:nth-child(4)  span,
[data-testid="stDataEditor"] [role="listbox"] [role="option"]:nth-child(4) span {{ font-size:0 !important; }}
[data-testid="stDataFrame"] [role="listbox"] [role="option"]:nth-child(4)::after,
[data-testid="stDataEditor"] [role="listbox"] [role="option"]:nth-child(4)::after  {{ content:"Diferente de"; font-size:.84rem; }}
[data-testid="stDataFrame"] [role="listbox"] [role="option"]:nth-child(5)  span,
[data-testid="stDataEditor"] [role="listbox"] [role="option"]:nth-child(5) span {{ font-size:0 !important; }}
[data-testid="stDataFrame"] [role="listbox"] [role="option"]:nth-child(5)::after,
[data-testid="stDataEditor"] [role="listbox"] [role="option"]:nth-child(5)::after  {{ content:"Começa com"; font-size:.84rem; }}
[data-testid="stDataFrame"] [role="listbox"] [role="option"]:nth-child(6)  span,
[data-testid="stDataEditor"] [role="listbox"] [role="option"]:nth-child(6) span {{ font-size:0 !important; }}
[data-testid="stDataFrame"] [role="listbox"] [role="option"]:nth-child(6)::after,
[data-testid="stDataEditor"] [role="listbox"] [role="option"]:nth-child(6)::after  {{ content:"Termina com"; font-size:.84rem; }}

/* ── App background ───────────────────────────────────────────────────────── */
.stApp,.main,section.main,
[data-testid="stAppViewContainer"],
[data-testid="stMainBlockContainer"] {{ background:{bg} !important; }}
.main .block-container,
[data-testid="stMainBlockContainer"] {{
    background:{bg} !important;
    padding:0 !important; max-width:100% !important;
}}
.main .block-container > div:first-child,
[data-testid="stMainBlockContainer"] > div:first-child {{
    padding:1rem 1.4rem 2rem !important;
}}

/* ══════════════════════════════════════════════════════════════════════════
   MASTHEAD — dark editorial
══════════════════════════════════════════════════════════════════════════ */
.masthead {{
    background:#0E0C0A;
    border-radius:16px;
    margin-bottom:20px;
    border:1px solid rgba(255,255,255,.06);
    box-shadow:0 1px 0 rgba(255,255,255,.03) inset, 0 20px 60px rgba(0,0,0,.25);
    overflow:hidden;
}}
.masthead-rule {{
    height:2px;
    background:linear-gradient(90deg,{_OMP},{_MTC},{_CONS});
}}
.masthead-body {{
    display:flex; align-items:flex-start; justify-content:space-between;
    gap:20px; padding:22px 28px 24px; flex-wrap:wrap;
}}
.masthead-left {{
    display:flex; align-items:flex-start; gap:14px;
    flex:1; min-width:200px;
}}
.masthead-logo-wrap {{
    width:42px; height:42px; border-radius:9px;
    background:rgba(255,255,255,.06);
    border:1px solid rgba(255,255,255,.10);
    display:flex; align-items:center; justify-content:center;
    flex-shrink:0; overflow:hidden; padding:4px;
}}
.masthead-logo-wrap img {{
    width:34px; height:34px; object-fit:contain; display:block;
}}
.masthead-right {{ flex-shrink:0; max-width:60%; }}
.masthead-eyebrow {{
    font-size:9.5px; font-weight:600; color:rgba(255,255,255,.25);
    text-transform:uppercase; letter-spacing:.14em; margin-bottom:6px;
}}
.masthead-brand {{
    font-size:clamp(.9rem,1.6vw,1.2rem);
    font-weight:900; color:rgba(255,255,255,.88);
    letter-spacing:-.02em; line-height:1.1;
}}
.masthead-chips {{
    display:flex; gap:6px; flex-wrap:wrap; margin-top:10px;
}}
.mchip {{
    display:inline-flex; align-items:center; gap:5px;
    background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.09);
    color:rgba(255,255,255,.55); font-size:.67rem; font-weight:600;
    padding:3px 9px; border-radius:100px;
}}
.mchip-live {{
    color:{_MTC} !important;
    border-color:rgba(61,107,86,.4) !important;
    background:rgba(61,107,86,.1) !important;
}}
.live-dot {{
    width:5px; height:5px; border-radius:50%; background:{_MTC};
    display:inline-block; margin-right:2px;
    animation:liveGlow 2s ease infinite;
}}
@keyframes liveGlow {{
    0%,100% {{ box-shadow:0 0 0 0 rgba(61,107,86,.5); }}
    50%      {{ box-shadow:0 0 0 5px rgba(61,107,86,0); }}
}}
@keyframes fadeUp {{
    from {{ opacity:0; transform:translateY(10px); }}
    to   {{ opacity:1; transform:translateY(0); }}
}}
.mstat-group {{
    display:flex; gap:0; align-items:flex-start; justify-content:flex-end;
}}
.mstat {{ padding:0; }}
.mstat + .mstat {{
    border-left:1px solid rgba(255,255,255,.1);
    padding-left:24px; margin-left:24px;
}}
.mstat-val {{
    font-size:clamp(1.4rem,2.2vw,2rem);
    font-weight:900; color:rgba(255,255,255,.9);
    letter-spacing:-.05em; line-height:1;
}}
.mstat-val-sm {{
    font-size:clamp(.9rem,1.4vw,1.3rem);
    font-weight:900; color:rgba(255,255,255,.9);
    letter-spacing:-.04em; line-height:1;
}}
.mstat-lbl {{
    font-size:.67rem; color:rgba(255,255,255,.28);
    text-transform:uppercase; letter-spacing:.09em;
    margin-top:5px; font-weight:600;
}}
.mprogress-bar {{ margin-top:16px; }}
.mprogress-label {{
    display:flex; justify-content:space-between; margin-bottom:6px;
}}
.mprogress-label span:first-child {{
    font-size:9.5px; text-transform:uppercase; letter-spacing:.1em;
    font-weight:600; color:rgba(255,255,255,.25);
}}
.mprogress-label span:last-child {{
    font-size:11px; color:rgba(255,255,255,.6); font-weight:700;
}}
.mprogress-track {{
    height:3px; background:rgba(255,255,255,.08);
    border-radius:100px; overflow:hidden;
}}
.mprogress-fill {{
    height:100%; border-radius:100px;
    background:linear-gradient(90deg,{_OMP},{_CONS});
}}

/* ══════════════════════════════════════════════════════════════════════════
   KPI HEADER / CARDS
══════════════════════════════════════════════════════════════════════════ */
.kpi-hdr {{
    display:grid;
    grid-template-columns:repeat(7,minmax(0,1fr));
    gap:10px; margin-bottom:16px;
}}
.kha-card,.kpi-card {{
    background:{surf};
    border-radius:12px; padding:16px;
    border:1px solid {border};
    box-shadow:{shadow};
    transition:box-shadow .25s ease, transform .25s ease;
    position:relative; overflow:hidden;
    cursor:default;
}}
.kha-card:hover,.kpi-card:hover {{
    box-shadow:{shadow_h};
    transform:translateY(-1px);
}}
.kha-icon {{
    position:absolute; right:10px; top:10px;
    width:26px; height:26px; border-radius:6px;
    display:flex; align-items:center; justify-content:center;
    flex-shrink:0;
}}
.kha-label,.kpi-label {{
    font-size:.6rem; font-weight:700;
    text-transform:uppercase; letter-spacing:.1em;
    color:{faint};
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
    padding-right:30px;
}}
.kha-value,.kpi-value {{
    font-size:1.12rem; font-weight:900;
    letter-spacing:-.04em; line-height:1.15;
    color:{txt}; word-break:break-word; margin-top:3px;
}}
.kha-sub,.kpi-sub {{
    font-size:.64rem; color:{faint};
    margin-top:4px; font-weight:500;
}}
.kpi-grid {{
    display:grid;
    grid-template-columns:repeat(7,1fr);
    gap:10px; margin:0 0 4px;
}}
.kpi-top {{ display:flex; align-items:center; gap:7px; margin-bottom:8px; }}
.kpi-icon {{
    width:28px; height:28px; border-radius:7px;
    display:flex; align-items:center; justify-content:center;
    font-size:.9rem; flex-shrink:0;
}}
.kpi-badge {{
    display:inline-flex; align-items:center; gap:2px;
    padding:2px 8px; border-radius:100px;
    font-size:9.5px; font-weight:600; margin-top:5px;
}}
.badge-up   {{ background:{badge_up_bg}; color:{badge_up_c}; }}
.badge-down {{ background:#FFE4EC; color:#E11D48; }}
.badge-neu  {{ background:{surf}; color:{muted}; border:1px solid {border}; }}

/* ══════════════════════════════════════════════════════════════════════════
   SIDEBAR — always dark
══════════════════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {{
    display:flex !important; visibility:visible !important;
    transform:translateX(0) !important; opacity:1 !important;
    background:#0E0C0A !important;
    border-right:1px solid rgba(255,255,255,.06) !important;
    min-width:230px !important;
}}
[data-testid="stSidebar"] > div {{ background:#0E0C0A !important; }}
[data-testid="stSidebar"] * {{ color:rgba(255,255,255,.5) !important; }}
[data-testid="stSidebar"] strong {{
    color:rgba(255,255,255,.72) !important; font-weight:700 !important;
}}
[data-testid="stSidebar"] label {{
    color:rgba(255,255,255,.2) !important; font-size:.65rem !important;
    text-transform:uppercase; letter-spacing:.09em; font-weight:600;
}}
[data-testid="stSidebar"] .stMarkdown p {{
    color:rgba(255,255,255,.5) !important; font-size:.82rem !important;
}}
[data-testid="stSidebar"] hr {{
    border-color:rgba(255,255,255,.06) !important; opacity:1 !important;
}}
[data-testid="stSidebar"] .stButton button {{
    background:rgba(255,255,255,.06) !important;
    border:1px solid rgba(255,255,255,.1) !important;
    color:rgba(255,255,255,.55) !important; font-weight:600 !important;
    border-radius:8px !important; transition:all .2s !important;
    white-space:nowrap !important; word-break:keep-all !important;
}}
[data-testid="stSidebar"] .stButton button[kind="primary"] {{
    background:{_MTC} !important; border:none !important;
    color:white !important;
    box-shadow:0 2px 10px rgba(61,107,86,.28) !important;
}}
/* Botões nativos de colapso — já tratados no bloco acima */
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {{
    background:#161412 !important; border-color:rgba(255,255,255,.1) !important;
    color:rgba(255,255,255,.6) !important; border-radius:8px !important;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] label {{
    color:rgba(255,255,255,.5) !important; font-size:.84rem !important;
    text-transform:none !important; letter-spacing:0 !important;
}}
[data-testid="stSidebar"] input[type="range"] {{
    accent-color:{_MTC} !important;
}}
[data-testid="stSidebar"] [data-testid="stImage"] img {{
    filter:brightness(0) invert(1) !important;
    opacity:.8 !important;
}}

/* ══════════════════════════════════════════════════════════════════════════
   CHARTS (Plotly)
══════════════════════════════════════════════════════════════════════════ */
[data-testid="stPlotlyChart"] > div {{
    background:{surf} !important;
    border-radius:13px !important; padding:4px !important;
    box-shadow:{shadow} !important;
    border:1px solid {border} !important;
    transition:box-shadow .25s ease, transform .25s ease !important;
}}
[data-testid="stPlotlyChart"] > div:hover {{
    box-shadow:{shadow_h} !important;
    transform:translateY(-1px) !important;
}}

/* ══════════════════════════════════════════════════════════════════════════
   ABAS / TABS
══════════════════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {{
    background:{surf} !important;
    border-radius:11px !important; padding:4px !important;
    gap:2px !important; flex-wrap:wrap !important;
    border:1px solid {border} !important;
    box-shadow:{shadow} !important;
    margin-bottom:20px !important;
}}
.stTabs [data-baseweb="tab"] {{
    color:{faint} !important; border-radius:8px !important;
    font-size:.79rem !important; font-weight:600 !important;
    padding:7px 18px !important; white-space:nowrap !important;
    transition:all .2s !important; max-width:220px !important;
    background:transparent !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
    background:rgba(26,23,20,.04) !important; color:{muted} !important;
}}
.stTabs [aria-selected="true"] {{
    background:{txt} !important; color:#FDFCF9 !important;
    font-weight:700 !important;
    box-shadow:0 2px 8px rgba(26,23,20,.18) !important; border:none !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
    background:{bg} !important; padding:16px 0 !important;
}}
/* Sub-tabs */
.stTabs .stTabs [data-baseweb="tab-list"] {{
    background:rgba(26,23,20,.04) !important;
    border:1px solid {border} !important;
    border-radius:10px !important; padding:4px !important;
}}
.stTabs .stTabs [data-baseweb="tab"] {{
    font-size:.72rem !important; padding:5px 11px !important;
    font-weight:500 !important;
}}
.stTabs .stTabs [aria-selected="true"] {{
    background:{surf} !important; color:{txt} !important;
    font-weight:700 !important;
    box-shadow:0 1px 4px rgba(26,23,20,.07) !important;
    border:1px solid {border} !important;
}}

/* ══════════════════════════════════════════════════════════════════════════
   SELETOR EMPRESA
══════════════════════════════════════════════════════════════════════════ */
.emp-toggle {{ margin-bottom:4px; }}
.emp-toggle .stButton button {{
    border-radius:100px !important;
    font-size:.80rem !important; font-weight:600 !important;
    padding:7px 18px !important;
    transition:all .22s ease !important;
    {btn_sec}
}}

/* ══════════════════════════════════════════════════════════════════════════
   DATAFRAMES
══════════════════════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"],[data-testid="stDataEditor"] {{
    background:{surf} !important; border-radius:12px !important;
    overflow:hidden !important; box-shadow:{shadow} !important;
    border:1px solid {border} !important;
}}

/* ══════════════════════════════════════════════════════════════════════════
   SEÇÕES E BADGES
══════════════════════════════════════════════════════════════════════════ */
.titulo-sec {{
    font-size:9.5px; font-weight:700; color:{faint};
    text-transform:uppercase; letter-spacing:.14em;
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
    display:flex; align-items:center; gap:12px;
    margin:24px 0 14px;
}}
.titulo-sec::after {{ content:''; flex:1; height:1px; background:{border}; }}
.badge-sim {{
    background:{badge_up_bg}; color:{badge_up_c};
    padding:3px 10px; border-radius:100px;
    font-weight:700; font-size:.72rem; display:inline-block;
}}
.badge-nao {{
    background:{surf}; color:{muted};
    padding:3px 10px; border-radius:100px;
    font-weight:600; font-size:.72rem; display:inline-block;
    border:1px solid {border};
}}
.periodo-badge {{
    display:inline-flex; align-items:center; gap:5px;
    background:{surf}; color:{muted};
    font-size:.72rem; font-weight:500;
    padding:4px 12px; border-radius:100px;
    border:1px solid {border};
}}
.alerta-dev {{
    background:#FFFBEB; border:.5px solid #F59E0B;
    border-left:4px solid #F59E0B;
    border-radius:10px; padding:14px 18px;
    font-size:.84rem; color:#92400E; margin:12px 0;
}}
.empty-state {{ text-align:center; padding:60px 20px; }}
.empty-icon  {{ font-size:3rem; margin-bottom:12px; }}
.empty-title {{ font-size:1rem; font-weight:700; color:{txt}; margin-bottom:6px; }}
.empty-sub   {{ font-size:.84rem; color:{muted}; max-width:420px; margin:0 auto; }}

/* ══════════════════════════════════════════════════════════════════════════
   ST.METRIC
══════════════════════════════════════════════════════════════════════════ */
[data-testid="stMetricValue"] > div,
[data-testid="stMetricValue"] {{
    white-space:normal !important; overflow:visible !important;
    text-overflow:unset !important; word-break:break-word !important;
    font-size:clamp(.82rem,1.8vw,1.12rem) !important;
    font-weight:900 !important; color:{txt} !important;
    letter-spacing:-0.04em !important;
}}
[data-testid="stMetricLabel"] > div,
[data-testid="stMetricLabel"] {{
    white-space:normal !important; overflow:visible !important;
    font-size:clamp(.6rem,1.1vw,.72rem) !important;
    font-weight:700 !important; text-transform:uppercase !important;
    letter-spacing:.1em !important; color:{faint} !important;
    line-height:1.3 !important;
}}
[data-testid="stMetricDelta"] {{
    font-size:.70rem !important; font-weight:600 !important;
}}

/* ══════════════════════════════════════════════════════════════════════════
   TEXTOS E INPUTS
══════════════════════════════════════════════════════════════════════════ */
h1,h2,h3,h4,h5,h6 {{
    color:{txt} !important; font-weight:900 !important;
    letter-spacing:-.02em !important;
}}
.stMarkdown p,.stMarkdown li {{ color:{txt} !important; }}
.stMarkdown code {{
    background:{surf} !important; color:{txt} !important;
    padding:2px 7px; border-radius:5px; font-size:.84em;
    border:1px solid {border} !important;
}}
small,.stCaption,[data-testid="stCaptionContainer"] {{
    color:{muted} !important; font-size:.77rem !important;
}}
hr {{ border-color:{border} !important; opacity:.8 !important; }}
[data-testid="stAlert"] {{ border-radius:10px !important; border-left-width:4px !important; }}
[data-testid="stSelectbox"] > div > div {{
    background:{input_bg} !important; border-color:{border} !important;
    color:{txt} !important; border-radius:8px !important;
}}
[data-testid="stRadio"] label {{ color:{txt} !important; font-size:.84rem !important; }}
[data-testid="stSpinner"] {{ color:{_MTC} !important; }}

/* ── Botão primary ───────────────────────────────────────────────────────── */
.stButton button[kind="primary"] {{
    background:{_MTC} !important; border:none !important;
    color:white !important; font-weight:700 !important;
    border-radius:8px !important; padding:7px 18px !important;
    box-shadow:0 2px 10px rgba(61,107,86,.28) !important;
    transition:all .18s ease !important;
    white-space:nowrap !important;
}}
.stButton button[kind="primary"]:hover {{
    background:#2D5A46 !important;
    transform:translateY(-1px) !important;
    box-shadow:0 4px 18px rgba(61,107,86,.38) !important;
}}

/* ── Toggle sidebar button ───────────────────────────────────────────────── */
[data-testid="column"] {{
    min-width:100px !important; width:auto !important;
}}
[data-testid="column"] button {{
    white-space:nowrap !important; word-break:keep-all !important;
    min-width:90px !important;
}}

/* ── Ocultar chrome Streamlit ─────────────────────────────────────────────── */
#MainMenu, footer, .stDeployButton,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {{
    display: none !important;
}}

{_dark_chart}

/* ══════════════════════════════════════════════════════════════════════════
   RESPONSIVO
══════════════════════════════════════════════════════════════════════════ */
@media (max-width:1400px) {{
    .kpi-hdr  {{ grid-template-columns:repeat(4,minmax(0,1fr)); }}
    .kpi-grid {{ grid-template-columns:repeat(4,1fr); }}
}}
@media (max-width:900px) {{
    .main .block-container > div:first-child {{ padding:.8rem !important; }}
    .kpi-hdr  {{ grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px; }}
    .kpi-grid {{ grid-template-columns:repeat(3,1fr); gap:8px; }}
    .masthead-body {{ padding:16px 18px 18px; gap:14px; }}
    .masthead-right {{ max-width:100%; width:100%; }}
    .stTabs [data-baseweb="tab"] {{ font-size:.72rem !important; padding:5px 10px !important; }}
    [data-testid="stPlotlyChart"] > div {{ border-radius:8px !important; }}
    .main [data-testid="stHorizontalBlock"] {{ flex-wrap:wrap !important; gap:8px !important; }}
    .main [data-testid="stHorizontalBlock"] > div {{
        min-width:calc(50% - 4px) !important;
        flex:1 1 calc(50% - 4px) !important; max-width:100% !important;
    }}
}}
@media (max-width:640px) {{
    .main .block-container > div:first-child {{ padding:.4rem .5rem 1rem !important; }}
    .kpi-hdr  {{ grid-template-columns:repeat(2,minmax(0,1fr)); gap:6px; }}
    .kpi-grid {{ grid-template-columns:repeat(2,1fr); gap:6px; }}
    .kha-card,.kpi-card {{ padding:10px 10px 8px; }}
    .kha-value,.kpi-value {{ font-size:.95rem; }}
    .masthead-body {{ padding:16px 18px; gap:12px; }}
    .mstat-val {{ font-size:1.5rem; }}
    .masthead-right {{ max-width:100%; }}
}}
</style>
"""


def aplicar_css(dark: bool = False) -> None:
    st.markdown(_css(dark), unsafe_allow_html=True)
