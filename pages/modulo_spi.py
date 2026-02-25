"""
⚡ Módulo SPI — Sistema de Pagamentos Instantâneos
====================================================
Consulta estatísticas diárias de transações Pix liquidadas
via API do Banco Central (endpoint PixLiquidadosAtual).
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from utils.i18n import t
from utils.helpers import (
    fmt_number,
    fmt_brl,
    fmt_pct,
    render_kpi_card,
    render_comparison_item,
    to_excel_bytes,
    to_csv_bytes,
)


# =============================================================================
# Data fetching (com cache)
# =============================================================================

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_spi_data(start_date: date) -> pd.DataFrame:
    """
    Consulta a API do BCB para dados do SPI (PixLiquidadosAtual).

    Parameters
    ----------
    start_date : date
        Data inicial da consulta.

    Returns
    -------
    pd.DataFrame
        DataFrame com colunas: Data, Quantidade, Total, Media
    """
    from bcb import SPI

    pix = SPI()
    ep = pix.get_endpoint("PixLiquidadosAtual")

    df = (
        ep.query()
        .select(ep.Data, ep.Quantidade, ep.Total, ep.Media)
        .filter(ep.Data >= datetime(start_date.year, start_date.month, start_date.day))
        .orderby(ep.Data.asc())
        .collect()
    )

    # Garante tipos corretos
    df["Data"] = pd.to_datetime(df["Data"]).dt.date
    df["Quantidade"] = pd.to_numeric(df["Quantidade"], errors="coerce").astype("Int64")
    df["Total"] = pd.to_numeric(df["Total"], errors="coerce")
    df["Media"] = pd.to_numeric(df["Media"], errors="coerce")

    return df


# =============================================================================
# Plotly chart helpers
# =============================================================================

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#94A3B8"),
    margin=dict(l=20, r=20, t=40, b=20),
    hovermode="x unified",
    xaxis=dict(
        gridcolor="rgba(148,163,184,0.07)",
        showline=False,
    ),
    yaxis=dict(
        gridcolor="rgba(148,163,184,0.07)",
        showline=False,
    ),
    hoverlabel=dict(
        bgcolor="#1A2332",
        bordercolor="rgba(148,163,184,0.2)",
        font=dict(color="#F1F5F9"),
    ),
)


def make_area_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color: str,
    title: str,
    y_label: str,
) -> go.Figure:
    """Cria gráfico de área com gradiente."""
    # Cor com transparência para o fill
    color_map = {
        "cyan": ("rgb(34,211,238)", "rgba(34,211,238,0.1)"),
        "emerald": ("rgb(52,211,153)", "rgba(52,211,153,0.1)"),
        "amber": ("rgb(251,191,36)", "rgba(251,191,36,0.1)"),
        "rose": ("rgb(251,113,133)", "rgba(251,113,133,0.1)"),
    }
    line_color, fill_color = color_map.get(color, color_map["cyan"])

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode="lines",
            line=dict(color=line_color, width=2),
            fill="tozeroy",
            fillcolor=fill_color,
            hovertemplate=f"%{{x|%d/%m/%Y}}<br>{y_label}: %{{y:,.0f}}<extra></extra>",
        )
    )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text=title, font=dict(size=14)),
        height=320,
    )

    return fig


# =============================================================================
# Stats helper
# =============================================================================

def compute_stats(df: pd.DataFrame, lang: str) -> pd.DataFrame:
    """Calcula estatísticas descritivas para as colunas numéricas."""
    stats_labels = {
        "mean": t("stat_mean", lang),
        "50%": t("stat_median", lang),
        "std": t("stat_std", lang),
        "min": t("stat_min", lang),
        "max": t("stat_max", lang),
        "25%": t("stat_q1", lang),
        "75%": t("stat_q3", lang),
    }

    desc = df[["Quantidade", "Total", "Media"]].describe()

    rows = []
    for stat_key, label in stats_labels.items():
        rows.append(
            {
                t("stat_metric", lang): label,
                t("stat_qty", lang): fmt_number(desc.loc[stat_key, "Quantidade"]),
                t("stat_total", lang): fmt_brl(desc.loc[stat_key, "Total"]),
                t("stat_avg", lang): f"R$ {desc.loc[stat_key, 'Media']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            }
        )

    return pd.DataFrame(rows)


# =============================================================================
# Main render function
# =============================================================================

def render(lang: str):
    """Renderiza toda a página do módulo SPI."""

    # ----- Back button -----
    if st.button(t("back_to_hub", lang), key="back_to_hub"):
        st.session_state.current_page = "hub"
        st.rerun()

    # ----- Header -----
    st.markdown(
        f"""
        <div style="margin-bottom: 24px;">
            <h1 style="font-size:28px; font-weight:700; letter-spacing:-0.02em;">
                {t("spi_page_title", lang)}
            </h1>
            <p style="color:#94A3B8; font-size:14px; margin-top:4px;">
                {t("spi_page_desc", lang)}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ----- Filters -----
    col_start, col_end, col_btn = st.columns([2, 2, 1], gap="medium")

    with col_start:
        start_date = st.date_input(
            t("start_date", lang),
            value=date(2023, 1, 1),
            min_value=date(2020, 11, 3),  # Pix started Nov 2020
            max_value=date.today(),
            format="DD/MM/YYYY",
        )

    with col_end:
        end_date = st.date_input(
            t("end_date", lang),
            value=date.today(),
            min_value=start_date,
            max_value=date.today(),
            format="DD/MM/YYYY",
        )

    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)  # align button
        query_btn = st.button(
            t("query_api", lang),
            key="query_spi",
            use_container_width=True,
            type="primary",
        )

    # ----- Fetch data -----
    # Auto-query on first load or when button is pressed
    if "spi_data" not in st.session_state:
        st.session_state.spi_queried = False

    if query_btn:
        st.session_state.spi_queried = True

    if not st.session_state.get("spi_queried", False):
        st.info(
            f"👆 {t('start_date', lang)}: selecione a data e clique em "
            f"**{t('query_api', lang)}** para carregar os dados."
            if lang == "pt"
            else f"👆 Select the {t('start_date', lang).lower()} and click "
            f"**{t('query_api', lang)}** to load data."
        )
        return

    # Fetch with spinner
    try:
        with st.spinner(t("loading", lang)):
            df = fetch_spi_data(start_date)
    except Exception as e:
        st.error(t("api_error", lang))
        st.caption(t("api_error_detail", lang))
        with st.expander("Detalhes do erro"):
            st.code(str(e))
        return

    # Filter end date
    df = df[df["Data"] <= end_date].copy()

    if df.empty:
        st.warning(t("no_data", lang))
        return

    # =====================================================================
    # KPI CARDS
    # =====================================================================
    total_days = len(df)
    total_qty = df["Quantidade"].sum()
    total_vol = df["Total"].sum()
    avg_daily = df["Media"].mean()

    k1, k2, k3, k4 = st.columns(4, gap="small")

    with k1:
        st.markdown(
            render_kpi_card(
                t("kpi_days", lang),
                f"{total_days:,}".replace(",", "."),
                t("kpi_days_sub", lang),
                "cyan",
            ),
            unsafe_allow_html=True,
        )

    with k2:
        st.markdown(
            render_kpi_card(
                t("kpi_qty", lang),
                fmt_number(total_qty),
                t("kpi_qty_sub", lang),
                "emerald",
            ),
            unsafe_allow_html=True,
        )

    with k3:
        st.markdown(
            render_kpi_card(
                t("kpi_volume", lang),
                fmt_brl(total_vol),
                t("kpi_volume_sub", lang),
                "amber",
            ),
            unsafe_allow_html=True,
        )

    with k4:
        st.markdown(
            render_kpi_card(
                t("kpi_avg", lang),
                fmt_brl(avg_daily),
                t("kpi_avg_sub", lang),
                "rose",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # =====================================================================
    # CHARTS
    # =====================================================================
    chart1, chart2 = st.columns(2, gap="medium")

    with chart1:
        fig_qty = make_area_chart(
            df,
            x_col="Data",
            y_col="Quantidade",
            color="cyan",
            title=t("chart_qty_title", lang),
            y_label=t("chart_quantity", lang),
        )
        st.plotly_chart(fig_qty, use_container_width=True, config={"displayModeBar": False})

    with chart2:
        fig_vol = make_area_chart(
            df,
            x_col="Data",
            y_col="Total",
            color="emerald",
            title=t("chart_vol_title", lang),
            y_label=t("chart_total", lang),
        )
        st.plotly_chart(fig_vol, use_container_width=True, config={"displayModeBar": False})

    # =====================================================================
    # PERIOD COMPARISON
    # =====================================================================
    st.markdown(
        f'<div class="section-title">{t("comparison_title", lang)}</div>',
        unsafe_allow_html=True,
    )

    comp_col1, comp_col2 = st.columns(2, gap="medium")

    with comp_col1:
        st.caption(f"🔵 {t('period_a', lang)}")
        ca1, ca2 = st.columns(2)
        with ca1:
            comp_a_start = st.date_input(
                f"{t('start_date', lang)} A",
                value=start_date,
                min_value=start_date,
                max_value=end_date,
                key="comp_a_start",
                format="DD/MM/YYYY",
                label_visibility="collapsed",
            )
        with ca2:
            # Default: midpoint between start and end
            midpoint = start_date + (end_date - start_date) // 2
            comp_a_end = st.date_input(
                f"{t('end_date', lang)} A",
                value=midpoint,
                min_value=comp_a_start,
                max_value=end_date,
                key="comp_a_end",
                format="DD/MM/YYYY",
                label_visibility="collapsed",
            )

    with comp_col2:
        st.caption(f"🟣 {t('period_b', lang)}")
        cb1, cb2 = st.columns(2)
        with cb1:
            comp_b_start = st.date_input(
                f"{t('start_date', lang)} B",
                value=comp_a_end + timedelta(days=1),
                min_value=start_date,
                max_value=end_date,
                key="comp_b_start",
                format="DD/MM/YYYY",
                label_visibility="collapsed",
            )
        with cb2:
            comp_b_end = st.date_input(
                f"{t('end_date', lang)} B",
                value=end_date,
                min_value=comp_b_start,
                max_value=end_date,
                key="comp_b_end",
                format="DD/MM/YYYY",
                label_visibility="collapsed",
            )

    # Compute comparison
    df_a = df[(df["Data"] >= comp_a_start) & (df["Data"] <= comp_a_end)]
    df_b = df[(df["Data"] >= comp_b_start) & (df["Data"] <= comp_b_end)]

    if not df_a.empty and not df_b.empty:
        avg_qty_a = df_a["Quantidade"].mean()
        avg_qty_b = df_b["Quantidade"].mean()
        avg_vol_a = df_a["Total"].mean()
        avg_vol_b = df_b["Total"].mean()
        avg_ticket_a = df_a["Media"].mean()
        avg_ticket_b = df_b["Media"].mean()

        delta_qty = (avg_qty_b - avg_qty_a) / avg_qty_a if avg_qty_a else None
        delta_vol = (avg_vol_b - avg_vol_a) / avg_vol_a if avg_vol_a else None
        delta_ticket = (avg_ticket_b - avg_ticket_a) / avg_ticket_a if avg_ticket_a else None

        c1, c2, c3 = st.columns(3, gap="small")

        with c1:
            st.markdown(
                render_comparison_item(
                    t("comp_avg_qty", lang),
                    fmt_number(avg_qty_a),
                    fmt_number(avg_qty_b),
                    delta_qty,
                ),
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                render_comparison_item(
                    t("comp_avg_vol", lang),
                    fmt_brl(avg_vol_a),
                    fmt_brl(avg_vol_b),
                    delta_vol,
                ),
                unsafe_allow_html=True,
            )
        with c3:
            ticket_fmt = lambda v: f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            st.markdown(
                render_comparison_item(
                    t("comp_avg_ticket", lang),
                    ticket_fmt(avg_ticket_a),
                    ticket_fmt(avg_ticket_b),
                    delta_ticket,
                ),
                unsafe_allow_html=True,
            )
    else:
        st.info(t("no_data_period", lang))

    st.markdown("<br>", unsafe_allow_html=True)

    # =====================================================================
    # DESCRIPTIVE STATISTICS
    # =====================================================================
    st.markdown(
        f'<div class="section-title">{t("stats_title", lang)}</div>',
        unsafe_allow_html=True,
    )

    stats_df = compute_stats(df, lang)
    st.dataframe(
        stats_df,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # =====================================================================
    # DATA TABLE + DOWNLOADS
    # =====================================================================
    st.markdown(
        f'<div class="section-title">{t("data_title", lang)}</div>',
        unsafe_allow_html=True,
    )

    st.caption(t("data_showing", lang, n=len(df)))

    # Download buttons
    dl1, dl2, dl_spacer = st.columns([1, 1, 4])

    # Prepare display DataFrame
    df_display = df.copy()
    df_display.columns = [
        t("col_date", lang),
        t("col_quantity", lang),
        t("col_total", lang),
        t("col_average", lang),
    ]

    with dl1:
        st.download_button(
            label=t("download_csv", lang),
            data=to_csv_bytes(df),
            file_name=f"spi_pix_{start_date}_{end_date}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with dl2:
        st.download_button(
            label=t("download_xlsx", lang),
            data=to_excel_bytes(df),
            file_name=f"spi_pix_{start_date}_{end_date}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    # Data table
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        height=400,
    )

    # Footer
    st.markdown(
        f"""
        <div class="footer">
            {t("source", lang)}:
            <a href="https://dadosabertos.bcb.gov.br/" target="_blank">
                dadosabertos.bcb.gov.br
            </a>
            · Endpoint: PixLiquidadosAtual
            · {t("built_with", lang)}
        </div>
        """,
        unsafe_allow_html=True,
    )
