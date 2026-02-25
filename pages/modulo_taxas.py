"""
💹 Módulo Taxas de Juros — Operações de Crédito
=================================================
Taxas de juros praticadas por IFs em modalidades de crédito.
Endpoints: TaxasJurosMensalPorMes e TaxasJurosDiariaPorInicioPeriodo.

Sub-módulos:
1. Ranking: Top/Bottom 10 por modalidade (dado mais recente)
2. Banco Individual: todas as modalidades + posição
3. Gráficos: scatter de cada banco ao longo do tempo (últimos 10 anos)
4. Download: dados brutos por modalidade e período
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date, timedelta
from utils.i18n import t
from utils.helpers import to_excel_bytes, to_csv_bytes


# =============================================================================
# Modalities config
# =============================================================================

# Monthly endpoint modalities
MONTHLY_MODALITIES = [
    "Financiamento imobiliário com taxas de mercado - Prefixado",
    "Financiamento imobiliário com taxas de mercado - Pós-fixado referenciado em IPCA",
]

# Daily endpoint modalities
DAILY_MODALITIES = [
    "Aquisição de veículos - Prefixado",
    "Capital de giro com prazo até 365 dias - Prefixado",
    "Capital de giro com prazo até 365 dias - Pós-fixado referenciado em juros flutuantes",
    "Capital de giro com prazo superior a 365 dias - Prefixado",
    "Capital de giro com prazo superior a 365 dias - Pós-fixado referenciado em juros flutuantes",
    "Cartão de crédito - rotativo total - Prefixado",
    "Cheque especial - Prefixado",
    "Conta garantida - Prefixado",
    "Conta garantida - Pós-fixado referenciado em juros flutuantes",
    "Crédito pessoal consignado privado - Prefixado",
    "Crédito pessoal não consignado - Prefixado",
    "Desconto de duplicatas - Prefixado",
]

ALL_MODALITIES = DAILY_MODALITIES + MONTHLY_MODALITIES

# Modalities excluded from ranking tab only
RANKING_EXCLUDED = {
    "Financiamento imobiliário com taxas de mercado - Prefixado",
    "Financiamento imobiliário com taxas de mercado - Pós-fixado referenciado em IPCA",
    "Capital de giro com prazo até 365 dias - Prefixado",
    "Capital de giro com prazo até 365 dias - Pós-fixado referenciado em juros flutuantes",
    "Capital de giro com prazo superior a 365 dias - Pós-fixado referenciado em juros flutuantes",
    "Conta garantida - Pós-fixado referenciado em juros flutuantes",
}

RANKING_MODALITIES = [m for m in ALL_MODALITIES if m not in RANKING_EXCLUDED]

# Short labels for display
def short_label(mod: str) -> str:
    """Create a shorter label for display."""
    return mod.replace("Pós-fixado referenciado em ", "Pós-").replace(" - Prefixado", " - Pré")


# =============================================================================
# Data fetching
# =============================================================================

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_daily_modality(modality: str, limit: int = 200000) -> pd.DataFrame:
    """Fetch data from TaxasJurosDiariaPorInicioPeriodo for a modality."""
    from bcb import TaxaJuros
    em = TaxaJuros()
    ep = em.get_endpoint("TaxasJurosDiariaPorInicioPeriodo")
    df = (
        ep.query()
        .filter(ep.Modalidade == modality)
        .orderby(ep.InicioPeriodo.desc())
        .limit(limit)
        .collect()
    )
    if not df.empty and "InicioPeriodo" in df.columns:
        df["InicioPeriodo"] = pd.to_datetime(df["InicioPeriodo"], errors="coerce")
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_monthly_modality(modality: str, limit: int = 200000) -> pd.DataFrame:
    """Fetch data from TaxasJurosMensalPorMes for a modality."""
    from bcb import TaxaJuros
    em = TaxaJuros()
    ep = em.get_endpoint("TaxasJurosMensalPorMes")
    df = (
        ep.query()
        .filter(ep.Modalidade == modality)
        .orderby(ep.Mes.desc())
        .limit(limit)
        .collect()
    )
    if not df.empty and "Mes" in df.columns:
        df["Mes"] = pd.to_datetime(df["Mes"], errors="coerce")
    return df


def get_latest_data(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """Filter to most recent date only."""
    if df.empty:
        return df
    max_date = df[date_col].max()
    return df[df[date_col] == max_date].copy()


def is_daily(modality: str) -> bool:
    """Check if modality uses daily endpoint."""
    return modality in DAILY_MODALITIES


def get_date_col(modality: str) -> str:
    """Get the date column name for a modality."""
    return "InicioPeriodo" if is_daily(modality) else "Mes"


def get_bank_col(modality: str) -> str:
    """Get the institution name column."""
    return "InstituicaoFinanceira"


# =============================================================================
# Plotly chart
# =============================================================================

PLOTLY_LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#94A3B8"),
    margin=dict(l=20, r=20, t=50, b=20),
    hoverlabel=dict(
        bgcolor="#1A2332",
        bordercolor="rgba(148,163,184,0.2)",
        font=dict(color="#F1F5F9"),
    ),
)

GRID_STYLE = dict(gridcolor="rgba(148,163,184,0.07)", showline=False)


def make_median_chart(df: pd.DataFrame, date_col: str, mod_name: str, lang: str) -> go.Figure:
    """
    Scatter plot of median rate over time (grouped by date).
    Like the reference chart: Mediana das Taxas de Juros.
    """
    cutoff = pd.Timestamp.now() - pd.DateOffset(years=10)
    df_plot = df[df[date_col] >= cutoff].copy()

    if df_plot.empty:
        df_plot = df.copy()

    # Group by date, compute median
    df_median = df_plot.groupby(date_col)["TaxaJurosAoAno"].median().reset_index()
    df_median = df_median.sort_values(date_col)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_median[date_col],
            y=df_median["TaxaJurosAoAno"],
            mode="markers",
            marker=dict(
                color="#22D3EE",
                size=3,
                opacity=0.6,
            ),
            hovertemplate=(
                "%{x|%d/%m/%Y}<br>"
                "Mediana: %{y:,.2f}% a.a.<extra></extra>"
            ),
            showlegend=False,
        )
    )

    fig.update_layout(
        **PLOTLY_LAYOUT_BASE,
        title=dict(
            text=f"Mediana das Taxas de Juros: {mod_name} — Fonte: BCB",
            font=dict(size=13),
        ),
        height=400,
        xaxis={**GRID_STYLE, "title": t("tax_chart_xaxis", lang)},
        yaxis={**GRID_STYLE, "title": t("tax_chart_yaxis", lang)},
    )

    return fig


# =============================================================================
# Styled HTML table
# =============================================================================

TABLE_CSS = """
<style>
    .tax-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        font-family: 'DM Sans', sans-serif;
    }
    .tax-table th {
        text-align: left;
        padding: 8px 10px;
        font-family: 'Space Mono', monospace;
        font-size: 11px;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        border-bottom: 2px solid rgba(148,163,184,0.15);
        background: rgba(255,255,255,0.02);
    }
    .tax-table td {
        padding: 7px 10px;
        color: #94A3B8;
        border-bottom: 1px solid rgba(148,163,184,0.06);
    }
    .tax-table tbody tr:hover {
        background: rgba(34,211,238,0.04);
    }
