"""
📍 Módulo Inadimplência — Operações de Crédito
================================================
Inadimplência por região e estado (PF e PJ).
Usa bcb.sgs.regional_economy.get_non_performing_loans.

Layout:
- Mapa do Brasil colorido por região (cores fixas, sem relação com valores)
- Hover mostra inadimplência PF/PJ da região e do estado
- Clique no estado → gráficos estado vs região
- Abaixo: 2 gráficos de linha (PF e PJ por região, 48 meses)
- Aba Download: dados brutos por região ou estado
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
from datetime import date
from utils.i18n import t
from utils.helpers import to_excel_bytes, to_csv_bytes


# =============================================================================
# Region / State config
# =============================================================================

REGIONS = {
    "N":  ["AC", "AP", "AM", "PA", "RO", "RR", "TO"],
    "NE": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
    "CO": ["DF", "GO", "MT", "MS"],
    "SE": ["ES", "MG", "RJ", "SP"],
    "S":  ["PR", "RS", "SC"],
}

STATE_TO_REGION = {}
for reg, states in REGIONS.items():
    for uf in states:
        STATE_TO_REGION[uf] = reg

ALL_STATES = sorted(STATE_TO_REGION.keys())

REGION_NAMES = {
    "N": "Norte", "NE": "Nordeste", "CO": "Centro-Oeste", "SE": "Sudeste", "S": "Sul",
}

REGION_COLORS = {
    "N":  "#22D3EE",  # cyan
    "NE": "#34D399",  # emerald
    "CO": "#FBBF24",  # amber
    "SE": "#FB7185",  # rose
    "S":  "#A78BFA",  # violet
}

STATE_NAMES = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas",
    "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo",
    "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
    "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte", "RS": "Rio Grande do Sul", "RO": "Rondônia",
    "RR": "Roraima", "SC": "Santa Catarina", "SP": "São Paulo",
    "SE": "Sergipe", "TO": "Tocantins",
}


# =============================================================================
# Data fetching
# =============================================================================

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_npl(location: str, mode: str, last: int = 48) -> pd.DataFrame:
    """
    Fetch non-performing loans data.

    Parameters
    ----------
    location : str
        Region code ("N", "NE", ...) or state code ("SP", "BA", ...).
    mode : str
        "pf", "pj", or "all".
    last : int
        Number of last months.
    """
    from bcb.sgs.regional_economy import get_non_performing_loans

    df = get_non_performing_loans(location, last=last, mode=mode)

    # Ensure DatetimeIndex
    if isinstance(df.index, pd.PeriodIndex):
        df.index = df.index.to_timestamp()
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    df.index.name = "Date"
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_npl_range(location: str, mode: str, start: str, end: str) -> pd.DataFrame:
    """Fetch NPL with date range for download."""
    from bcb.sgs.regional_economy import get_non_performing_loans

    df = get_non_performing_loans(location, start=start, end=end, mode=mode)

    if isinstance(df.index, pd.PeriodIndex):
        df.index = df.index.to_timestamp()
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    df.index.name = "Date"
    return df


def _safe_fetch_last(location: str, mode: str) -> float | None:
    """Fetch last value for a location/mode. Returns float or None."""
    try:
        df = fetch_npl(location, mode=mode, last=1)
        if not df.empty:
            return float(df.iloc[-1, 0])
    except Exception:
        pass
    return None


def load_all_data():
    """
    Load latest values for all states and regions (PF + PJ separately).
    API mode='all' returns total (not PF+PJ split), so we fetch each mode.
    API last= max is 20, so for 48 months we use start/end.
    Returns: (state_data, region_data, region_series_pf, region_series_pj)
    """
    # State latest values (for map hover) — PF and PJ separately
    state_data = {}  # UF -> {"pf": val, "pj": val}
    for uf in ALL_STATES:
        state_data[uf] = {
            "pf": _safe_fetch_last(uf, "pf"),
            "pj": _safe_fetch_last(uf, "pj"),
        }

    # Region latest values
    region_data = {}  # REG -> {"pf": val, "pj": val}
    for reg in REGIONS.keys():
        region_data[reg] = {
            "pf": _safe_fetch_last(reg, "pf"),
            "pj": _safe_fetch_last(reg, "pj"),
        }

    # Region time series (48 months) for charts — use start/end
    today = date.today()
    y4 = today.year - 4
    m4 = today.month
    start_4y = date(y4, m4, 1).strftime("%Y-%m-%d")
    end_str = today.strftime("%Y-%m-%d")

    region_series_pf = {}
    region_series_pj = {}
    for reg in REGIONS.keys():
        try:
            df_pf = fetch_npl_range(reg, mode="pf", start=start_4y, end=end_str)
            if not df_pf.empty:
                region_series_pf[reg] = df_pf.iloc[:, 0]
        except Exception:
            pass
        try:
            df_pj = fetch_npl_range(reg, mode="pj", start=start_4y, end=end_str)
            if not df_pj.empty:
                region_series_pj[reg] = df_pj.iloc[:, 0]
        except Exception:
            pass

    return state_data, region_data, region_series_pf, region_series_pj


# =============================================================================
# GeoJSON for Brazil states (simplified inline)
# =============================================================================

@st.cache_data(ttl=86400)
def get_brazil_geojson():
    """Fetch Brazil states GeoJSON from a public source."""
    import urllib.request
    url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


# =============================================================================
# Plotly charts
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


def make_brazil_map(state_data, region_data, geojson, lang):
    """
    Create a choropleth map of Brazil.
    Each region has a base color; states get lighter/darker shades
    based on their NPL (PF+PJ average). Higher NPL = darker shade.
    """
    if geojson is None:
        return None

    # Collect NPL values per region for normalization
    region_npl_values = {}  # reg -> list of (uf, npl_avg)
    for uf in ALL_STATES:
        reg = STATE_TO_REGION[uf]
        s_data = state_data.get(uf, {})
        pf = s_data.get("pf")
        pj = s_data.get("pj")
        vals = [v for v in [pf, pj] if v is not None and pd.notna(v)]
        npl_avg = float(np.mean(vals)) if vals else None
        if reg not in region_npl_values:
            region_npl_values[reg] = []
        region_npl_values[reg].append((uf, npl_avg))

    # Min/max per region for normalization
    region_ranges = {}
    for reg, items in region_npl_values.items():
        vals = [v for _, v in items if v is not None]
        if vals and max(vals) > min(vals):
            region_ranges[reg] = (min(vals), max(vals))
        else:
            region_ranges[reg] = (0, 1)

    def shade_color(hex_color, factor):
        """factor 0→very light, 1→base color."""
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        blend = 0.3 + 0.7 * factor
        r = min(255, int(r * blend + 255 * (1 - blend)))
        g = min(255, int(g * blend + 255 * (1 - blend)))
        b = min(255, int(b * blend + 255 * (1 - blend)))
        return f"#{r:02x}{g:02x}{b:02x}"

    # Build one trace per state for individual coloring
    fig = go.Figure()

    for feature in geojson["features"]:
        uf = feature["properties"].get("sigla", "")
        if not uf or uf not in STATE_TO_REGION:
            continue

        reg = STATE_TO_REGION[uf]
        reg_name = REGION_NAMES.get(reg, reg)
        state_name = STATE_NAMES.get(uf, uf)
        base_color = REGION_COLORS.get(reg, "#94A3B8")

        # Compute shade factor
        s_data = state_data.get(uf, {})
        pf = s_data.get("pf")
        pj = s_data.get("pj")
        vals = [v for v in [pf, pj] if v is not None and pd.notna(v)]
        npl_avg = float(np.mean(vals)) if vals else None

        rng = region_ranges.get(reg, (0, 1))
        if npl_avg is not None and rng[1] > rng[0]:
            factor = (npl_avg - rng[0]) / (rng[1] - rng[0])
        else:
            factor = 0.5

        fill_color = shade_color(base_color, factor)

        # Hover text
        s_pf_str = f"{pf:.2f}%" if pf is not None and pd.notna(pf) else "—"
        s_pj_str = f"{pj:.2f}%" if pj is not None and pd.notna(pj) else "—"

        r_data = region_data.get(reg, {})
        r_pf = r_data.get("pf")
        r_pj = r_data.get("pj")
        r_pf_str = f"{r_pf:.2f}%" if r_pf is not None and pd.notna(r_pf) else "—"
        r_pj_str = f"{r_pj:.2f}%" if r_pj is not None and pd.notna(r_pj) else "—"

        hover = (
            f"<b>{state_name} ({uf})</b> — {reg_name}<br>"
            f"<br>"
            f"<b>{t('inad_state', lang)}:</b><br>"
            f"  PF: {s_pf_str} · PJ: {s_pj_str}<br>"
            f"<br>"
            f"<b>{t('inad_region', lang)} {reg_name}:</b><br>"
            f"  PF: {r_pf_str} · PJ: {r_pj_str}"
        )

        # Individual GeoJSON per state
        single_geojson = {"type": "FeatureCollection", "features": [feature]}

        fig.add_trace(
            go.Choropleth(
                geojson=single_geojson,
                locations=[uf],
                z=[factor],
                featureidkey="properties.sigla",
                colorscale=[[0, fill_color], [1, fill_color]],
                showscale=False,
                hovertext=[hover],
                hoverinfo="text",
                marker=dict(line=dict(color="#0F172A", width=1)),
            )
        )

    fig.update_geos(
        fitbounds="locations",
        visible=False,
        bgcolor="rgba(0,0,0,0)",
    )

    fig.update_layout(
        **PLOTLY_LAYOUT_BASE,
        title=dict(text=t("inad_map_title", lang), font=dict(size=14)),
        height=550,
        geo=dict(bgcolor="rgba(0,0,0,0)"),
        dragmode=False,
    )

    # Region legend
    for reg, color in REGION_COLORS.items():
        fig.add_trace(
            go.Scattergeo(
                lon=[None], lat=[None],
                mode="markers",
                marker=dict(size=10, color=color),
                name=f"{reg} — {REGION_NAMES[reg]}",
                showlegend=True,
            )
        )

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.05,
            xanchor="center",
            x=0.5,
            font=dict(size=11),
        ),
    )

    return fig


def make_region_line_chart(series_dict, title, lang):
    """Create a line chart with one line per region."""
    fig = go.Figure()

    for reg in ["N", "NE", "CO", "SE", "S"]:
        if reg not in series_dict:
            continue
        s = series_dict[reg]
        fig.add_trace(
            go.Scatter(
                x=s.index,
                y=s.values,
                name=f"{reg} — {REGION_NAMES[reg]}",
                mode="lines",
                line=dict(color=REGION_COLORS[reg], width=2),
                hovertemplate=f"{REGION_NAMES[reg]}: %{{y:.2f}}%<extra></extra>",
            )
        )

    layout_base = {**PLOTLY_LAYOUT_BASE}
    layout_base["margin"] = dict(l=20, r=20, t=50, b=80)

    fig.update_layout(
        **layout_base,
        title=dict(text=title, font=dict(size=13)),
        height=400,
        xaxis=GRID_STYLE,
        yaxis={**GRID_STYLE, "title": "%"},
        legend=dict(
            orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5,
            font=dict(size=10),
        ),
    )

    return fig


def make_state_vs_region_chart(df_state, df_region, uf, reg, mode_label, lang):
    """Line chart comparing state vs region for PF or PJ."""
    fig = go.Figure()

    state_name = STATE_NAMES.get(uf, uf)
    reg_name = REGION_NAMES.get(reg, reg)

    if df_state is not None and not df_state.empty:
        s = df_state.iloc[:, 0]
        fig.add_trace(
            go.Scatter(
                x=s.index, y=s.values,
                name=f"{state_name} ({uf})",
                mode="lines",
                line=dict(color="#22D3EE", width=2.5),
                hovertemplate=f"{state_name}: %{{y:.2f}}%<extra></extra>",
            )
        )

    if df_region is not None and not df_region.empty:
        s = df_region.iloc[:, 0]
        fig.add_trace(
            go.Scatter(
                x=s.index, y=s.values,
                name=f"Região {reg_name}",
                mode="lines",
                line=dict(color=REGION_COLORS.get(reg, "#94A3B8"), width=2, dash="dash"),
                hovertemplate=f"Região {reg_name}: %{{y:.2f}}%<extra></extra>",
            )
        )

    title = f"{mode_label}: {state_name} vs Região {reg_name}"
    fig.update_layout(
        **PLOTLY_LAYOUT_BASE,
        title=dict(text=title, font=dict(size=13)),
        height=320,
        xaxis=GRID_STYLE,
        yaxis={**GRID_STYLE, "title": "%"},
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(size=10),
        ),
    )

    return fig


# =============================================================================
# Main render
# =============================================================================

def render(lang: str):
    """Renders the NPL module page."""

    if st.button(t("back_to_hub", lang), key="back_inad"):
        st.session_state.current_page = "hub"
        for k in list(st.session_state.keys()):
            if k.startswith("inad_"):
                del st.session_state[k]
        st.rerun()

    st.markdown(
        f"""
        <div style="margin-bottom: 24px;">
            <h1 style="font-size:28px; font-weight:700; letter-spacing:-0.02em;">
                {t("inad_page_title", lang)}
            </h1>
            <p style="color:#94A3B8; font-size:14px; margin-top:4px;">
                {t("inad_page_desc", lang)}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_map, tab_download = st.tabs([
        t("inad_tab_map", lang),
        t("inad_tab_download", lang),
    ])

    with tab_map:
        _render_map_tab(lang)

    with tab_download:
        _render_download_tab(lang)

    st.markdown(
        f"""
        <div class="footer">
            {t("source", lang)}:
            <a href="https://dadosabertos.bcb.gov.br/" target="_blank">dadosabertos.bcb.gov.br</a>
            · SGS Regional Economy · {t("built_with", lang)}
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# Tab: Map + Charts
# =============================================================================

def _render_map_tab(lang: str):
    query_btn = st.button(t("inad_query", lang), key="query_inad", type="primary")

    if not query_btn and "inad_data" not in st.session_state:
        return

    if query_btn:
        progress = st.progress(0, text=t("loading", lang))
        geojson = get_brazil_geojson()
        progress.progress(0.1)

        state_data, region_data, region_series_pf, region_series_pj = load_all_data()
        progress.progress(0.9)

        st.session_state.inad_data = {
            "geojson": geojson,
            "state_data": state_data,
            "region_data": region_data,
            "region_series_pf": region_series_pf,
            "region_series_pj": region_series_pj,
        }
        progress.empty()

    data = st.session_state.inad_data
    geojson = data["geojson"]
    state_data = data["state_data"]
    region_data = data["region_data"]
    region_series_pf = data["region_series_pf"]
    region_series_pj = data["region_series_pj"]

    # ----- Map -----
    if geojson:
        fig_map = make_brazil_map(state_data, region_data, geojson, lang)
        if fig_map:
            map_event = st.plotly_chart(
                fig_map,
                use_container_width=True,
                config={"displayModeBar": False, "staticPlot": False, "scrollZoom": False},
                on_select="rerun",
                key="brazil_map",
            )

            # Detect click on state
            selected_uf = None
            if map_event and hasattr(map_event, "selection") and map_event.selection:
                sel = map_event.selection
                if hasattr(sel, "points") and sel.points:
                    pt = sel.points[0]
                    loc = pt.get("location")
                    if loc and loc in STATE_TO_REGION:
                        selected_uf = loc

            st.caption(t("inad_click_state", lang))

            # ----- State detail charts (if clicked) -----
            if selected_uf:
                _render_state_detail(selected_uf, lang)
    else:
        st.warning("⚠️ GeoJSON do Brasil indisponível. Verifique a conexão.")

        # Fallback: state selector
        selected_uf = st.selectbox(
            t("inad_state", lang),
            options=ALL_STATES,
            format_func=lambda uf: f"{STATE_NAMES.get(uf, uf)} ({uf})",
        )
        if selected_uf:
            _render_state_detail(selected_uf, lang)

    st.markdown("<br>", unsafe_allow_html=True)

    # ----- Region line charts -----
    col_pf, col_pj = st.columns(2, gap="medium")

    with col_pf:
        if region_series_pf:
            fig_pf = make_region_line_chart(
                region_series_pf,
                t("inad_region_pf", lang),
                lang,
            )
            st.plotly_chart(fig_pf, use_container_width=True, config={"displayModeBar": False})

    with col_pj:
        if region_series_pj:
            fig_pj = make_region_line_chart(
                region_series_pj,
                t("inad_region_pj", lang),
                lang,
            )
            st.plotly_chart(fig_pj, use_container_width=True, config={"displayModeBar": False})


def _render_state_detail(uf: str, lang: str):
    """Render state vs region comparison charts."""
    reg = STATE_TO_REGION.get(uf, "")
    state_name = STATE_NAMES.get(uf, uf)

    st.markdown(
        f"<div style='font-size:18px; font-weight:700; margin:20px 0 10px; color:#22D3EE;'>"
        f"📍 {t('inad_state_detail', lang, uf=f'{state_name} ({uf})')}</div>",
        unsafe_allow_html=True,
    )

    # Fetch state and region data (use start/end — last max is 20)
    today = date.today()
    start_4y = date(today.year - 4, today.month, 1).strftime("%Y-%m-%d")
    end_str = today.strftime("%Y-%m-%d")

    try:
        df_state_pf = fetch_npl_range(uf, mode="pf", start=start_4y, end=end_str)
        df_state_pj = fetch_npl_range(uf, mode="pj", start=start_4y, end=end_str)
        df_region_pf = fetch_npl_range(reg, mode="pf", start=start_4y, end=end_str)
        df_region_pj = fetch_npl_range(reg, mode="pj", start=start_4y, end=end_str)
    except Exception as e:
        st.warning(f"Erro ao buscar dados: {e}")
        return

    col_pf, col_pj = st.columns(2, gap="medium")

    with col_pf:
        fig = make_state_vs_region_chart(
            df_state_pf, df_region_pf, uf, reg, t("inad_pf", lang), lang
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_pj:
        fig = make_state_vs_region_chart(
            df_state_pj, df_region_pj, uf, reg, t("inad_pj", lang), lang
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# =============================================================================
# Tab: Download
# =============================================================================

def _render_download_tab(lang: str):
    st.markdown(
        f'<div class="section-title">{t("inad_download_title", lang)}</div>',
        unsafe_allow_html=True,
    )
    st.caption(t("inad_download_desc", lang))

    col_scope, col_start, col_end = st.columns(3)

    with col_scope:
        scope = st.radio(
            t("inad_scope", lang),
            options=[t("inad_scope_regions", lang), t("inad_scope_states", lang)],
            key="inad_dl_scope",
        )

    with col_start:
        dl_start = st.date_input(
            t("start_date", lang),
            value=date(2020, 1, 1),
            format="DD/MM/YYYY",
            key="inad_dl_start",
        )

    with col_end:
        dl_end = st.date_input(
            t("end_date", lang),
            value=date.today(),
            format="DD/MM/YYYY",
            key="inad_dl_end",
        )

    dl_btn = st.button(t("inad_download_btn", lang), key="inad_dl_btn", type="primary")

    if not dl_btn:
        return

    is_regions = scope == t("inad_scope_regions", lang)
    locations = list(REGIONS.keys()) if is_regions else ALL_STATES

    start_str = dl_start.strftime("%Y-%m-%d")
    end_str = dl_end.strftime("%Y-%m-%d")

    progress = st.progress(0, text=t("inad_downloading", lang))
    all_frames = []
    total = len(locations) * 2  # pf + pj for each

    step = 0
    for loc in locations:
        for mode in ["pf", "pj"]:
            try:
                df = fetch_npl_range(loc, mode=mode, start=start_str, end=end_str)
                if not df.empty:
                    # API returns column named after location (e.g. "SP", "NE")
                    col_name = df.columns[0]
                    df_out = df.reset_index()
                    df_out.rename(columns={col_name: "Valor"}, inplace=True)
                    df_out["Date"] = pd.to_datetime(df_out["Date"]).dt.strftime("%Y-%m-%d")
                    df_out["Local"] = loc
                    df_out["Modo"] = mode.upper()
                    if is_regions:
                        df_out["NomeLocal"] = REGION_NAMES.get(loc, loc)
                    else:
                        df_out["NomeLocal"] = STATE_NAMES.get(loc, loc)
                    df_out = df_out[["Date", "Valor", "Local", "Modo", "NomeLocal"]]
                    all_frames.append(df_out)
            except Exception:
                pass

            step += 1
            progress.progress(step / total)

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
            file_name=f"inadimplencia_{dl_start}_{dl_end}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with dl2:
        st.download_button(
            t("download_xlsx", lang),
            data=to_excel_bytes(df_all),
            file_name=f"inadimplencia_{dl_start}_{dl_end}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    st.dataframe(df_all, use_container_width=True, hide_index=True, height=400)
