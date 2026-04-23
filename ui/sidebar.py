"""
ui/sidebar.py
Barra lateral do painel — design dark editorial.
"""

import streamlit as st
from datetime import date
import os

_LOGO_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'banco de imagens', 'logo_agoramakers.png'
)


def renderizar_sidebar(pasta_dados: str, arquivos_fn) -> dict:

    # ── Inicializar session_state ─────────────────────────────────────────────
    if "tema_escuro" not in st.session_state:
        st.session_state.tema_escuro = False
    if "sidebar_visivel" not in st.session_state:
        st.session_state.sidebar_visivel = True
    if "sb_mostrar_vazios" not in st.session_state:
        st.session_state.sb_mostrar_vazios = False
    if "sb_n_linhas" not in st.session_state:
        st.session_state.sb_n_linhas = 50

    with st.sidebar:

        # ── Botão fechar (mobile only) ─────────────────────────────────────────
        st.markdown("""
        <style>
        div[data-testid="stSidebar"] .sb-close-row { display: none; }
        @media (max-width: 768px) {
            div[data-testid="stSidebar"] .sb-close-row {
                display: flex !important;
                justify-content: flex-end;
                padding: 8px 4px 0;
            }
        }
        </style>
        <div class="sb-close-row"></div>
        """, unsafe_allow_html=True)

        col_close, _ = st.columns([10, 1])
        with col_close:
            st.markdown("""
            <style>
            div[data-testid="stSidebar"]
                div[data-testid="stHorizontalBlock"]:first-of-type
                > div:first-child button {
                display: none;
                white-space: nowrap !important;
                word-break: keep-all !important;
            }
            @media (max-width: 768px) {
                div[data-testid="stSidebar"]
                    div[data-testid="stHorizontalBlock"]:first-of-type
                    > div:first-child button {
                    display: flex !important;
                    background: rgba(255,255,255,.08) !important;
                    border: 1px solid rgba(255,255,255,.12) !important;
                    border-radius: 8px !important;
                    font-size: 13px !important;
                    font-weight: 600 !important;
                    color: rgba(255,255,255,.6) !important;
                    padding: 4px 12px !important;
                    min-width: 90px !important;
                }
            }
            </style>
            """, unsafe_allow_html=True)
            if st.button("✕ Fechar", key="sb_btn_fechar_mobile"):
                st.session_state.sidebar_visivel = False
                st.rerun()

        # ── Logo ──────────────────────────────────────────────────────────────
        st.markdown('<div style="padding:16px 4px 0;">', unsafe_allow_html=True)
        if os.path.exists(_LOGO_PATH):
            st.image(_LOGO_PATH, width=120)
        else:
            st.markdown(
                '<div style="font-size:24px;color:rgba(255,255,255,.7);">'
                '◈</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div style="padding:6px 4px 14px;">
            <div style="font-size:11.5px;font-weight:700;
                 color:rgba(255,255,255,.85);letter-spacing:-.01em;
                 line-height:1.2;">Painel Executivo</div>
            <div style="font-size:9px;color:rgba(255,255,255,.2);
                 text-transform:uppercase;letter-spacing:.14em;
                 margin-top:2px;">Agora Makers</div>
        </div>
        """, unsafe_allow_html=True)
        st.divider()

        # ── Tema ───────────────────────────────────────────────────────────────
        def _on_tema_change():
            st.session_state.tema_escuro = st.session_state["sb_toggle_tema"]
            st.rerun()

        st.toggle(
            "🌙 Tema escuro",
            key="sb_toggle_tema",
            value=st.session_state.tema_escuro,
            on_change=_on_tema_change,
        )
        st.divider()

        # ── Status de arquivos ─────────────────────────────────────────────────
        st.markdown("**📁 ARQUIVOS**")
        cores = {"omp": "#4A6D8C", "mtc": "#3D6B56"}
        nomes = {"omp": "ftc002omp.csv", "mtc": "ftc002mtc.csv"}
        try:
            disp = arquivos_fn(pasta_dados)
            for suf, existe in disp.items():
                cor = cores.get(suf, "#9E6D47")
                st.markdown(
                    f'<span style="color:{cor}">●</span>&nbsp;'
                    f'<code style="background:rgba(255,255,255,.06);'
                    f'border:1px solid rgba(255,255,255,.1);'
                    f'color:rgba(255,255,255,.45);padding:1px 6px;'
                    f'border-radius:4px;font-size:10px;">'
                    f'{nomes.get(suf, suf)}</code> '
                    f'{"✅" if existe else "❌"}',
                    unsafe_allow_html=True,
                )
        except Exception:
            st.caption("(status indisponível)")
        st.divider()

        # ── Intercompany ───────────────────────────────────────────────────────
        st.markdown("**🔀 INTERCOMPANY**")
        st.caption("Exclui transações entre empresas do grupo quando SIM.")
        flag_ic = st.selectbox(
            "Filtro IC",
            options=["NÃO", "SIM"],
            index=0,
            key="sb_flag_ic",
        )
        st.divider()

        # ── Filtro de período ──────────────────────────────────────────────────
        st.markdown("**📅 PERÍODO**")
        modo_data = st.radio(
            "Modo de período",
            options=["Atual", "Personalizado"],
            index=0,
            label_visibility="collapsed",
            key="sb_modo_data",
        )

        hoje = date.today()
        if modo_data == "Atual":
            data_inicio = None
            data_fim    = hoje
            st.caption(f"Dados até {hoje.strftime('%d/%m/%Y')}")
        else:
            c1, c2 = st.columns(2)
            with c1:
                data_inicio = st.date_input(
                    "De", value=date(hoje.year, 1, 1),
                    key="sb_data_ini", format="DD/MM/YYYY",
                )
            with c2:
                data_fim = st.date_input(
                    "Até", value=hoje,
                    key="sb_data_fim", format="DD/MM/YYYY",
                )
            if data_inicio and data_fim and data_inicio > data_fim:
                st.warning("⚠️ Data inicial maior que a final.")
        st.divider()

        # ── Visualização ───────────────────────────────────────────────────────
        st.markdown("**🔍 VISUALIZAÇÃO**")
        mostrar_vazios = st.toggle(
            "Mostrar linhas excluídas (IC/Própria)",
            key="sb_mostrar_vazios",
        )
        n_linhas = st.slider(
            "Linhas na tabela",
            min_value=10, max_value=500, value=50, step=10,
            key="sb_n_linhas",
        )
        st.divider()

        if st.button("🔄 Reprocessar", use_container_width=True,
                     type="primary", key="sb_btn_reprocessar"):
            st.cache_data.clear()
            st.rerun()

        # ── Versão ────────────────────────────────────────────────────────────
        st.markdown("""
        <div style="padding:10px 4px 6px;font-size:9px;
             color:rgba(255,255,255,.12);text-align:center;">
            abril 2026 · v3.0
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