</style>
"""


def render_ranking_table(df: pd.DataFrame, lang: str) -> str:
    """Render styled HTML ranking table."""
    header = f"""
    <tr>
        <th style="width:40px;">#</th>
        <th>{t("tax_institution", lang)}</th>
        <th style="text-align:right;">{t("tax_rate", lang)}</th>
    </tr>"""

    rows = ""
    for i, (_, row) in enumerate(df.iterrows()):
        rank = i + 1
        name = row.get("InstituicaoFinanceira", "—")
        rate = row.get("TaxaJurosAoAno", float("nan"))
        rate_str = f"{rate:,.2f}" if pd.notna(rate) else "—"
        rows += f"""
        <tr>
            <td style="color:#22D3EE; font-weight:700; font-family:Space Mono,monospace;">{rank}</td>
            <td>{name}</td>
            <td style="text-align:right; font-family:Space Mono,monospace;">{rate_str}</td>
        </tr>"""

    return f"""
    <table class="tax-table">
        <thead>{header}</thead>
        <tbody>{rows}</tbody>
    </table>"""


# =============================================================================
# Main render
# =============================================================================

def render(lang: str):
    """Renders the Interest Rates module page."""

    if st.button(t("back_to_hub", lang), key="back_tax"):
        st.session_state.current_page = "hub"
        for k in list(st.session_state.keys()):
            if k.startswith("tax_"):
                del st.session_state[k]
        st.rerun()

    st.markdown(
        f"""
        <div style="margin-bottom: 24px;">
            <h1 style="font-size:28px; font-weight:700; letter-spacing:-0.02em;">
                {t("tax_page_title", lang)}
            </h1>
            <p style="color:#94A3B8; font-size:14px; margin-top:4px;">
                {t("tax_page_desc", lang)}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(TABLE_CSS, unsafe_allow_html=True)

    tab_ranking, tab_bank, tab_charts, tab_download = st.tabs([
        t("tax_tab_ranking", lang),
        t("tax_tab_bank", lang),
        t("tax_tab_charts", lang),
        t("tax_tab_download", lang),
    ])

    with tab_ranking:
        _render_ranking(lang)

    with tab_bank:
        _render_bank(lang)

    with tab_charts:
        _render_charts(lang)

    with tab_download:
        _render_download(lang)

    st.markdown(
        f"""
        <div class="footer">
            {t("source", lang)}:
            <a href="https://dadosabertos.bcb.gov.br/" target="_blank">dadosabertos.bcb.gov.br</a>
            · TaxaJuros API · {t("built_with", lang)}
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# Shared data loader
# =============================================================================

def _load_all_latest(selected_mods: list, progress_holder=None) -> dict:
    """
    Fetch latest data for each selected modality.
    Returns dict: {modality: df_latest}
    """
    results = {}
    total = len(selected_mods)

    for i, mod in enumerate(selected_mods):
        try:
            if is_daily(mod):
                df = fetch_daily_modality(mod, limit=5000)
                date_col = "InicioPeriodo"
            else:
                df = fetch_monthly_modality(mod, limit=5000)
                date_col = "Mes"

            if not df.empty:
                df_latest = get_latest_data(df, date_col)
                if not df_latest.empty:
                    results[mod] = df_latest
        except Exception:
            pass

        if progress_holder:
            progress_holder.progress((i + 1) / total)

    return results


# =============================================================================
# Tab: Ranking
# =============================================================================

def _render_ranking(lang: str):
    selected = st.multiselect(
        t("tax_select_modalities", lang),
        options=RANKING_MODALITIES,
        default=RANKING_MODALITIES,
        key="tax_rank_mods",
    )

    if not selected:
        return

    query_btn = st.button(t("tax_query", lang), key="query_tax_rank", type="primary")

    if not query_btn and "tax_ranking_data" not in st.session_state:
        return

    if query_btn:
        progress = st.progress(0, text=t("loading", lang))
        data = _load_all_latest(selected, progress)
        progress.empty()
        st.session_state.tax_ranking_data = data

    if "tax_ranking_data" not in st.session_state:
        return

    data = st.session_state.tax_ranking_data

    if not data:
        st.warning(t("no_data", lang))
        return

    # Show reference date from first modality
    first_df = next(iter(data.values()))
    date_col = "InicioPeriodo" if "InicioPeriodo" in first_df.columns else "Mes"
    if date_col in first_df.columns:
        ref_date = first_df[date_col].max()
        if pd.notna(ref_date):
            st.markdown(
                f"<div style='font-family:Space Mono,monospace; font-size:12px; color:#64748B; "
                f"margin-bottom:16px;'>"
                f"📅 {t('tax_ref_date', lang)}: <strong style='color:#22D3EE;'>"
                f"{ref_date.strftime('%d/%m/%Y') if hasattr(ref_date, 'strftime') else ref_date}"
                f"</strong></div>",
                unsafe_allow_html=True,
            )

    for mod in selected:
        if mod not in data:
            continue

        df_latest = data[mod]
        # Excluir IFs com taxa zero
        df_latest = df_latest[df_latest["TaxaJurosAoAno"] > 0]
        df_sorted_desc = df_latest.sort_values("TaxaJurosAoAno", ascending=False).head(10)
        df_sorted_asc = df_latest.sort_values("TaxaJurosAoAno", ascending=True).head(10)

        total_banks = len(df_latest)

        st.markdown(
            f"<div style='font-size:15px; font-weight:600; margin:24px 0 8px;'>"
            f"{mod} "
            f"<span style='font-size:11px; color:#64748B;'>({total_banks} {t('tax_total_banks', lang)})</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

        col_left, col_right = st.columns(2, gap="medium")

        with col_left:
            st.markdown(
                f"<div style='font-size:13px; font-weight:600; color:#FB7185; margin-bottom:6px;'>"
                f"▲ {t('tax_largest', lang)}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                render_ranking_table(df_sorted_desc.reset_index(drop=True), lang),
                unsafe_allow_html=True,
            )

        with col_right:
            st.markdown(
                f"<div style='font-size:13px; font-weight:600; color:#34D399; margin-bottom:6px;'>"
                f"▼ {t('tax_smallest', lang)}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                render_ranking_table(df_sorted_asc.reset_index(drop=True), lang),
                unsafe_allow_html=True,
            )

        st.markdown("<hr style='border-color:rgba(148,163,184,0.06);margin:8px 0;'>", unsafe_allow_html=True)


# =============================================================================
# Tab: Banco Individual
# =============================================================================

def _render_bank(lang: str):
    query_btn = st.button(t("tax_query", lang), key="query_tax_bank", type="primary")

    if query_btn:
        progress = st.progress(0, text=t("loading", lang))
        data = _load_all_latest(ALL_MODALITIES, progress)
        progress.empty()
        st.session_state.tax_bank_data = data

    if "tax_bank_data" not in st.session_state:
        if "tax_ranking_data" in st.session_state:
            st.session_state.tax_bank_data = st.session_state.tax_ranking_data
        else:
            st.info(f"👆 {t('tax_query', lang)}")
            return

    data = st.session_state.tax_bank_data

    # Collect all bank names
    all_banks = set()
    for df in data.values():
        if "InstituicaoFinanceira" in df.columns:
            all_banks.update(df["InstituicaoFinanceira"].dropna().unique())

    bank_list = sorted(all_banks)

    selected_bank = st.selectbox(
        t("tax_select_bank", lang),
        options=bank_list,
        key="tax_bank_select",
    )

    if not selected_bank:
        return

    st.markdown(
        f"<div style='font-size:20px; font-weight:700; margin:16px 0 8px;'>"
        f"🏦 {selected_bank}</div>",
        unsafe_allow_html=True,
    )

    # Build overview table
    header = f"""
    <tr>
        <th>{t("tax_modality", lang)}</th>
        <th style="text-align:right;">{t("tax_rate", lang)}</th>
        <th style="text-align:center;">{t("tax_position", lang)}</th>
    </tr>"""

    rows_html = ""
    for mod in ALL_MODALITIES:
        if mod not in data:
            continue

        df_mod = data[mod]
        bank_row = df_mod[df_mod["InstituicaoFinanceira"] == selected_bank]

        if bank_row.empty:
            continue

        rate = bank_row["TaxaJurosAoAno"].iloc[0]
        rate_str = f"{rate:,.2f}" if pd.notna(rate) else "—"

        # Ranking position (ascending = lower rate is better position)
        if pd.notna(rate):
            n = len(df_mod)
            rank = int((df_mod["TaxaJurosAoAno"] < rate).sum() + 1)
            pos_str = f"{rank}º {t('tax_of_banks', lang, n=n)}"
        else:
            pos_str = "—"

        rows_html += f"""
        <tr>
            <td style="font-weight:500; color:#F1F5F9; font-size:12px;">{mod}</td>
            <td style="text-align:right; font-family:Space Mono,monospace;">{rate_str}</td>
            <td style="text-align:center; font-family:Space Mono,monospace; color:#22D3EE;">{pos_str}</td>
        </tr>"""

    if rows_html:
        st.markdown(
            f'<table class="tax-table"><thead>{header}</thead><tbody>{rows_html}</tbody></table>',
            unsafe_allow_html=True,
        )
    else:
        st.info(f"{selected_bank}: dados indisponíveis para as modalidades selecionadas.")


# =============================================================================
# Tab: Gráficos
# =============================================================================

def _render_charts(lang: str):
    selected_mod = st.selectbox(
        t("tax_select_chart_mod", lang),
        options=ALL_MODALITIES,
        key="tax_chart_mod",
    )

    if not selected_mod:
        return

    query_btn = st.button(t("tax_query", lang), key="query_tax_chart", type="primary")

    if query_btn:
        with st.spinner(t("loading", lang)):
            try:
                if is_daily(selected_mod):
                    df = fetch_daily_modality(selected_mod, limit=200000)
                else:
                    df = fetch_monthly_modality(selected_mod, limit=200000)
                st.session_state.tax_chart_data = (selected_mod, df)
            except Exception as e:
                st.error(t("api_error", lang))
                st.code(str(e))
                return

    if "tax_chart_data" not in st.session_state:
        return

    mod_name, df = st.session_state.tax_chart_data
    date_col = get_date_col(mod_name)

    if df.empty:
        st.warning(t("no_data", lang))
        return

    fig = make_median_chart(df, date_col, mod_name, lang)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.caption(f"📊 {len(df):,} observações")


# =============================================================================
# Tab: Download
# =============================================================================

def _render_download(lang: str):
    st.markdown(
        f'<div class="section-title">{t("tax_download_title", lang)}</div>',
        unsafe_allow_html=True,
    )
    st.caption(t("tax_download_desc", lang))

    selected_mods = st.multiselect(
        t("tax_select_modalities", lang),
        options=ALL_MODALITIES,
        default=ALL_MODALITIES[:3],
        key="tax_dl_mods",
    )

    col_start, col_end = st.columns(2)
    with col_start:
        dl_start = st.date_input(
            t("start_date", lang),
            value=date(2020, 1, 1),
            min_value=date(2000, 1, 1),
            max_value=date.today(),
            format="DD/MM/YYYY",
            key="tax_dl_start",
        )
    with col_end:
        dl_end = st.date_input(
            t("end_date", lang),
            value=date.today(),
            min_value=dl_start,
            max_value=date.today(),
            format="DD/MM/YYYY",
            key="tax_dl_end",
        )

    if not selected_mods:
        return

    dl_btn = st.button(t("tax_download_btn", lang), key="tax_dl_btn", type="primary")

    if not dl_btn:
        return

    progress = st.progress(0, text=t("tax_downloading", lang))
    all_frames = []
    total = len(selected_mods)

    for i, mod in enumerate(selected_mods):
        try:
            if is_daily(mod):
                df = fetch_daily_modality(mod, limit=100000)
                date_col = "InicioPeriodo"
            else:
                df = fetch_monthly_modality(mod, limit=100000)
                date_col = "Mes"

            if not df.empty:
                # Filter date range
                mask = (df[date_col] >= pd.Timestamp(dl_start)) & (df[date_col] <= pd.Timestamp(dl_end))
                df_filtered = df[mask].copy()
                if not df_filtered.empty:
                    all_frames.append(df_filtered)
        except Exception:
            pass

        progress.progress((i + 1) / total, text=f"{t('tax_downloading', lang)} {mod[:40]}...")

    progress.empty()

    if not all_frames:
        st.warning(t("no_data", lang))
        return

    df_all = pd.concat(all_frames, ignore_index=True)

    st.success(f"✅ {len(df_all):,} registros")

    dl1, dl2, _ = st.columns([1, 1, 4])
    with dl1:
        st.download_button(
            t("download_csv", lang),
            data=to_csv_bytes(df_all),
            file_name=f"taxas_{dl_start}_{dl_end}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with dl2:
        st.download_button(
            t("download_xlsx", lang),
            data=to_excel_bytes(df_all),
            file_name=f"taxas_{dl_start}_{dl_end}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    st.dataframe(df_all, use_container_width=True, hide_index=True, height=400)
