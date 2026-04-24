"""
ui/sidebar.py — Barra lateral · Agora Makers
"""
import streamlit as st
from datetime import date


def renderizar_sidebar(pasta_dados: str, arquivos_fn) -> dict:

    if "tema_escuro" not in st.session_state:
        st.session_state.tema_escuro = False
    if "sidebar_visivel" not in st.session_state:
        st.session_state.sidebar_visivel = True
    if "sb_mostrar_vazios" not in st.session_state:
        st.session_state.sb_mostrar_vazios = False
    if "sb_n_linhas" not in st.session_state:
        st.session_state.sb_n_linhas = 50

    with st.sidebar:

        # ── Botão fechar mobile ────────────────────────────────────────────────
        st.markdown("""
        <style>
        div[data-testid="stSidebar"]
            div[data-testid="stHorizontalBlock"]:first-of-type
            > div:first-child button { display: none !important; }
        @media (max-width: 768px) {
            div[data-testid="stSidebar"]
                div[data-testid="stHorizontalBlock"]:first-of-type
                > div:first-child button {
                display: flex !important;
                background: rgba(255,255,255,.08) !important;
                border: 1px solid rgba(255,255,255,.14) !important;
                border-radius: 8px !important;
                font-size: 12px !important;
                font-weight: 600 !important;
                color: rgba(255,255,255,.65) !important;
                padding: 4px 12px !important;
                margin: 6px 0 0 0 !important;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        col_close, _ = st.columns([1, 3])
        with col_close:
            if st.button("✕ Fechar", key="sb_btn_fechar_mobile"):
                st.session_state.sidebar_visivel = False
                st.rerun()

        # ── Logo Agora Makers ─────────────────────────────────────────────────
        st.markdown("""
        <div style="padding: 20px 16px 8px; text-align: center;">
            <!-- Logo SVG Agora Makers -->
            <div style="
                width: 64px; height: 64px;
                background: linear-gradient(135deg, #1A3A5C 0%, #0D2040 100%);
                border-radius: 16px;
                border: 1px solid rgba(255,255,255,.12);
                display: flex; align-items: center; justify-content: center;
                margin: 0 auto 12px;
                box-shadow: 0 8px 24px rgba(0,0,0,.35), 0 1px 0 rgba(255,255,255,.08) inset;
            ">
                <svg viewBox="0 0 40 40" width="36" height="36" fill="none">
                    <!-- Grade 2x2 estilizada -->
                    <rect x="4"  y="4"  width="14" height="14" rx="3.5" fill="white" opacity=".90"/>
                    <rect x="22" y="4"  width="14" height="14" rx="3.5" fill="white" opacity=".55"/>
                    <rect x="4"  y="22" width="14" height="14" rx="3.5" fill="white" opacity=".55"/>
                    <rect x="22" y="22" width="14" height="14" rx="3.5" fill="#5CB88A" opacity=".90"/>
                    <!-- Detalhe central -->
                    <circle cx="20" cy="20" r="2.5" fill="white" opacity=".35"/>
                </svg>
            </div>
            <div style="
                font-size: 13.5px; font-weight: 800;
                color: rgba(255,255,255,.88);
                letter-spacing: -.02em; line-height: 1.2;
            ">Agora Makers</div>
            <div style="
                font-size: 9px; font-weight: 600;
                color: rgba(255,255,255,.25);
                text-transform: uppercase; letter-spacing: .14em;
                margin-top: 3px;
            ">Painel Executivo · BI</div>
            <!-- Linha degradê -->
            <div style="
                height: 1.5px; margin: 14px 0 0;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,.12), transparent);
            "></div>
        </div>
        """, unsafe_allow_html=True)

        # ── Status arquivos ───────────────────────────────────────────────────
        st.markdown("""
        <div style="padding: 10px 16px 4px;">
            <div style="font-size:9px;font-weight:700;color:rgba(255,255,255,.22);
                 text-transform:uppercase;letter-spacing:.12em;margin-bottom:8px;">
                📁 Fontes de dados
            </div>
        </div>
        """, unsafe_allow_html=True)
        cores = {"omp": "#4A8AC4", "mtc": "#5CB88A"}
        nomes = {"omp": "ftc002omp.csv", "mtc": "ftc002mtc.csv"}
        labels = {"omp": "My City", "mtc": "Metalco"}
        try:
            disp = arquivos_fn(pasta_dados)
            for suf, existe in disp.items():
                cor = cores.get(suf, "#999")
                icone = "✅" if existe else "❌"
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:8px;'
                    f'padding:5px 16px;font-size:.78rem;">'
                    f'<span style="color:{cor};font-size:10px;">●</span>'
                    f'<span style="color:rgba(255,255,255,.55);">{labels.get(suf,suf)}</span>'
                    f'<span style="margin-left:auto;font-size:.7rem;">{icone}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        except Exception:
            st.caption("(status indisponível)")

        st.markdown('<div style="height:1px;margin:10px 16px;background:rgba(255,255,255,.06);"></div>',
                    unsafe_allow_html=True)

        # ── Tema ─────────────────────────────────────────────────────────────
        def _on_tema_change():
            st.session_state.tema_escuro = st.session_state["sb_toggle_tema"]
            st.rerun()

        st.toggle("🌙  Tema escuro", key="sb_toggle_tema",
                  value=st.session_state.tema_escuro, on_change=_on_tema_change)

        st.markdown('<div style="height:1px;margin:8px 0;background:rgba(255,255,255,.06);"></div>',
                    unsafe_allow_html=True)

        # ── Intercompany ──────────────────────────────────────────────────────
        st.markdown("""
        <div style="padding:4px 0 2px;">
            <div style="font-size:9px;font-weight:700;color:rgba(255,255,255,.22);
                 text-transform:uppercase;letter-spacing:.12em;margin-bottom:4px;">
                🔀 Intercompany
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Exclui transações entre empresas do grupo quando SIM.")
        flag_ic = st.selectbox("Filtro IC", options=["NÃO", "SIM"], index=0, key="sb_flag_ic",
                               label_visibility="collapsed")

        st.markdown('<div style="height:1px;margin:10px 0;background:rgba(255,255,255,.06);"></div>',
                    unsafe_allow_html=True)

        # ── Período ───────────────────────────────────────────────────────────
        st.markdown("""
        <div style="padding:4px 0 2px;">
            <div style="font-size:9px;font-weight:700;color:rgba(255,255,255,.22);
                 text-transform:uppercase;letter-spacing:.12em;margin-bottom:4px;">
                📅 Período
            </div>
        </div>
        """, unsafe_allow_html=True)
        modo_data = st.radio("Modo", options=["Atual", "Personalizado"], index=0,
                             label_visibility="collapsed", key="sb_modo_data",
                             horizontal=True)
        hoje = date.today()
        if modo_data == "Atual":
            data_inicio = None
            data_fim    = hoje
            st.caption(f"Dados até {hoje.strftime('%d/%m/%Y')}")
        else:
            c1, c2 = st.columns(2)
            with c1:
                data_inicio = st.date_input("De", value=date(hoje.year, 1, 1),
                                            key="sb_data_ini", format="DD/MM/YYYY")
            with c2:
                data_fim = st.date_input("Até", value=hoje,
                                         key="sb_data_fim", format="DD/MM/YYYY")
            if data_inicio and data_fim and data_inicio > data_fim:
                st.warning("⚠️ Data inicial maior que a final.")

        st.markdown('<div style="height:1px;margin:10px 0;background:rgba(255,255,255,.06);"></div>',
                    unsafe_allow_html=True)

        # ── Visualização ──────────────────────────────────────────────────────
        st.markdown("""
        <div style="padding:4px 0 2px;">
            <div style="font-size:9px;font-weight:700;color:rgba(255,255,255,.22);
                 text-transform:uppercase;letter-spacing:.12em;margin-bottom:4px;">
                🔍 Visualização
            </div>
        </div>
        """, unsafe_allow_html=True)
        mostrar_vazios = st.toggle("Mostrar linhas excluídas (IC/Própria)",
                                   key="sb_mostrar_vazios")
        n_linhas = st.slider("Linhas na tabela", min_value=10, max_value=500,
                             value=50, step=10, key="sb_n_linhas")

        st.markdown('<div style="height:1px;margin:12px 0 10px;background:rgba(255,255,255,.06);"></div>',
                    unsafe_allow_html=True)

        if st.button("🔄  Reprocessar dados", use_container_width=True,
                     type="primary", key="sb_btn_reprocessar"):
            st.cache_data.clear()
            st.rerun()

        # Rodapé da sidebar
        st.markdown("""
        <div style="margin-top:24px;padding:12px 16px;
             border-top:1px solid rgba(255,255,255,.06);
             text-align:center;">
            <div style="font-size:8.5px;color:rgba(255,255,255,.18);
                 letter-spacing:.08em;text-transform:uppercase;">
                My City · Metalco · My Equilibria
            </div>
            <div style="font-size:8px;color:rgba(255,255,255,.12);margin-top:3px;">
                © Agora Makers · ISO 9001:2015 · FSC
            </div>
        </div>
        """, unsafe_allow_html=True)

    return {
        "flag_ic":        flag_ic,
        "mostrar_vazios": mostrar_vazios,
        "n_linhas":       n_linhas,
        "data_inicio":    data_inicio,
        "data_fim":       data_fim,
        "tema_escuro":    st.session_state.get("tema_escuro", False),
    }
