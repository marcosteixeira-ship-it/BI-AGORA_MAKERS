"""
ui/abas/aba_exportar.py
Exportação dos DataFrames processados pelo pipeline em CSV.
"""
import io
import zipfile
from datetime import datetime

import pandas as pd
import streamlit as st


# ── Helpers ───────────────────────────────────────────────────────────────────

def _formatar_ptbr(df: pd.DataFrame) -> pd.DataFrame:
    """Converte colunas numéricas para formato PT-BR: separador decimal ',' e milhar '.'."""
    df = df.copy()
    for col in df.select_dtypes(include="number").columns:
        col_sem_nulo = df[col].dropna()
        inteiro = col_sem_nulo.empty or (col_sem_nulo % 1 == 0).all()
        if inteiro:
            df[col] = df[col].apply(
                lambda v: "" if pd.isna(v) else f"{int(v):,}".replace(",", ".")
            )
        else:
            df[col] = df[col].apply(
                lambda v: "" if pd.isna(v)
                else f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
    return df


def _csv_bytes(df: pd.DataFrame) -> bytes:
    """CSV com separador ; e BOM UTF-8, números em formato PT-BR (1.000,50)."""
    return _formatar_ptbr(df).to_csv(index=False, sep=";").encode("utf-8-sig")


def _resumo(df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return "Sem dados"
    return f"{len(df):,} linhas · {len(df.columns)} colunas"


def _card_download(col, titulo: str, df: pd.DataFrame, filename: str, key: str) -> None:
    """Renderiza um card com informações + botão de download."""
    disponivel = df is not None and not df.empty
    icone = "✅" if disponivel else "❌"
    with col:
        st.markdown(
            f"<div style='background:{'#F0FDF4' if disponivel else '#FFF5F5'};"
            f"border:1px solid {'#86EFAC' if disponivel else '#FCA5A5'};"
            f"border-radius:10px;padding:12px 14px;margin-bottom:4px;'>"
            f"<div style='font-weight:700;font-size:.88rem;color:#0F172A;'>{icone} {titulo}</div>"
            f"<div style='font-size:.72rem;color:#64748B;margin-top:2px;'>{_resumo(df)}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        if disponivel:
            st.download_button(
                label="⬇️ Baixar CSV",
                data=_csv_bytes(df),
                file_name=filename,
                mime="text/csv",
                use_container_width=True,
                key=key,
            )
        else:
            st.button(
                "Sem dados",
                disabled=True,
                use_container_width=True,
                key=f"dis_{key}",
            )


# ── Render principal ──────────────────────────────────────────────────────────

def renderizar(
    d_fat: dict | None,
    d_esc: dict | None,
    d_ped: dict | None,
) -> None:
    _vz = pd.DataFrame()

    st.markdown(
        "<div style='font-size:1.05rem;font-weight:700;color:#0F172A;"
        "margin-bottom:4px;'>📥 Exportar Dados Tratados</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Todos os arquivos abaixo já passaram pelo pipeline completo: "
        "leitura → normalização → fórmulas (RB, RL, CPV, Margem…). "
        "Separador `;` · Números em formato PT-BR (1.000,50) · Encoding UTF-8 com BOM · compatível com Excel e Power BI."
    )

    # ── Seção FAT ─────────────────────────────────────────────────────────────
    st.markdown("##### 🧾 Faturamento")
    c1, c2, c3 = st.columns(3, gap="small")
    _card_download(c1, "FAT My City",
                   d_fat.get("omp", _vz) if d_fat else _vz,
                   "fat_mycity_tratado.csv", "dl_fat_omp")
    _card_download(c2, "FAT Metalco",
                   d_fat.get("mtc", _vz) if d_fat else _vz,
                   "fat_metalco_tratado.csv", "dl_fat_mtc")
    _card_download(c3, "FAT Consolidado",
                   d_fat.get("consolidado", _vz) if d_fat else _vz,
                   "fat_consolidado_tratado.csv", "dl_fat_cons")

    # ── Seção ESC ─────────────────────────────────────────────────────────────
    st.markdown("##### ↩️ Escrita Fiscal / Devoluções")
    c4, c5, _ = st.columns(3, gap="small")
    _card_download(c4, "ESC My City",
                   d_esc.get("omp", _vz) if d_esc else _vz,
                   "esc_mycity_tratada.csv", "dl_esc_omp")
    _card_download(c5, "ESC Metalco",
                   d_esc.get("mtc", _vz) if d_esc else _vz,
                   "esc_metalco_tratada.csv", "dl_esc_mtc")

    # ── Seção PED ─────────────────────────────────────────────────────────────
    st.markdown("##### 📋 Pedidos")
    c6, c7, _ = st.columns(3, gap="small")
    _card_download(c6, "PED My City",
                   d_ped.get("omp", _vz) if d_ped else _vz,
                   "ped_mycity_tratado.csv", "dl_ped_omp")
    _card_download(c7, "PED Metalco",
                   d_ped.get("mtc", _vz) if d_ped else _vz,
                   "ped_metalco_tratado.csv", "dl_ped_mtc")

    # ── Exportar tudo em ZIP ──────────────────────────────────────────────────
    st.divider()
    st.markdown("##### 📦 Exportar tudo em ZIP")
    st.caption("Um único arquivo `.zip` com todos os CSVs disponíveis.")

    lotes = {
        "fat_mycity_tratado.csv":      d_fat.get("omp", _vz) if d_fat else _vz,
        "fat_metalco_tratado.csv":     d_fat.get("mtc", _vz) if d_fat else _vz,
        "fat_consolidado_tratado.csv": d_fat.get("consolidado", _vz) if d_fat else _vz,
        "esc_mycity_tratada.csv":      d_esc.get("omp", _vz) if d_esc else _vz,
        "esc_metalco_tratada.csv":     d_esc.get("mtc", _vz) if d_esc else _vz,
        "ped_mycity_tratado.csv":      d_ped.get("omp", _vz) if d_ped else _vz,
        "ped_metalco_tratado.csv":     d_ped.get("mtc", _vz) if d_ped else _vz,
    }

    arquivos_disponiveis = [(fn, df) for fn, df in lotes.items() if not df.empty]

    if arquivos_disponiveis:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for fn, df in arquivos_disponiveis:
                zf.writestr(fn, _csv_bytes(df))
        buf.seek(0)
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        st.download_button(
            label=f"📦 Baixar ZIP ({len(arquivos_disponiveis)} arquivo(s))",
            data=buf.getvalue(),
            file_name=f"bi_dados_tratados_{ts}.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True,
            key="dl_zip_tudo",
        )
    else:
        st.warning("Nenhum dado disponível para exportar. Verifique os CSVs na pasta `data/`.")
