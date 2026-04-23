"""
ui/abas/aba_metas.py
Aba editável de distribuidores, metas anuais e sazonalidade.
Persiste em data/metas_config.json.
"""
import streamlit as st
import pandas as pd
import json
import os
import plotly.graph_objects as go
from ui.componentes.cards import titulo_secao

_CFG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "metas_config.json")

MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
         "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
MESES_NUM = {m: i + 1 for i, m in enumerate(MESES)}

_SAZON_PADRAO = [7.0, 7.5, 8.0, 9.0, 9.5, 12.0,
                 11.5, 10.5, 9.5, 8.5, 8.5, 9.0]

_FONT = "Outfit, system-ui, -apple-system, sans-serif"
_WHITE = "rgba(0,0,0,0)"
_GRID  = "#F1F5F9"


def _carregar_config() -> dict:
    if os.path.exists(_CFG_PATH):
        try:
            with open(_CFG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "distribuidores": [
            {"Distribuidor": "", "Meta OMP (R$)": 0.0, "Meta Metalco (R$)": 0.0}
        ],
        "sazonalidade": {m: p for m, p in zip(MESES, _SAZON_PADRAO)},
    }


def _salvar_config(cfg: dict) -> None:
    try:
        os.makedirs(os.path.dirname(_CFG_PATH), exist_ok=True)
        with open(_CFG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _grafico_meta_real(df_proj: pd.DataFrame, cp: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_proj["Mês"], y=df_proj["_meta_val"],
        name="Meta", marker_color="#CBD5E1",
        hovertemplate="<b>%{x}</b><br>Meta: R$ %{y:,.0f}<extra></extra>",
    ))
    cores = [
        "#10B981" if r >= 100 else ("#F59E0B" if r >= 70 else "#EF4444")
        for r in df_proj["_ating"]
    ]
    fig.add_trace(go.Bar(
        x=df_proj["Mês"], y=df_proj["_real_val"],
        name="Realizado", marker_color=cores,
        hovertemplate="<b>%{x}</b><br>Realizado: R$ %{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        height=260, barmode="overlay",
        paper_bgcolor=_WHITE, plot_bgcolor=_WHITE,
        font=dict(family=_FONT, size=11, color="#374151"),
        margin=dict(l=8, r=8, t=8, b=8),
        legend=dict(orientation="h", y=1.06, x=1, xanchor="right",
                    font=dict(size=10)),
        yaxis=dict(tickprefix="R$ ", tickformat=",.0f", gridcolor=_GRID,
                   linecolor="#E2E8F0"),
        xaxis=dict(gridcolor=_GRID, linecolor="#E2E8F0"),
        hoverlabel=dict(bgcolor="white", bordercolor="#E2E8F0",
                        font_size=12, font_family=_FONT),
    )
    return fig


def renderizar(df_fat_omp: pd.DataFrame, df_fat_mtc: pd.DataFrame) -> None:
    if "metas_cfg" not in st.session_state:
        st.session_state.metas_cfg = _carregar_config()

    cfg = st.session_state.metas_cfg

    # ── Distribuidores ────────────────────────────────────────────────────────
    titulo_secao("🏢 Distribuidores e Metas Anuais")
    st.caption("Adicione ou edite linhas. Clique em **Salvar** para persistir.")

    df_dist = pd.DataFrame(cfg.get("distribuidores", []))
    colunas_esperadas = ["Distribuidor", "Meta OMP (R$)", "Meta Metalco (R$)"]
    if df_dist.empty or list(df_dist.columns) != colunas_esperadas:
        df_dist = pd.DataFrame([{c: ("" if i == 0 else 0.0)
                                  for i, c in enumerate(colunas_esperadas)}])

    edited_dist = st.data_editor(
        df_dist,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Distribuidor": st.column_config.TextColumn(
                "Distribuidor (Razão Social)", width="large"),
            "Meta OMP (R$)": st.column_config.NumberColumn(
                "Meta OMP (R$)", format="R$ %.2f", min_value=0),
            "Meta Metalco (R$)": st.column_config.NumberColumn(
                "Meta Metalco (R$)", format="R$ %.2f", min_value=0),
        },
        key="editor_dist",
    )

    # ── Sazonalidade ──────────────────────────────────────────────────────────
    titulo_secao("📅 Sazonalidade — Distribuição Mensal da Meta (%)")
    st.caption("Percentual de cada mês sobre a meta anual total. Deve somar 100%.")

    sazon = cfg.get("sazonalidade",
                    {m: p for m, p in zip(MESES, _SAZON_PADRAO)})
    df_sazon = pd.DataFrame([
        {"Mês": m, "% da Meta": float(sazon.get(m, 0.0))}
        for m in MESES
    ])

    col_sz, col_gap = st.columns([1, 2])
    with col_sz:
        edited_sazon = st.data_editor(
            df_sazon,
            num_rows="fixed",
            use_container_width=True,
            hide_index=True,
            column_config={
                "Mês": st.column_config.TextColumn("Mês", disabled=True, width="small"),
                "% da Meta": st.column_config.NumberColumn(
                    "% da Meta", format="%.2f%%", min_value=0.0, max_value=100.0),
            },
            key="editor_sazon",
        )
    with col_gap:
        soma = edited_sazon["% da Meta"].sum()
        delta = soma - 100
        if abs(delta) < 0.01:
            st.success(f"✅ Soma: {soma:.2f}%")
        else:
            st.warning(f"⚠️ Soma: **{soma:.2f}%** — ajuste {delta:+.2f}% para totalizar 100%.")

        # Gráfico da sazonalidade
        fig_sz = go.Figure(go.Bar(
            x=edited_sazon["Mês"], y=edited_sazon["% da Meta"],
            marker=dict(
                color=edited_sazon["% da Meta"],
                colorscale=[[0, "#DBEAFE"], [1, "#1A56DB"]],
                line=dict(width=0),
            ),
            text=[f"{v:.1f}%" for v in edited_sazon["% da Meta"]],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>%{y:.2f}%<extra></extra>",
        ))
        fig_sz.update_layout(
            height=220, paper_bgcolor=_WHITE, plot_bgcolor=_WHITE,
            font=dict(family=_FONT, size=11),
            margin=dict(l=4, r=4, t=4, b=4),
            yaxis=dict(ticksuffix="%", gridcolor=_GRID, linecolor="#E2E8F0"),
            xaxis=dict(gridcolor=_GRID, linecolor="#E2E8F0"),
            showlegend=False,
        )
        st.plotly_chart(fig_sz, use_container_width=True)

    # ── Salvar ────────────────────────────────────────────────────────────────
    if st.button("💾 Salvar configurações", type="primary", use_container_width=False):
        nova_cfg = {
            "distribuidores": edited_dist.to_dict("records"),
            "sazonalidade": dict(zip(edited_sazon["Mês"], edited_sazon["% da Meta"])),
        }
        st.session_state.metas_cfg = nova_cfg
        _salvar_config(nova_cfg)
        st.success("✅ Configurações salvas com sucesso!")
        st.rerun()

    st.divider()

    # ── Projeção mensal ────────────────────────────────────────────────────────
    titulo_secao("📊 Projeção de Metas por Mês × Realizado")

    dist_valid = edited_dist[
        edited_dist["Distribuidor"].astype(str).str.strip() != ""
    ] if not edited_dist.empty else pd.DataFrame()

    if dist_valid.empty:
        st.info("Adicione ao menos um distribuidor com meta para ver a projeção.")
        return

    sazon_vals = (
        edited_sazon.set_index("Mês")["% da Meta"].astype(float) / 100.0
    )

    col_omp, col_mtc = st.columns(2, gap="large")

    for widget_col, label, meta_col, df_real, cp in [
        (col_omp, "🏙️ My City (OMP)",    "Meta OMP (R$)",     df_fat_omp, "#1A56DB"),
        (col_mtc, "⚙️ Metalco",           "Meta Metalco (R$)", df_fat_mtc, "#057A55"),
    ]:
        with widget_col:
            st.markdown(f"**{label}**")
            meta_total = (
                dist_valid[meta_col].sum()
                if meta_col in dist_valid.columns else 0.0
            )
            if meta_total <= 0:
                st.info(f"Meta total: R$ 0 — defina as metas na tabela acima.")
                continue

            st.metric(
                "Meta Anual Total",
                f"R$ {meta_total:,.0f}",
                help="Soma das metas de todos os distribuidores",
            )

            rows = []
            for mes in MESES:
                pct_m = float(sazon_vals.get(mes, 0.0))
                meta_m = meta_total * pct_m
                real_m = 0.0
                if (not df_real.empty
                        and "Data de emissão" in df_real.columns
                        and "Valor total" in df_real.columns):
                    mes_num = MESES_NUM[mes]
                    dt = pd.to_datetime(df_real["Data de emissão"], errors="coerce")
                    mask = dt.dt.month == mes_num
                    real_m = float(df_real.loc[mask, "Valor total"].sum())
                ating = real_m / meta_m * 100 if meta_m > 0 else 0.0
                rows.append({
                    "Mês": mes,
                    "_meta_val": meta_m,
                    "_real_val": real_m,
                    "_ating": ating,
                })

            df_proj = pd.DataFrame(rows)
            fig = _grafico_meta_real(df_proj, cp)
            st.plotly_chart(fig, use_container_width=True)

            # Tabela formatada
            df_show = df_proj[["Mês"]].copy()
            df_show["Meta"] = df_proj["_meta_val"].apply(lambda v: f"R$ {v:,.0f}")
            df_show["Realizado"] = df_proj["_real_val"].apply(lambda v: f"R$ {v:,.0f}")
            df_show["% Atingido"] = df_proj["_ating"].apply(lambda v: f"{v:.1f}%")
            st.dataframe(df_show, use_container_width=True, hide_index=True)

    # ── Tabela consolidada por distribuidor ────────────────────────────────────
    titulo_secao("🏢 Resumo por Distribuidor")
    rows_d = []
    for _, row in dist_valid.iterrows():
        nome = str(row["Distribuidor"]).strip()
        m_omp = float(row.get("Meta OMP (R$)", 0) or 0)
        m_mtc = float(row.get("Meta Metalco (R$)", 0) or 0)
        rows_d.append({
            "Distribuidor": nome,
            "Meta OMP":     f"R$ {m_omp:,.0f}",
            "Meta Metalco": f"R$ {m_mtc:,.0f}",
            "Meta Total":   f"R$ {m_omp + m_mtc:,.0f}",
        })
    if rows_d:
        st.dataframe(pd.DataFrame(rows_d), use_container_width=True, hide_index=True)
