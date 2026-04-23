"""
ui/charts.py — Biblioteca de gráficos Plotly para o Painel Executivo.
Usa as colunas do pipeline painel_executivo.
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

FONT  = "Inter, system-ui, -apple-system, sans-serif"
GRID  = "#EDE8E0"
WHITE = "rgba(0,0,0,0)"

ESTADO_COORDS = {
    "ACRE":(-9.97499,-67.8243),"ALAGOAS":(-9.6658,-35.7350),
    "AMAPA":(0.0349,-51.0694),"AMAZONAS":(-3.1190,-60.0217),
    "BAHIA":(-12.9714,-38.5014),"CEARA":(-3.7172,-38.5433),
    "DISTRITO FEDERAL":(-15.7942,-47.8822),"ESPIRITO SANTO":(-20.3155,-40.3128),
    "GOIAS":(-16.6864,-49.2643),"MARANHAO":(-2.5297,-44.3028),
    "MATO GROSSO":(-15.5961,-56.0967),"MATO GROSSO DO SUL":(-20.4697,-54.6201),
    "MINAS GERAIS":(-19.9167,-43.9345),"PARA":(-1.4558,-48.5044),
    "PARAIBA":(-7.1195,-34.8450),"PARANA":(-25.4195,-49.2646),
    "PERNAMBUCO":(-8.0578,-34.8829),"PIAUI":(-5.0920,-42.8034),
    "RIO DE JANEIRO":(-22.9068,-43.1729),"RIO GRANDE DO NORTE":(-5.7945,-35.2110),
    "RIO GRANDE DO SUL":(-30.0346,-51.2177),"RONDONIA":(-8.7612,-63.9004),
    "RORAIMA":(2.8235,-60.6758),"SANTA CATARINA":(-27.5954,-48.5480),
    "SAO PAULO":(-23.5505,-46.6333),"SERGIPE":(-10.9472,-37.0731),
    "TOCANTINS":(-10.2491,-48.3243),
}


def _preparar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "Data de emissão" in df.columns:
        dt = pd.to_datetime(df["Data de emissão"], errors="coerce")
        if "_mes_per" not in df.columns:
            df["_mes_per"] = dt.dt.to_period("M").astype(str)
        if "_mes" not in df.columns:
            df["_mes"] = dt.dt.month
        if "_semana" not in df.columns:
            df["_semana"] = dt.dt.isocalendar().week.astype("Int64")
        if "_dia_sem" not in df.columns:
            df["_dia_sem"] = dt.dt.day_name()
    return df


def _base(fig, h=380, title="", margins=None):
    m = margins or dict(l=12, r=12, t=44 if title else 16, b=12)
    fig.update_layout(
        height=h, margin=m,
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        font=dict(family=FONT, size=12, color="#7A736B"),
        hoverlabel=dict(bgcolor="#FDFCF9", bordercolor="#E6E1D8",
                        font_size=12, font_family=FONT),
        title=dict(text=title, font=dict(size=14, color="#1A1714", family=FONT),
                   x=0, xanchor="left", pad=dict(l=4)) if title else None,
    )
    fig.update_xaxes(gridcolor=GRID, linecolor="#E6E1D8", tickfont=dict(size=11), automargin=True)
    fig.update_yaxes(gridcolor=GRID, linecolor="#E6E1D8", tickfont=dict(size=11), automargin=True)
    return fig


def heatmap_familia_mes(df: pd.DataFrame, cp: str) -> go.Figure:
    df = _preparar(df)
    col_fam = "Família"
    if df.empty or "_mes_per" not in df.columns or col_fam not in df.columns:
        return go.Figure()
    d = df.groupby([col_fam, "_mes_per"])["Valor total"].sum().reset_index()
    top_fam = d.groupby(col_fam)["Valor total"].sum().nlargest(14).index
    d = d[d[col_fam].isin(top_fam)]
    pt = d.pivot_table(index=col_fam, columns="_mes_per",
                       values="Valor total", aggfunc="sum").fillna(0)
    pt = pt.loc[pt.sum(axis=1).sort_values(ascending=False).index]
    text_vals = [[f"R${v/1e3:.0f}K" if v >= 500 else "" for v in row] for row in pt.values]
    fig = go.Figure(go.Heatmap(
        z=pt.values, x=list(pt.columns), y=list(pt.index),
        colorscale=[[0,"#EFF6FF"],[0.3,"#93C5FD"],[0.7,cp],[1,"#1e3a5f"]],
        text=text_vals, texttemplate="%{text}", textfont=dict(size=9),
        hovertemplate="<b>%{y}</b><br>%{x}<br>R$ %{z:,.0f}<extra></extra>",
        showscale=True,
        colorbar=dict(title=dict(text="R$"), tickformat=",.0f", thickness=14, len=0.8),
        xgap=2, ygap=2,
    ))
    _base(fig, h=max(340, len(pt) * 30), title="🌡️ Famílias de Produtos Mais Vendidas × Mês",
          margins=dict(l=160, r=80, t=50, b=40))
    fig.update_xaxes(tickangle=-30)
    return fig


def heatmap_semana_dia(df: pd.DataFrame, cp: str) -> go.Figure:
    df = _preparar(df)
    if df.empty or "_semana" not in df.columns:
        return go.Figure()
    dias_pt = {"Monday": "Seg", "Tuesday": "Ter", "Wednesday": "Qua",
               "Thursday": "Qui", "Friday": "Sex", "Saturday": "Sáb", "Sunday": "Dom"}
    dias_ord = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    df2 = df.dropna(subset=["_semana", "_dia_sem"]).copy()
    df2["dia_pt"] = df2["_dia_sem"].map(dias_pt)
    pivot = df2.groupby(["_semana", "dia_pt"])["Valor total"].sum().reset_index()
    pt = pivot.pivot_table(index="dia_pt", columns="_semana",
                           values="Valor total", aggfunc="sum").fillna(0)
    pt = pt.reindex([d for d in dias_ord if d in pt.index])
    fig = go.Figure(go.Heatmap(
        z=pt.values, x=[f"S{c}" for c in pt.columns], y=pt.index,
        colorscale=[[0, "#F0F9FF"], [0.4, "#93C5FD"], [0.8, cp], [1, "#1e3a5f"]],
        hovertemplate="<b>%{y} — %{x}</b><br>R$ %{z:,.0f}<extra></extra>",
        showscale=True,
        colorbar=dict(title=dict(text="R$"), tickformat=",.0f", thickness=12, len=0.8),
        xgap=1, ygap=2,
    ))
    _base(fig, h=280, title="🗓️ Mapa de Calor — Vendas por Semana × Dia")
    fig.update_layout(xaxis_tickangle=-45)
    return fig


def fat_mensal(df: pd.DataFrame, cp: str) -> go.Figure:
    df = _preparar(df)
    if df.empty or "_mes_per" not in df.columns:
        return go.Figure()
    men = df.groupby("_mes_per")["Valor total"].sum().reset_index().sort_values("_mes_per")
    max_v = men["Valor total"].max() or 1
    men["cor"] = men["Valor total"].apply(
        lambda v: "#10B981" if v >= max_v * 0.8 else ("#F59E0B" if v >= max_v * 0.5 else cp))
    fig = go.Figure(go.Bar(
        x=men["_mes_per"], y=men["Valor total"],
        marker=dict(color=men["cor"].tolist(), line=dict(width=0)),
        text=[f"R${v/1e3:.0f}K" for v in men["Valor total"]], textposition="outside",
        hovertemplate="<b>%{x}</b><br>R$ %{y:,.0f}<extra></extra>",
    ))
    _base(fig, h=320, title="📊 Faturamento Mensal")
    fig.update_yaxes(tickprefix="R$ ", tickformat=",.0f")
    fig.update_xaxes(tickangle=-30)
    return fig


def top_clientes(df: pd.DataFrame, cp: str, n: int = 12) -> go.Figure:
    if df.empty or "Razão Social" not in df.columns:
        return go.Figure()
    d = df.groupby("Razão Social").agg(Fat=("Valor total", "sum")).reset_index()
    d = d.nlargest(n, "Fat").sort_values("Fat")
    fig = go.Figure(go.Bar(
        y=d["Razão Social"].str[:42], x=d["Fat"], orientation="h",
        marker=dict(color=d["Fat"],
                    colorscale=[[0, "#DBEAFE"], [1, cp]],
                    line=dict(width=0)),
        text=[f"R$ {v/1e3:.0f}K" for v in d["Fat"]], textposition="outside",
        hovertemplate="<b>%{y}</b><br>R$ %{x:,.0f}<extra></extra>",
    ))
    _base(fig, h=max(320, n * 34), title=f"🏆 Top {n} Clientes por Faturamento",
          margins=dict(l=10, r=100, t=44, b=12))
    fig.update_xaxes(tickprefix="R$ ", tickformat=",.0f", automargin=True)
    fig.update_yaxes(tickfont=dict(size=10), automargin=True)
    return fig


def treemap_grupos(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return go.Figure()
    fam_col  = "Família"
    desc_col = "Descrição"
    if fam_col not in df.columns:
        return go.Figure()
    if desc_col in df.columns:
        d = df.groupby([fam_col, desc_col])["Valor total"].sum().reset_index()
        d = d[d["Valor total"] > 0]
        fig = px.treemap(d, path=[fam_col, desc_col], values="Valor total",
                         color="Valor total",
                         color_continuous_scale=["#DBEAFE", "#1A56DB"])
    else:
        d = df.groupby(fam_col)["Valor total"].sum().reset_index()
        d = d[d["Valor total"] > 0]
        fig = px.treemap(d, path=[fam_col], values="Valor total",
                         color="Valor total",
                         color_continuous_scale=["#DBEAFE", "#1A56DB"])
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>R$ %{value:,.0f}<br>%{percentRoot:.1%} do total<extra></extra>",
        textfont=dict(size=12),
    )
    _base(fig, h=420, title="🌳 Treemap — Família de Itens × Descrição")
    fig.update_coloraxes(colorbar=dict(title="R$", tickformat=",.0f", thickness=12))
    return fig


def scatter_fat_margem(df: pd.DataFrame, cp: str) -> go.Figure:
    if df.empty or "Razão Social" not in df.columns:
        return go.Figure()
    try:
        from modulos.fat.config import COL_MARGEM
        margem_col = COL_MARGEM
    except ImportError:
        margem_col = "Margem"
    if margem_col not in df.columns:
        return go.Figure()
    qtde_col = "Qtde. faturada" if "Qtde. faturada" in df.columns else "Valor total"
    d = df.groupby("Razão Social").agg(
        Fat=("Valor total", "sum"),
        Margem=(margem_col, "sum"),
        Qtde=(qtde_col, "sum"),
    ).reset_index()
    d = d[d["Fat"] > 0].copy()
    d["M%"] = d["Margem"] / d["Fat"] * 100
    fig = go.Figure(go.Scatter(
        x=d["Fat"], y=d["M%"], mode="markers",
        text=d["Razão Social"].str[:32],
        marker=dict(
            size=np.sqrt(d["Qtde"].clip(1)) * 2 + 6,
            color=d["M%"],
            colorscale=[[0, "#EF4444"], [0.4, "#F59E0B"], [1, "#10B981"]],
            showscale=True, opacity=0.80,
            colorbar=dict(title="Margem%", ticksuffix="%", thickness=12),
            line=dict(color="white", width=1),
        ),
        hovertemplate="<b>%{text}</b><br>Fat: R$ %{x:,.0f}<br>Margem: %{y:.1f}%<extra></extra>",
    ))
    fig.add_hline(y=0, line_color="#EF4444", line_dash="dash", line_width=1.5)
    _base(fig, h=420, title="⚡ Faturamento × Margem por Cliente")
    fig.update_xaxes(tickprefix="R$ ", tickformat=",.0f", title="Faturamento (R$)")
    fig.update_yaxes(ticksuffix="%", title="Margem (%)")
    return fig


def mapa_brasil(df: pd.DataFrame, cp: str) -> go.Figure:
    if df.empty or "Estado" not in df.columns:
        return go.Figure()
    try:
        from modulos.fat.config import COL_MARGEM
        margem_col = COL_MARGEM
    except ImportError:
        margem_col = "Margem"
    agg: dict = {"Fat": ("Valor total", "sum"), "Notas": ("Nota", "nunique")}
    if margem_col in df.columns:
        agg["Margem"] = (margem_col, "sum")
    if "Cliente" in df.columns:
        agg["Clientes"] = ("Cliente", "nunique")
    d = df.groupby("Estado").agg(**agg).reset_index()
    d["_up"] = d["Estado"].str.upper().str.strip()
    d["lat"] = d["_up"].map(lambda x: ESTADO_COORDS.get(x, (None, None))[0])
    d["lon"] = d["_up"].map(lambda x: ESTADO_COORDS.get(x, (None, None))[1])
    d = d.dropna(subset=["lat", "lon"])
    if d.empty:
        return go.Figure()
    d["M%"] = (d["Margem"] / d["Fat"] * 100).round(1) if "Margem" in d.columns else 0.0
    d["tamanho"] = np.sqrt(d["Fat"].clip(1) / d["Fat"].max()) * 55 + 8
    clientes_vals = d["Clientes"].tolist() if "Clientes" in d.columns else [0] * len(d)
    fig = go.Figure(go.Scattergeo(
        lat=d["lat"], lon=d["lon"],
        text=d["Estado"],
        customdata=np.stack([d["Fat"], d["M%"], d["Notas"], clientes_vals], axis=-1),
        marker=dict(
            size=d["tamanho"],
            color=d["M%"],
            colorscale=[[0, "#FEE2E2"], [0.3, "#FEF3C7"], [0.6, "#D1FAE5"], [1, "#065F46"]],
            cmin=float(d["M%"].min()), cmax=float(d["M%"].max()),
            showscale=True,
            colorbar=dict(title=dict(text="Margem%"), ticksuffix="%",
                          thickness=14, len=0.7, x=1.01),
            opacity=0.85, line=dict(color="white", width=1.5),
        ),
        hovertemplate=(
            "<b>%{text}</b><br>"
            "💰 Fat: R$ %{customdata[0]:,.0f}<br>"
            "📊 Margem: %{customdata[1]:.1f}%<br>"
            "🧾 Notas: %{customdata[2]:,}<br>"
            "👥 Clientes: %{customdata[3]:,}"
            "<extra></extra>"
        ),
        name="Estados",
    ))
    fig.update_geos(
        scope="south america",
        showland=True, landcolor="#F8FAFC",
        showocean=True, oceancolor="#DBEAFE",
        showlakes=True, lakecolor="#BFDBFE",
        showrivers=True, rivercolor="#93C5FD",
        showcountries=True, countrycolor="#CBD5E1", countrywidth=0.8,
        showsubunits=True, subunitcolor="#E2E8F0", subunitwidth=0.5,
        showcoastlines=True, coastlinecolor="#94A3B8",
        bgcolor=WHITE,
        center=dict(lat=-14.2, lon=-51.9),
        projection_scale=3.8, resolution=50,
    )
    fig.update_layout(
        height=540,
        margin=dict(l=0, r=90, t=56, b=0),
        paper_bgcolor=WHITE,
        font=dict(family=FONT, size=12, color="#374151"),
        title=dict(
            text=(
                "🌎 Distribuição Geográfica — Faturamento por Estado<br>"
                "<sup>Tamanho = volume de vendas · Cor = Margem % · "
                "Use scroll/pinch para zoom</sup>"
            ),
            font=dict(size=14, color="#111827", family=FONT),
            x=0, xanchor="left",
        ),
        hoverlabel=dict(bgcolor="white", bordercolor="#E2E8F0",
                        font_size=12, font_family=FONT),
        dragmode="zoom",
    )
    return fig


def heatmap_estado_mes(df: pd.DataFrame, cp: str) -> go.Figure:
    df = _preparar(df)
    if df.empty or "_mes_per" not in df.columns or "Estado" not in df.columns:
        return go.Figure()
    d = df.groupby(["Estado", "_mes_per"])["Valor total"].sum().reset_index()
    pt = d.pivot_table(index="Estado", columns="_mes_per",
                       values="Valor total", aggfunc="sum").fillna(0)
    pt = pt.loc[pt.sum(axis=1).sort_values(ascending=False).head(20).index]
    text_vals = [
        [f"R${v/1e3:.0f}K" if v >= 1000 else "" for v in row]
        for row in pt.values
    ]
    fig = go.Figure(go.Heatmap(
        z=pt.values, x=list(pt.columns), y=list(pt.index),
        colorscale=[[0, "#F0F9FF"], [0.2, "#BAE6FD"], [0.5, "#38BDF8"],
                    [0.8, cp], [1, "#1e3a5f"]],
        text=text_vals, texttemplate="%{text}", textfont=dict(size=9, color="#1E293B"),
        hovertemplate="<b>%{y}</b><br>%{x}<br>R$ %{z:,.0f}<extra></extra>",
        showscale=True,
        colorbar=dict(title=dict(text="R$"), tickformat=",.0f", thickness=14, len=0.8),
        xgap=1, ygap=1,
    ))
    _base(fig, h=max(380, len(pt) * 28),
          title="🗺️ Mapa de Calor — Vendas por Estado × Mês",
          margins=dict(l=170, r=80, t=50, b=40))
    fig.update_xaxes(tickangle=-30, side="bottom")
    fig.update_yaxes(tickfont=dict(size=10))
    return fig


def heatmap_estado_produto(df: pd.DataFrame, cp: str) -> go.Figure:
    if df.empty or "Estado" not in df.columns or "Grupo de itens" not in df.columns:
        return go.Figure()
    d = df.groupby(["Estado", "Grupo de itens"])["Valor total"].sum().reset_index()
    top_estados = d.groupby("Estado")["Valor total"].sum().nlargest(15).index
    top_grupos  = d.groupby("Grupo de itens")["Valor total"].sum().nlargest(8).index
    d = d[d["Estado"].isin(top_estados) & d["Grupo de itens"].isin(top_grupos)]
    pt = d.pivot_table(index="Estado", columns="Grupo de itens",
                       values="Valor total", aggfunc="sum").fillna(0)
    pt = pt.loc[pt.sum(axis=1).sort_values(ascending=True).index]
    text_vals = [
        [f"R${v/1e3:.0f}K" if v >= 1000 else "" for v in row]
        for row in pt.values
    ]
    fig = go.Figure(go.Heatmap(
        z=pt.values, x=list(pt.columns), y=list(pt.index),
        colorscale=[[0, "#ECFDF5"], [0.3, "#6EE7B7"], [0.7, "#059669"], [1, "#064E3B"]],
        text=text_vals, texttemplate="%{text}", textfont=dict(size=9),
        hovertemplate="<b>%{y}</b><br>%{x}<br>R$ %{z:,.0f}<extra></extra>",
        showscale=True,
        colorbar=dict(title=dict(text="R$"), tickformat=",.0f", thickness=14, len=0.8),
        xgap=2, ygap=1,
    ))
    _base(fig, h=max(380, len(pt) * 30),
          title="📦 Mapa de Calor — Produtos por Estado",
          margins=dict(l=170, r=80, t=50, b=80))
    fig.update_xaxes(tickangle=-30, tickfont=dict(size=10))
    fig.update_yaxes(tickfont=dict(size=10))
    return fig


def heatmap_margem_grupo(df: pd.DataFrame) -> go.Figure:
    df = _preparar(df)
    if df.empty or "_mes_per" not in df.columns or "Grupo de itens" not in df.columns:
        return go.Figure()
    try:
        from modulos.fat.config import COL_MARGEM
        margem_col = COL_MARGEM
    except ImportError:
        margem_col = "Margem"
    if margem_col not in df.columns:
        return go.Figure()
    d = df.groupby(["_mes_per", "Grupo de itens"]).agg(
        Fat=("Valor total", "sum"), Mgm=(margem_col, "sum")).reset_index()
    d["M%"] = (d["Mgm"] / d["Fat"] * 100).fillna(0).round(1)
    pt = d.pivot_table(index="Grupo de itens", columns="_mes_per",
                       values="M%").fillna(0)
    fig = go.Figure(go.Heatmap(
        z=pt.values, x=list(pt.columns), y=list(pt.index),
        colorscale=[[0, "#FEE2E2"], [0.5, "#FEF9C3"], [1, "#DCFCE7"]],
        text=[[f"{v:.1f}%" for v in row] for row in pt.values],
        texttemplate="%{text}", textfont=dict(size=11),
        hovertemplate="<b>%{y} · %{x}</b><br>Margem: %{z:.1f}%<extra></extra>",
        showscale=True,
        colorbar=dict(title="%", thickness=12, len=0.8),
    ))
    _base(fig, h=max(300, len(pt) * 34),
          title="🌡️ Mapa de Calor — Margem% por Grupo × Mês",
          margins=dict(l=170, r=60, t=50, b=40))
    return fig
