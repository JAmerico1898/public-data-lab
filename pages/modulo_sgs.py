"""
📈 Módulo SGS — Sistema Gerenciador de Séries Temporais
========================================================
Consulta séries temporais do Banco Central via bcb.sgs.
Permite busca por nome, entrada de códigos, nomeação opcional,
gráficos combinados com eixo duplo, correlação e download.

Correções v2:
- sgs.get() chamado com formato de data seguro (yyyy-mm-dd)
- Frequência tratada como reamostragem pós-consulta (não parâmetro da API)
- PeriodIndex convertido para DatetimeIndex automaticamente
- Cache usa tupla (hashable) em vez de dict
- Catálogo mostra frequência nativa de cada série
- Aviso de periodicidade mista é contextual
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date
from utils.i18n import t
from utils.helpers import (
    render_kpi_card,
    to_excel_bytes,
    to_csv_bytes,
)


# =============================================================================
# Popular Series Catalog
# =============================================================================

POPULAR_SERIES = {
    "sgs_cat_inflation": [
        (433, "IPCA", "IPCA - Variação mensal (%)", "M"),
        (192, "INCC", "INCC-DI - Variação mensal (%)", "M"),
        (189, "IGP-M", "IGP-M - Variação mensal (%)", "M"),
        (190, "IGP-DI", "IGP-DI - Variação mensal (%)", "M"),
    ],
    "sgs_cat_interest": [
        (432, "Selic Meta", "Taxa Selic Meta (% a.a.)", "D"),
        (11,  "Selic Over", "Taxa Selic Over (% a.a.)", "D"),
        (12,  "CDI", "CDI Acumulado no mês (%)", "M"),
        (4389, "CDI Anual", "CDI Anualizado (% a.a.)", "D"),
        (226, "TR", "TR - Taxa Referencial (%)", "M"),
    ],
    "sgs_cat_exchange": [
        (1,   "USD Compra", "Taxa de câmbio USD/BRL - Compra", "D"),
        (10813, "USD Venda", "Taxa de câmbio USD/BRL - Venda", "D"),
        (21619, "EUR Compra", "Taxa de câmbio EUR/BRL - Compra", "D"),
        (21620, "EUR Venda", "Taxa de câmbio EUR/BRL - Venda", "D"),
    ],
    "sgs_cat_activity": [
        (24363, "PIB Mensal", "PIB Mensal - Valores correntes (R$ milhões)", "M"),
        (4380,  "PIB Real", "PIB Real - Var. % trimestral", "T"),
        (28183, "IBC-Br", "IBC-Br - Índice de Atividade Econômica", "M"),
    ],
    "sgs_cat_credit": [
        (20542, "Saldo Crédito", "Saldo de operações de crédito (R$ milhões)", "M"),
        (20714, "Inadimplência PF", "Inadimplência PF - Recursos livres (%)", "M"),
    ],
    "sgs_cat_fiscal": [
        (4505,  "Dívida/PIB", "Dívida líquida do setor público (% PIB)", "M"),
        (4536,  "Primário/PIB", "Resultado primário (% PIB) - Acum. 12m", "M"),
    ],
}

# Flat lookup: code → (name, description, frequency)
_SERIES_LOOKUP = {}
for _cat, _items in POPULAR_SERIES.items():
    for _code, _name, _desc, _freq in _items:
        _SERIES_LOOKUP[_code] = (_name, _desc, _freq)


# =============================================================================
# Data fetching (with cache)
# =============================================================================

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_sgs_data(
    codes_tuple: tuple,
    start_str: str,
    end_str: str,
) -> pd.DataFrame:
    """
    Consulta a API do BCB/SGS usando sgs.dataframe().

    Parameters
    ----------
    codes_tuple : tuple of (col_name, code) pairs
        Convertido de dict para tuple para ser hashable (cache do Streamlit).
        Exemplo: (("IPCA", 433), ("INCC", 192))
    start_str : str
        Data inicial no formato 'yyyy-mm-dd'.
    end_str : str
        Data final no formato 'yyyy-mm-dd'.

    Returns
    -------
    pd.DataFrame com DatetimeIndex

    Exemplos equivalentes
    ---------------------
    Sem nomes:
        sgs.dataframe([433, 192], start='2020-01-01', end='2024-12-31')
    Com nomes (dict):
        sgs.dataframe({'IPCA': 433, 'INCC': 192}, start='2020-01-01', end='2024-12-31')
    """
    from bcb import sgs

    # Rebuild dict from tuple: {col_name: code}
    codes_dict = {name: code for name, code in codes_tuple}

    # Tentar com dict {nome: código} para ter colunas nomeadas
    # Se falhar, usar lista de códigos e renomear depois
    df = sgs.get(
        codes=codes_dict,
        start=start_str,
        end=end_str,
        multi=True,
    )

    # Handle PeriodIndex (common for monthly series like IPCA, INCC)
    if isinstance(df.index, pd.PeriodIndex):
        df.index = df.index.to_timestamp()

    # Ensure DatetimeIndex
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    df.index.name = "Date"
    df = df.sort_index()

    return df


def resample_data(df: pd.DataFrame, freq: str) -> pd.DataFrame:
    """
    Reamostra o DataFrame para a frequência desejada (pós-consulta).

    Parameters
    ----------
    freq : str
        'M' = mensal (média), 'A' = anual (média)
    """
    freq_map = {"M": "ME", "A": "YE"}
    pd_freq = freq_map.get(freq, freq)
    return df.resample(pd_freq).mean()


# =============================================================================
# Plotly chart helpers
# =============================================================================

PLOTLY_LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#94A3B8"),
    margin=dict(l=20, r=20, t=50, b=20),
    hovermode="x unified",
    hoverlabel=dict(
        bgcolor="#1A2332",
        bordercolor="rgba(148,163,184,0.2)",
        font=dict(color="#F1F5F9"),
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(size=12),
    ),
)

CHART_COLORS = [
    "#22D3EE",  # cyan
    "#34D399",  # emerald
    "#FBBF24",  # amber
    "#FB7185",  # rose
    "#A78BFA",  # violet
    "#F472B6",  # pink
    "#60A5FA",  # blue
    "#4ADE80",  # green
]

GRID_STYLE = dict(gridcolor="rgba(148,163,184,0.07)", showline=False)


def should_use_dual_axis(df: pd.DataFrame, columns: list) -> tuple:
    """
    Determines if dual Y-axis is needed based on magnitude difference.
    Uses log-scale clustering: groups series by order of magnitude.
    Returns (use_dual, primary_cols, secondary_cols).
    
    Example: IPCA (~0.5), INCC (~0.6), CDI (~12)
    → log10 means: IPCA=-0.3, INCC=-0.2, CDI=1.08
    → Gap between INCC and CDI is largest → split there
    → Primary: [CDI], Secondary: [IPCA, INCC]
    → But majority rule: larger group = primary
    → Primary: [IPCA, INCC], Secondary: [CDI]
    """
    if len(columns) < 2:
        return False, columns, []

    means = {}
    for col in columns:
        m = df[col].dropna().abs().mean()
        if m > 0:
            means[col] = m

    if len(means) < 2:
        return False, columns, []

    # Sort by magnitude
    sorted_cols = sorted(means.items(), key=lambda x: x[1])
    min_mean = sorted_cols[0][1]
    max_mean = sorted_cols[-1][1]

    # Only use dual axis if overall range exceeds 5x
    if max_mean / min_mean <= 5:
        return False, columns, []

    # Find the largest gap in log-space between consecutive series
    log_means = [(col, np.log10(m)) for col, m in sorted_cols]
    best_gap = 0
    best_split = 1  # split index: items before = group A, items from split onward = group B

    for i in range(1, len(log_means)):
        gap = log_means[i][1] - log_means[i - 1][1]
        if gap > best_gap:
            best_gap = gap
            best_split = i

    # Only split if the gap is meaningful (> 0.7 ≈ 5x difference at the split point)
    if best_gap < 0.7:
        return False, columns, []

    group_low = [col for col, _ in log_means[:best_split]]
    group_high = [col for col, _ in log_means[best_split:]]

    # Primary axis = larger group (majority wins); secondary = smaller group
    if len(group_high) >= len(group_low):
        return True, group_high, group_low
    else:
        return True, group_low, group_high


def make_combined_chart(df, columns, title, lang):
    """Creates a combined line chart, with dual Y-axis if needed."""
    use_dual, primary_cols, secondary_cols = should_use_dual_axis(df, columns)
    fig = go.Figure()

    # Forward-fill para séries com periodicidades diferentes
    # (séries mensais preenchem os dias intermediários com o último valor)
    df_plot = df[columns].ffill()

    for i, col in enumerate(columns):
        is_secondary = col in secondary_cols
        fig.add_trace(
            go.Scatter(
                x=df_plot.index,
                y=df_plot[col],
                name=f"{col} {'(→)' if is_secondary else '(←)'}",
                mode="lines",
                line=dict(
                    color=CHART_COLORS[i % len(CHART_COLORS)],
                    width=2.5,
                ),
                yaxis="y2" if is_secondary else "y",
                hovertemplate=f"{col}: %{{y:,.4g}}<extra></extra>",
                connectgaps=True,
            )
        )

    layout = {**PLOTLY_LAYOUT_BASE}
    layout["title"] = dict(text=title, font=dict(size=14))
    layout["height"] = 400
    layout["xaxis"] = {**GRID_STYLE}
    layout["yaxis"] = {
        **GRID_STYLE,
        "title": dict(
            text=" · ".join(primary_cols) if use_dual else None,
            font=dict(color=CHART_COLORS[0], size=12),
        ) if use_dual else None,
    }

    if use_dual:
        sec_color_idx = columns.index(secondary_cols[0]) if secondary_cols[0] in columns else 0
        layout["yaxis2"] = {
            **GRID_STYLE,
            "title": dict(
                text=" · ".join(secondary_cols),
                font=dict(color=CHART_COLORS[sec_color_idx % len(CHART_COLORS)], size=12),
            ),
            "overlaying": "y",
            "side": "right",
        }

    fig.update_layout(**layout)
    return fig


def make_individual_chart(df, col, color):
    """Creates an individual area chart for a single series."""
    if color.startswith("#"):
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        line_color = f"rgb({r},{g},{b})"
        fill_color = f"rgba({r},{g},{b},0.1)"
    else:
        line_color = color
        fill_color = color.replace(")", ",0.1)").replace("rgb", "rgba")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df[col], mode="lines",
            line=dict(color=line_color, width=2),
            fill="tozeroy", fillcolor=fill_color,
            hovertemplate=f"%{{x|%d/%m/%Y}}<br>{col}: %{{y:,.4g}}<extra></extra>",
        )
    )
    fig.update_layout(
        **PLOTLY_LAYOUT_BASE, title=dict(text=col, font=dict(size=14)),
        height=280, xaxis=GRID_STYLE, yaxis=GRID_STYLE, showlegend=False,
    )
    return fig


def make_correlation_heatmap(df, title):
    """Creates a correlation heatmap."""
    corr = df.corr()
    fig = go.Figure(
        data=go.Heatmap(
            z=corr.values, x=corr.columns, y=corr.index,
            colorscale=[[0, "#FB7185"], [0.5, "#1A2332"], [1, "#22D3EE"]],
            zmin=-1, zmax=1,
            text=np.round(corr.values, 3), texttemplate="%{text}",
            textfont=dict(size=12, color="#F1F5F9"),
            hovertemplate="%{x} × %{y}<br>ρ = %{z:.4f}<extra></extra>",
        )
    )
    fig.update_layout(
        **PLOTLY_LAYOUT_BASE, title=dict(text=title, font=dict(size=14)),
        height=400, xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False, autorange="reversed"),
    )
    return fig


def make_scatter(df, col_x, col_y):
    """Creates a scatter plot between two series with trendline."""
    fig = go.Figure(
        data=go.Scatter(
            x=df[col_x], y=df[col_y], mode="markers",
            marker=dict(color="#22D3EE", size=5, opacity=0.6, line=dict(width=0)),
            hovertemplate=f"{col_x}: %{{x:,.4g}}<br>{col_y}: %{{y:,.4g}}<extra></extra>",
        )
    )
    mask = df[[col_x, col_y]].dropna()
    if len(mask) > 2:
        z = np.polyfit(mask[col_x], mask[col_y], 1)
        p = np.poly1d(z)
        x_range = np.linspace(mask[col_x].min(), mask[col_x].max(), 50)
        fig.add_trace(go.Scatter(
            x=x_range, y=p(x_range), mode="lines",
            line=dict(color="#FB7185", width=2, dash="dash"),
            name="Trend", hoverinfo="skip",
        ))
    fig.update_layout(
        **PLOTLY_LAYOUT_BASE,
        title=dict(text=f"{col_x}  ×  {col_y}", font=dict(size=14)),
        height=380, xaxis={**GRID_STYLE, "title": col_x},
        yaxis={**GRID_STYLE, "title": col_y}, showlegend=False,
    )
    return fig


# =============================================================================
# Stats helper
# =============================================================================

def compute_series_stats(df, lang):
    """Computes descriptive statistics per series."""
    rows = []
    for col in df.columns:
        s = df[col].dropna()
        rows.append({
            t("sgs_code", lang): col,
            t("sgs_observations", lang): len(s),
            t("sgs_first_date", lang): s.index.min().strftime("%d/%m/%Y") if len(s) > 0 else "—",
            t("sgs_last_date", lang): s.index.max().strftime("%d/%m/%Y") if len(s) > 0 else "—",
            t("sgs_missing", lang): int(df[col].isna().sum()),
            t("stat_mean", lang): f"{s.mean():,.4f}" if len(s) > 0 else "—",
            t("stat_median", lang): f"{s.median():,.4f}" if len(s) > 0 else "—",
            t("stat_std", lang): f"{s.std():,.4f}" if len(s) > 0 else "—",
            t("stat_min", lang): f"{s.min():,.4f}" if len(s) > 0 else "—",
            t("stat_max", lang): f"{s.max():,.4f}" if len(s) > 0 else "—",
        })
    return pd.DataFrame(rows)


# =============================================================================
# Helper: detect mixed frequencies
# =============================================================================

def detect_mixed_frequencies(series_list):
    """Check if selected series have different known frequencies."""
    freqs = set()
    for s in series_list:
        known = _SERIES_LOOKUP.get(s["code"])
        if known:
            freqs.add(known[2])
    return len(freqs) > 1


# =============================================================================
# Main render function
# =============================================================================

def render(lang: str):
    """Renders the SGS module page."""

    # ----- Back button -----
    if st.button(t("back_to_hub", lang), key="back_sgs"):
        st.session_state.current_page = "hub"
        for key in ["sgs_data", "sgs_codes_dict", "sgs_queried"]:
            st.session_state.pop(key, None)
        st.rerun()

    # ----- Header -----
    st.markdown(
        f"""
        <div style="margin-bottom: 24px;">
            <h1 style="font-size:28px; font-weight:700; letter-spacing:-0.02em;">
                {t("sgs_page_title", lang)}
            </h1>
            <p style="color:#94A3B8; font-size:14px; margin-top:4px;">
                {t("sgs_page_desc", lang)}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ----- Initialize session state -----
    if "sgs_series_list" not in st.session_state:
        st.session_state.sgs_series_list = []

    # =================================================================
    # SERIES INPUT SECTION
    # =================================================================
    tab_search, tab_codes, tab_popular = st.tabs([
        t("sgs_mode_search", lang),
        t("sgs_mode_codes", lang),
        t("sgs_mode_popular", lang),
    ])

    # --- Tab 1: Search by name ---
    with tab_search:
        search_query = st.text_input(
            t("sgs_mode_search", lang),
            placeholder=t("sgs_search_placeholder", lang),
            label_visibility="collapsed",
        )

        if search_query and len(search_query) >= 2:
            query_lower = search_query.lower()
            results = []
            for cat_key, items in POPULAR_SERIES.items():
                for code, name, desc, freq in items:
                    if (
                        query_lower in name.lower()
                        or query_lower in desc.lower()
                        or query_lower in str(code)
                    ):
                        results.append((code, name, desc, freq))

            if results:
                st.caption(t("sgs_search_results", lang))
                for code, name, desc, freq in results:
                    already_added = any(
                        s["code"] == code for s in st.session_state.sgs_series_list
                    )
                    col_info, col_freq_tag, col_btn = st.columns([5, 1, 1])
                    with col_info:
                        st.markdown(
                            f"**{code}** — {name} · "
                            f"<span style='color:#64748B;font-size:12px;'>{desc}</span>",
                            unsafe_allow_html=True,
                        )
                    with col_freq_tag:
                        freq_lbl = {"D": "Diária", "M": "Mensal", "T": "Trim.", "A": "Anual"}.get(freq, freq)
                        st.markdown(
                            f"<span style='font-family:Space Mono,monospace; font-size:11px; "
                            f"color:#64748B; padding:2px 8px; border:1px solid rgba(148,163,184,0.2); "
                            f"border-radius:4px;'>{freq_lbl}</span>",
                            unsafe_allow_html=True,
                        )
                    with col_btn:
                        if already_added:
                            st.button("✓", key=f"search_add_{code}", disabled=True)
                        else:
                            if st.button(t("sgs_add", lang), key=f"search_add_{code}"):
                                st.session_state.sgs_series_list.append({"code": code, "name": name})
                                st.rerun()
            else:
                st.info(t("sgs_no_results", lang))

    # --- Tab 2: Manual code entry ---
    with tab_codes:
        codes_input = st.text_input(
            t("sgs_mode_codes", lang),
            placeholder=t("sgs_codes_placeholder", lang),
            label_visibility="collapsed",
        )
        st.caption(t("sgs_codes_help", lang))

        if st.button(t("sgs_add", lang), key="add_codes_btn"):
            if codes_input:
                for part in codes_input.split(","):
                    part = part.strip()
                    if part.isdigit():
                        code = int(part)
                        already = any(s["code"] == code for s in st.session_state.sgs_series_list)
                        if not already:
                            known = _SERIES_LOOKUP.get(code)
                            default_name = known[0] if known else ""
                            st.session_state.sgs_series_list.append({"code": code, "name": default_name})
                st.rerun()

    # --- Tab 3: Popular series ---
    with tab_popular:
        st.caption(t("sgs_popular_desc", lang))

        for cat_key, items in POPULAR_SERIES.items():
            st.markdown(f"**{t(cat_key, lang)}**")
            n_cols = min(len(items), 4)
            cols = st.columns(n_cols)

            for i, (code, name, desc, freq) in enumerate(items):
                already_added = any(s["code"] == code for s in st.session_state.sgs_series_list)
                with cols[i % n_cols]:
                    freq_tag = {"D": "D", "M": "M", "T": "T", "A": "A"}.get(freq, "")
                    label = f"✓ {code}" if already_added else f"{code} {name} [{freq_tag}]"
                    if st.button(label, key=f"pop_{code}", disabled=already_added, use_container_width=True):
                        st.session_state.sgs_series_list.append({"code": code, "name": name})
                        st.rerun()

    st.markdown("<hr style='border-color: rgba(148,163,184,0.1);'>", unsafe_allow_html=True)

    # =================================================================
    # SELECTED SERIES TABLE
    # =================================================================
    st.markdown(
        f'<div class="section-title">{t("sgs_selected_series", lang)}</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.sgs_series_list:
        st.info(t("sgs_no_series", lang))
        return

    if len(st.session_state.sgs_series_list) > 3:
        st.info(t("sgs_warn_max_chart", lang))

    if detect_mixed_frequencies(st.session_state.sgs_series_list):
        st.warning(t("sgs_warn_periodicity", lang))

    series_to_remove = []
    for idx, series in enumerate(st.session_state.sgs_series_list):
        col_code, col_name, col_freq_info, col_remove = st.columns([1, 3, 1, 0.5])

        with col_code:
            st.markdown(
                f"<div style='padding:8px 0; font-family:Space Mono,monospace; "
                f"font-weight:700; color:#22D3EE;'>{series['code']}</div>",
                unsafe_allow_html=True,
            )
        with col_name:
            new_name = st.text_input(
                t("sgs_name_label", lang), value=series["name"],
                placeholder=t("sgs_name_placeholder", lang),
                key=f"name_{idx}", label_visibility="collapsed",
            )
            st.session_state.sgs_series_list[idx]["name"] = new_name

        with col_freq_info:
            known = _SERIES_LOOKUP.get(series["code"])
            if known:
                fl = {"D": "Diária", "M": "Mensal", "T": "Trim.", "A": "Anual"}.get(known[2], "?")
                st.markdown(
                    f"<div style='padding:8px 0; font-size:11px; color:#64748B; "
                    f"font-family:Space Mono,monospace;'>{fl}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown("<div style='padding:8px 0; font-size:11px; color:#64748B;'>—</div>", unsafe_allow_html=True)

        with col_remove:
            if st.button("🗑️", key=f"remove_{idx}"):
                series_to_remove.append(idx)

    if series_to_remove:
        for idx in sorted(series_to_remove, reverse=True):
            st.session_state.sgs_series_list.pop(idx)
        st.rerun()

    if len(st.session_state.sgs_series_list) > 1:
        if st.button(t("sgs_clear_all", lang), key="clear_all"):
            st.session_state.sgs_series_list = []
            st.rerun()

    st.markdown("<hr style='border-color: rgba(148,163,184,0.1);'>", unsafe_allow_html=True)

    # =================================================================
    # DATE RANGE & RESAMPLE FREQUENCY
    # =================================================================
    col_start, col_end, col_freq, col_btn = st.columns([2, 2, 2, 1], gap="medium")

    with col_start:
        start_date = st.date_input(
            t("start_date", lang), value=date(2020, 1, 1),
            min_value=date(1986, 1, 1), max_value=date.today(), format="DD/MM/YYYY",
        )

    with col_end:
        end_date = st.date_input(
            t("end_date", lang), value=date.today(),
            min_value=start_date, max_value=date.today(), format="DD/MM/YYYY",
        )

    resample_options_pt = {
        "Original (sem reamostragem)": "original",
        "Mensal (média)": "M",
        "Anual (média)": "A",
    }
    resample_options_en = {
        "Original (no resampling)": "original",
        "Monthly (mean)": "M",
        "Annual (mean)": "A",
    }
    resample_options = resample_options_pt if lang == "pt" else resample_options_en

    with col_freq:
        resample_label = st.selectbox(
            t("sgs_frequency", lang),
            options=list(resample_options.keys()),
        )
        resample_value = resample_options[resample_label]

    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        query_btn = st.button(
            t("query_api", lang), key="query_sgs",
            use_container_width=True, type="primary",
        )

    # Warnings
    days_range = (end_date - start_date).days
    if days_range > 3650:
        st.warning(t("sgs_warn_10y", lang))

    # =================================================================
    # FETCH DATA
    # =================================================================
    if not query_btn and "sgs_data" not in st.session_state:
        return

    if query_btn:
        codes_dict = {}
        for s in st.session_state.sgs_series_list:
            if s["name"].strip():
                col_name = f"{s['code']}_{s['name'].strip()}"
            else:
                col_name = str(s["code"])
            codes_dict[col_name] = s["code"]

        codes_tuple = tuple(codes_dict.items())

        try:
            with st.spinner(t("loading", lang)):
                df = fetch_sgs_data(
                    codes_tuple=codes_tuple,
                    start_str=start_date.strftime("%Y-%m-%d"),
                    end_str=end_date.strftime("%Y-%m-%d"),
                )
                if resample_value != "original":
                    df = resample_data(df, resample_value)

            st.session_state.sgs_data = df
            st.session_state.sgs_codes_dict = codes_dict
        except Exception as e:
            st.error(t("api_error", lang))
            st.caption(t("api_error_detail", lang))
            with st.expander("Detalhes do erro / Error details"):
                st.code(str(e))
            return

    if "sgs_data" not in st.session_state:
        return

    df = st.session_state.sgs_data

    if df.empty:
        st.warning(t("no_data", lang))
        return

    all_columns = list(df.columns)
    chart_columns = all_columns[:3]

    # =================================================================
    # KPI CARDS
    # =================================================================
    kpi_colors = ["cyan", "emerald", "amber", "rose"]
    n_kpis = min(len(all_columns), 4)
    kpi_cols = st.columns(n_kpis, gap="small")

    for i in range(n_kpis):
        col = all_columns[i]
        s = df[col].dropna()
        with kpi_cols[i]:
            last_val = f"{s.iloc[-1]:,.4g}" if len(s) > 0 else "—"
            last_date = s.index[-1].strftime("%d/%m/%Y") if len(s) > 0 else ""
            st.markdown(
                render_kpi_card(col, last_val, last_date, kpi_colors[i % 4]),
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # =================================================================
    # CHARTS
    # =================================================================
    if len(chart_columns) >= 2:
        st.markdown(f'<div class="section-title">{t("sgs_chart_combined", lang)}</div>', unsafe_allow_html=True)
        fig_combined = make_combined_chart(df[chart_columns], chart_columns, t("sgs_chart_title", lang), lang)
        st.plotly_chart(fig_combined, use_container_width=True, config={"displayModeBar": False})

    st.markdown(f'<div class="section-title">{t("sgs_chart_individual", lang)}</div>', unsafe_allow_html=True)

    if len(chart_columns) >= 2:
        chart_cols_row = st.columns(min(len(chart_columns), 3), gap="medium")
        for i, col in enumerate(chart_columns):
            with chart_cols_row[i]:
                fig = make_individual_chart(df, col, CHART_COLORS[i])
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    elif len(chart_columns) == 1:
        fig = make_individual_chart(df, chart_columns[0], CHART_COLORS[0])
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<br>", unsafe_allow_html=True)

    # =================================================================
    # CORRELATION
    # =================================================================
    if len(chart_columns) >= 2:
        st.markdown(f'<div class="section-title">{t("sgs_correlation_title", lang)}</div>', unsafe_allow_html=True)
        corr_cols = st.columns([3, 2], gap="medium")

        with corr_cols[0]:
            fig_heatmap = make_correlation_heatmap(df[chart_columns].dropna(), t("sgs_heatmap_title", lang))
            st.plotly_chart(fig_heatmap, use_container_width=True, config={"displayModeBar": False})

        with corr_cols[1]:
            st.markdown(
                f'<div class="section-title" style="font-size:13px;">{t("sgs_scatter_title", lang)}</div>',
                unsafe_allow_html=True,
            )
            scatter_x = st.selectbox(t("sgs_scatter_select_x", lang), options=chart_columns, index=0, key="scatter_x")
            scatter_y = st.selectbox(t("sgs_scatter_select_y", lang), options=chart_columns, index=min(1, len(chart_columns) - 1), key="scatter_y")

            if scatter_x != scatter_y:
                fig_scatter = make_scatter(df.dropna(subset=[scatter_x, scatter_y]), scatter_x, scatter_y)
                st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})

        st.markdown("<br>", unsafe_allow_html=True)

    # =================================================================
    # STATISTICS
    # =================================================================
    st.markdown(f'<div class="section-title">{t("sgs_stats_per_series", lang)}</div>', unsafe_allow_html=True)
    stats_df = compute_series_stats(df, lang)
    st.dataframe(stats_df, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # =================================================================
    # DATA TABLE + DOWNLOADS
    # =================================================================
    st.markdown(f'<div class="section-title">{t("data_title", lang)}</div>', unsafe_allow_html=True)

    df_export = df.copy()
    df_export.index = df_export.index.strftime("%d/%m/%Y")
    df_export = df_export.reset_index()
    df_export.rename(columns={"Date": t("col_date", lang)}, inplace=True)

    st.caption(t("data_showing", lang, n=len(df_export)))

    dl1, dl2, dl_spacer = st.columns([1, 1, 4])
    with dl1:
        st.download_button(
            label=t("download_csv", lang), data=to_csv_bytes(df_export),
            file_name=f"sgs_{start_date}_{end_date}.csv",
            mime="text/csv", use_container_width=True,
        )
    with dl2:
        st.download_button(
            label=t("download_xlsx", lang), data=to_excel_bytes(df_export),
            file_name=f"sgs_{start_date}_{end_date}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    st.dataframe(df_export, use_container_width=True, hide_index=True, height=400)

    # Footer
    st.markdown(
        f"""
        <div class="footer">
            {t("source", lang)}:
            <a href="https://dadosabertos.bcb.gov.br/" target="_blank">dadosabertos.bcb.gov.br</a>
            · SGS API · {t("built_with", lang)}
        </div>
        """,
        unsafe_allow_html=True,
    )
