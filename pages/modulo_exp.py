"""
🔮 Módulo Expectativas — Sistema de Expectativas de Mercado
=============================================================
Consulta expectativas anuais do mercado via API do Banco Central.
Endpoint: ExpectativasMercadoAnuais

Lógica:
1. Para cada indicador selecionado, consulta a API ordenando por Data desc.
2. Filtra apenas a data mais recente (Data == max_date).
3. Filtra DataReferencia nos 3 próximos anos a partir do ano atual.
4. Apresenta tabela + gráfico com barras de erro (média ± desvio, min/max).
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date, datetime
from utils.i18n import t
from utils.helpers import render_kpi_card


# =============================================================================
# Available indicators with units
# =============================================================================

INDICATORS = {
    "Câmbio":                           {"unit": "R$/US$", "icon": "💱"},
    "Dívida bruta do governo geral":    {"unit": "% PIB",  "icon": "📋"},
    "IGP-M":                            {"unit": "%",      "icon": "📊"},
    "Investimento direto no país":      {"unit": "US$ bi", "icon": "🌍"},
    "IPCA":                             {"unit": "%",      "icon": "📈"},
    "PIB Total":                        {"unit": "%",      "icon": "🏭"},
    "Resultado nominal":                {"unit": "% PIB",  "icon": "📋"},
    "Resultado primário":               {"unit": "% PIB",  "icon": "📋"},
    "Selic":                            {"unit": "% a.a.", "icon": "💰"},
    "Taxa de desocupação":              {"unit": "%",      "icon": "👷"},
}


# =============================================================================
# Data fetching (with cache)
# =============================================================================

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_expectations(indicator: str, ref_years: tuple) -> pd.DataFrame:
    """
    Consulta a API de Expectativas do BCB para um indicador.

    Parameters
    ----------
    indicator : str
        Nome do indicador (ex: 'IPCA', 'Câmbio').
    ref_years : tuple
        Tupla com os anos de referência (ex: (2026, 2027, 2028)).

    Returns
    -------
    pd.DataFrame com colunas filtradas, apenas data mais recente.
    """
    from bcb import Expectativas

    em = Expectativas()
    ep = em.get_endpoint("ExpectativasMercadoAnuais")

    # Buscar dados ordenados por data desc, com limite generoso
    df = (
        ep.query()
        .filter(ep.Indicador == indicator)
        .orderby(ep.Data.desc())
        .limit(100)
        .collect()
    )

    if df.empty:
        return pd.DataFrame()

    # Encontrar a data mais recente
    df["Data"] = pd.to_datetime(df["Data"])
    max_date = df["Data"].max()

    # Filtrar: apenas data mais recente
    df = df[df["Data"] == max_date].copy()

    # Converter DataReferencia para int (ano)
    df["_ano_ref"] = pd.to_numeric(df["DataReferencia"], errors="coerce").astype("Int64")

    # Filtrar: apenas os anos de referência desejados
    df = df[df["_ano_ref"].isin(ref_years)].copy()

    if df.empty:
        return pd.DataFrame()

    # Selecionar e renomear colunas
    df = df[["DataReferencia", "Media", "Mediana", "DesvioPadrao", "Minimo", "Maximo",
             "numeroRespondentes", "Data"]].copy()

    df = df.sort_values("DataReferencia").reset_index(drop=True)
    
    # Remover duplicatas: manter apenas a primeira entrada por DataReferencia
    df = df.drop_duplicates(subset=["DataReferencia"], keep="first")
    
    return df


# =============================================================================
# Plotly chart: bar with error bars (mean ± std, min/max whiskers)
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

YEAR_COLORS = ["#22D3EE", "#34D399", "#FBBF24"]


def make_expectation_chart(df: pd.DataFrame, var_name: str, unit: str) -> go.Figure:
    """
    Creates a simple bar chart showing the Mean for each reference year.
    """
    fig = go.Figure()

    years = df["DataReferencia"].tolist()

    fig.add_trace(
        go.Bar(
            x=years,
            y=df["Media"],
            marker=dict(
                color="#22D3EE",
                line=dict(width=0),
                opacity=0.85,
            ),
            text=df["Media"].apply(lambda x: f"{x:,.2f}"),
            textposition="outside",
            textfont=dict(color="#F1F5F9", size=12),
            hovertemplate=(
                "<b>%{x}</b><br>"
                f"Média: %{{y:,.2f}} {unit}<br>"
                "<extra></extra>"
            ),
            showlegend=False,
        )
    )

    # Add some headroom for text labels
    y_max = df["Media"].max()
    y_min = df["Media"].min()
    margin = (y_max - y_min) * 0.3 if y_max != y_min else y_max * 0.2

    fig.update_layout(
        **PLOTLY_LAYOUT_BASE,
        title=dict(text=f"{var_name} ({unit})", font=dict(size=14)),
        height=320,
        xaxis={**GRID_STYLE, "type": "category", "title": None},
        yaxis={
            **GRID_STYLE,
            "title": unit,
            "range": [
                max(0, y_min - margin) if y_min >= 0 else y_min - margin,
                y_max + margin,
            ],
        },
        bargap=0.4,
    )

    return fig


# =============================================================================
# Main render function
# =============================================================================

def render(lang: str):
    """Renders the Expectations module page."""

    # ----- Back button -----
    if st.button(t("back_to_hub", lang), key="back_exp"):
        st.session_state.current_page = "hub"
        st.session_state.pop("exp_data", None)
        st.rerun()

    # ----- Header -----
    st.markdown(
        f"""
        <div style="margin-bottom: 24px;">
            <h1 style="font-size:28px; font-weight:700; letter-spacing:-0.02em;">
                {t("exp_page_title", lang)}
            </h1>
            <p style="color:#94A3B8; font-size:14px; margin-top:4px;">
                {t("exp_page_desc", lang)}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ----- Indicator selection (all selected by default) -----
    all_indicators = list(INDICATORS.keys())

    selected = st.multiselect(
        t("exp_select_vars", lang),
        options=all_indicators,
        default=all_indicators,
    )

    if not selected:
        st.info(t("exp_select_vars", lang))
        return

    # Reference years: current year + next 2
    current_year = date.today().year
    ref_years = (current_year, current_year + 1, current_year + 2)

    st.caption(
        f"{t('exp_ref_years', lang)}: **{ref_years[0]}**, **{ref_years[1]}**, **{ref_years[2]}**"
    )

    # ----- Query button -----
    query_btn = st.button(
        t("exp_query", lang),
        key="query_exp",
        type="primary",
    )

    if not query_btn and "exp_data" not in st.session_state:
        return

    # ----- Fetch data for all selected indicators -----
    if query_btn:
        all_data = {}
        progress = st.progress(0, text=t("loading", lang))

        for i, indicator in enumerate(selected):
            try:
                df = fetch_expectations(indicator, ref_years)
                if not df.empty:
                    all_data[indicator] = df
            except Exception as e:
                st.warning(f"{indicator}: {e}")

            progress.progress((i + 1) / len(selected))

        progress.empty()
        st.session_state.exp_data = all_data

    if "exp_data" not in st.session_state:
        return

    all_data = st.session_state.exp_data

    if not all_data:
        st.warning(t("no_data", lang))
        return

    # Show survey date from first available indicator
    first_df = next(iter(all_data.values()))
    survey_date = first_df["Data"].iloc[0]
    if isinstance(survey_date, (datetime, pd.Timestamp)):
        survey_date_str = survey_date.strftime("%d/%m/%Y")
    else:
        survey_date_str = str(survey_date)

    st.markdown(
        f"<div style='font-family:Space Mono,monospace; font-size:12px; color:#64748B; "
        f"margin-bottom:20px;'>"
        f"📅 {t('exp_survey_date', lang)}: <strong style='color:#22D3EE;'>{survey_date_str}</strong>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # =================================================================
    # RENDER EACH INDICATOR
    # =================================================================
    for indicator in selected:
        if indicator not in all_data:
            st.info(t("exp_no_data_var", lang, var=indicator))
            continue

        df = all_data[indicator]
        info = INDICATORS[indicator]
        unit = info["unit"]
        icon = info["icon"]

        st.markdown(
            f"<div style='font-size:18px; font-weight:600; margin:30px 0 12px; "
            f"display:flex; align-items:center; gap:8px;'>"
            f"{icon} {indicator}"
            f"<span style='font-size:12px; color:#64748B; font-family:Space Mono,monospace; "
            f"margin-left:8px;'>{unit}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # Layout: chart left, table right
        col_chart, col_table = st.columns([3, 2], gap="medium")

        with col_chart:
            fig = make_expectation_chart(df, indicator, unit)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with col_table:
            # Prepare display table
            df_display = df[["DataReferencia", "Media", "Mediana", "DesvioPadrao",
                             "Minimo", "Maximo"]].copy()

            col_names = {
                "DataReferencia": "Ano" if lang == "pt" else "Year",
                "Media": t("exp_col_mean", lang),
                "Mediana": t("exp_col_median", lang),
                "DesvioPadrao": t("exp_col_std", lang),
                "Minimo": t("exp_col_min", lang),
                "Maximo": t("exp_col_max", lang),
            }
            df_display.rename(columns=col_names, inplace=True)

            # Format numeric columns to 2 decimals
            num_cols = df_display.columns[1:]
            for c in num_cols:
                df_display[c] = df_display[c].apply(
                    lambda x: f"{x:,.2f}" if pd.notna(x) else "—"
                )

            # Styled HTML table
            ano_col = "Ano" if lang == "pt" else "Year"
            header = "".join(f"<th>{c}</th>" for c in df_display.columns)
            rows_html = ""
            for _, row in df_display.iterrows():
                cells = ""
                for j, val in enumerate(row):
                    if j == 0:
                        cells += f"<td style='font-weight:700; color:#22D3EE;'>{val}</td>"
                    else:
                        cells += f"<td>{val}</td>"
                rows_html += f"<tr>{cells}</tr>"

            table_html = f"""
            <style>
                .exp-table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 13px;
                    font-family: 'DM Sans', sans-serif;
                }}
                .exp-table th {{
                    text-align: left;
                    padding: 10px 12px;
                    font-family: 'Space Mono', monospace;
                    font-size: 11px;
                    font-weight: 700;
                    color: #64748B;
                    text-transform: uppercase;
                    letter-spacing: 0.04em;
                    border-bottom: 2px solid rgba(148,163,184,0.15);
                    background: rgba(255,255,255,0.02);
                }}
                .exp-table td {{
                    padding: 10px 12px;
                    color: #94A3B8;
                    border-bottom: 1px solid rgba(148,163,184,0.06);
                }}
                .exp-table tbody tr:hover {{
                    background: rgba(34,211,238,0.04);
                }}
            </style>
            <table class="exp-table">
                <thead><tr>{header}</tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
            """
            st.markdown(table_html, unsafe_allow_html=True)

            # Respondents info
            if "numeroRespondentes" in df.columns:
                n_resp = df["numeroRespondentes"].iloc[0]
                if pd.notna(n_resp):
                    st.markdown(
                        f"<div style='margin-top:10px; font-size:12px; color:#64748B;'>"
                        f"👥 {int(n_resp)} {t('exp_respondents', lang)}</div>",
                        unsafe_allow_html=True,
                    )

        st.markdown(
            "<hr style='border-color: rgba(148,163,184,0.06); margin:10px 0;'>",
            unsafe_allow_html=True,
        )

    # Footer
    st.markdown(
        f"""
        <div class="footer">
            {t("source", lang)}:
            <a href="https://dadosabertos.bcb.gov.br/" target="_blank">dadosabertos.bcb.gov.br</a>
            · ExpectativasMercadoAnuais
            · {t("built_with", lang)}
        </div>
        """,
        unsafe_allow_html=True,
    )
