"""
🏦 Módulo IF.Data — Dados de Instituições Financeiras
=======================================================
Dados contábeis e regulatórios de IFs supervisionadas pelo BCB.
Relatórios: Resumo (1) e Ativo (2).
Filtro: Segmentos 1-4, sufixo "– PRUDENCIAL", TipoInstituicao=1.

Sub-módulos:
1. Ranking: Top/Bottom 10 por variável
2. Banco Individual: todas as variáveis + posição no ranking
3. Download: dados brutos para pesquisa (limite 24 meses)
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
from utils.i18n import t
from utils.helpers import to_excel_bytes, to_csv_bytes


# =============================================================================
# Variables config
# =============================================================================

# Variables from Resumo (Relatorio=1)
RESUMO_VARS = [
    "Ativo Total",
    "Captações",
    "Patrimônio Líquido",
    "Lucro Líquido",
    "Índice de Basileia",
]

# Variables from Ativo (Relatorio=2)
# Nomes reais contêm \n — mapeamos para nomes limpos
ATIVO_COL_OP_CREDITO = "Operações de Crédito \n(e)"
ATIVO_COL_BRUTO = "Valor Contábil Bruto \n(e1)"
ATIVO_COL_PERDA = "Perda Esperada \n(e2)"

# All user-facing variables
ALL_VARIABLES = [
    "Ativo Total",
    "Captações",
    "Patrimônio Líquido",
    "Lucro Líquido",
    "Índice de Basileia",
    "Operações de Crédito",
    "Perda Esperada de Crédito",
]

# Ranking sort: True = desc (larger is "Maiores"), except Perda Esperada
RANKING_DESC = {
    "Ativo Total": True,
    "Captações": True,
    "Patrimônio Líquido": True,
    "Lucro Líquido": True,
    "Índice de Basileia": True,
    "Operações de Crédito": True,
    "Perda Esperada de Crédito": False,  # lower is "Maiores" (better)
}

UNITS = {
    "Ativo Total": "R$",
    "Captações": "R$",
    "Patrimônio Líquido": "R$",
    "Lucro Líquido": "R$",
    "Índice de Basileia": "%",
    "Operações de Crédito": "R$",
    "Perda Esperada de Crédito": "%",
}


# =============================================================================
# Data fetching
# =============================================================================

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_cadastro(anomes: int) -> pd.DataFrame:
    """Fetch IfDataCadastro: list of institutions with segment info."""
    from bcb.odata import IFDATA
    ifdata = IFDATA()
    ep = ifdata.get_endpoint("IfDataCadastro")
    try:
        df = ep.get(AnoMes=anomes)
        return df if df is not None else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_valores(anomes: int, tipo: int, relatorio: int) -> pd.DataFrame:
    """Fetch IfDataValores for a given period, type, and report."""
    from bcb.odata import IFDATA
    ifdata = IFDATA()
    ep = ifdata.get_endpoint("IfDataValores")
    try:
        df = ep.get(AnoMes=anomes, TipoInstituicao=tipo, Relatorio=relatorio)
        return df if df is not None else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def find_latest_quarter() -> int:
    """Tenta trimestres recentes até encontrar um com dados."""
    from bcb.odata import IFDATA
    ifdata = IFDATA()
    ep = ifdata.get_endpoint("IfDataValores")

    today = date.today()
    y, m = today.year, today.month
    # Gerar últimos 6 trimestres candidatos
    candidates = []
    for _ in range(6):
        q_month = ((m - 1) // 3) * 3 + 3
        candidates.append(y * 100 + q_month)
        m -= 3
        if m <= 0:
            m += 12
            y -= 1

    for anomes in candidates:
        try:
            df = ep.get(AnoMes=anomes, TipoInstituicao=1, Relatorio=1)
            if df is not None and not df.empty:
                return anomes
        except Exception:
            continue

    return candidates[-1]

def filter_institutions(df_cadastro: pd.DataFrame) -> pd.DataFrame:
    """Filter institutions: segments 1-4, PRUDENCIAL suffix."""
    df = df_cadastro.copy()
    # Filter segments S1-S4 (column Sr has values like "S1", "S2", "S3", "S4")
    df = df[df["Sr"].isin(["S1", "S2", "S3", "S4"])]
    # Filter PRUDENCIAL
    df = df[df["NomeInstituicao"].str.contains("PRUDENCIAL", case=False, na=False)]
    return df[["CodInst", "NomeInstituicao", "Sr"]].drop_duplicates(subset=["CodInst"])


def build_ranking_data(
    df_resumo: pd.DataFrame,
    df_ativo: pd.DataFrame,
    df_cadastro_filtered: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build a unified DataFrame with all variables per institution.
    Merges Resumo + Ativo data, computes Perda Esperada, joins with names.
    """
    valid_codes = set(df_cadastro_filtered["CodInst"].tolist())

    # --- Process Resumo ---
    records = []
    if not df_resumo.empty:
        for _, row in df_resumo.iterrows():
            if row.get("CodInst") in valid_codes:
                var_name = str(row.get("NomeColuna", "")).strip()
                if var_name in RESUMO_VARS:
                    val = pd.to_numeric(row.get("Saldo"), errors="coerce")
                    # Índice de Basileia vem como proporção (0.12 = 12%)
                    if var_name == "Índice de Basileia" and pd.notna(val):
                        val = val * 100
                    records.append({
                        "CodInst": row["CodInst"],
                        "Variable": var_name,
                        "Value": val,
                    })

    # --- Process Ativo ---
    ativo_data = {}  # CodInst -> {col_name: value}
    target_cols = {ATIVO_COL_OP_CREDITO, ATIVO_COL_BRUTO, ATIVO_COL_PERDA}
    if not df_ativo.empty:
        for _, row in df_ativo.iterrows():
            if row.get("CodInst") in valid_codes:
                var_name = str(row.get("NomeColuna", ""))
                if var_name in target_cols:
                    cod = row["CodInst"]
                    if cod not in ativo_data:
                        ativo_data[cod] = {}
                    ativo_data[cod][var_name] = pd.to_numeric(row.get("Saldo"), errors="coerce")

    # Add Op. Crédito + compute Perda Esperada
    for cod, vals in ativo_data.items():
        op_cred = vals.get(ATIVO_COL_OP_CREDITO)
        bruto = vals.get(ATIVO_COL_BRUTO)
        perda = vals.get(ATIVO_COL_PERDA)

        if pd.notna(op_cred):
            records.append({
                "CodInst": cod,
                "Variable": "Operações de Crédito",
                "Value": op_cred,
            })

        if pd.notna(bruto) and pd.notna(perda) and bruto != 0:
            pec = round(abs(perda) / bruto * 100, 2)
            records.append({
                "CodInst": cod,
                "Variable": "Perda Esperada de Crédito",
                "Value": pec,
            })

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)

    # Pivot: one row per institution, one column per variable
    df_pivot = df.pivot_table(index="CodInst", columns="Variable", values="Value", aggfunc="first")
    df_pivot = df_pivot.reset_index()

    # Merge with institution names
    df_ranking = df_pivot.merge(
        df_cadastro_filtered[["CodInst", "NomeInstituicao"]],
        on="CodInst",
        how="left",
    )

    # Clean institution name (remove " – PRUDENCIAL" for display)
    df_ranking["NomeInstituicao"] = (
        df_ranking["NomeInstituicao"]
        .str.replace(r"\s*[-–]\s*PRUDENCIAL", "", regex=True)
        .str.strip()
    )

    return df_ranking


def fmt_value(val, var_name: str) -> str:
    if pd.isna(val):
        return "—"
    if var_name == "Perda Esperada de Crédito":
        return f"{val:,.2f}%"
    if var_name == "Índice de Basileia":
        return f"{val:,.2f}"
    elif var_name in ("Ativo Total", "Captações", "Patrimônio Líquido",
                      "Lucro Líquido", "Operações de Crédito"):
        if abs(val) >= 1e9:
            return f"{val/1e9:,.1f} bi"
        elif abs(val) >= 1e6:
            return f"{val/1e6:,.1f} mi"
        else:
            return f"{val:,.0f}"
    return f"{val:,.2f}"


# =============================================================================
# Styled HTML table helper
# =============================================================================

def render_ranking_table(df: pd.DataFrame, var: str, lang: str) -> str:
    """Render a styled HTML ranking table."""
    header = f"""
    <tr>
        <th style="width:40px;">{t("ifd_rank_col", lang)}</th>
        <th>{t("ifd_institution", lang)}</th>
        <th style="text-align:right;">{var}</th>
    </tr>"""

    rows = ""
    for i, (_, row) in enumerate(df.iterrows()):
        rank = i + 1
        name = row["NomeInstituicao"]
        val = fmt_value(row[var], var)
        rows += f"""
        <tr>
            <td style="color:#22D3EE; font-weight:700; font-family:Space Mono,monospace;">{rank}</td>
            <td>{name}</td>
            <td style="text-align:right; font-family:Space Mono,monospace;">{val}</td>
        </tr>"""

    return f"""
    <table class="ifd-table">
        <thead>{header}</thead>
        <tbody>{rows}</tbody>
    </table>"""


TABLE_CSS = """
<style>
    .ifd-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        font-family: 'DM Sans', sans-serif;
    }
    .ifd-table th {
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
    .ifd-table td {
        padding: 7px 10px;
        color: #94A3B8;
        border-bottom: 1px solid rgba(148,163,184,0.06);
    }
    .ifd-table tbody tr:hover {
        background: rgba(34,211,238,0.04);
    }
</style>
"""


# =============================================================================
# Main render function
# =============================================================================

def render(lang: str):
    """Renders the IF.Data module page."""

    # ----- Back button -----
    if st.button(t("back_to_hub", lang), key="back_ifd"):
        st.session_state.current_page = "hub"
        for k in list(st.session_state.keys()):
            if k.startswith("ifd_"):
                del st.session_state[k]
        st.rerun()

    # ----- Header -----
    st.markdown(
        f"""
        <div style="margin-bottom: 24px;">
            <h1 style="font-size:28px; font-weight:700; letter-spacing:-0.02em;">
                {t("ifd_page_title", lang)}
            </h1>
            <p style="color:#94A3B8; font-size:14px; margin-top:4px;">
                {t("ifd_page_desc", lang)}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Inject table CSS once
    st.markdown(TABLE_CSS, unsafe_allow_html=True)

    # =================================================================
    # TABS
    # =================================================================
    tab_ranking, tab_bank, tab_download = st.tabs([
        t("ifd_tab_ranking", lang),
        t("ifd_tab_bank", lang),
        t("ifd_tab_download", lang),
    ])

    # =================================================================
    # TAB 1: RANKING
    # =================================================================
    with tab_ranking:
        render_ranking_tab(lang)

    # =================================================================
    # TAB 2: BANCO INDIVIDUAL
    # =================================================================
    with tab_bank:
        render_bank_tab(lang)

    # =================================================================
    # TAB 3: DOWNLOAD
    # =================================================================
    with tab_download:
        render_download_tab(lang)

    # Footer
    st.markdown(
        f"""
        <div class="footer">
            {t("source", lang)}:
            <a href="https://dadosabertos.bcb.gov.br/" target="_blank">dadosabertos.bcb.gov.br</a>
            · IF.Data API
            · {t("built_with", lang)}
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# Tab: Ranking
# =============================================================================

def render_ranking_tab(lang: str):
    """Render the ranking sub-module."""

    selected_vars = st.multiselect(
        t("ifd_select_vars", lang),
        options=ALL_VARIABLES,
        default=ALL_VARIABLES,
        key="ifd_ranking_vars",
    )

    if not selected_vars:
        return

    query_btn = st.button(t("ifd_query", lang), key="query_ranking", type="primary")

    if not query_btn and "ifd_ranking_data" not in st.session_state:
        return

    if query_btn:
        with st.spinner(t("loading", lang)):
            data = _load_latest_data()
            if data is not None:
                st.session_state.ifd_ranking_data = data

    if "ifd_ranking_data" not in st.session_state:
        return

    df_ranking, anomes = st.session_state.ifd_ranking_data
    
    # Filtro de materialidade para ranking
    df_ranking = df_ranking.copy()
    if "Patrimônio Líquido" in df_ranking.columns:
        df_ranking = df_ranking[
            (df_ranking["Patrimônio Líquido"].fillna(0) > 100_000_000)
        ]
    if "Operações de Crédito" in df_ranking.columns:
        df_ranking = df_ranking[
            (df_ranking["Operações de Crédito"].fillna(0) > 200_000_000)
        ]
    if "Ativo Total" in df_ranking.columns:
        df_ranking = df_ranking[
            (df_ranking["Ativo Total"].fillna(0) > 1_000_000_000)
        ]

    if df_ranking.empty:
        st.warning(t("no_data", lang))
        return

    total_ifs = len(df_ranking)
    st.markdown(
        f"<div style='font-family:Space Mono,monospace; font-size:12px; color:#64748B; "
        f"margin-bottom:16px;'>"
        f"📅 {t('ifd_ref_date', lang)}: <strong style='color:#22D3EE;'>{anomes}</strong> · "
        f"{t('ifd_total_ifs', lang)}: <strong style='color:#22D3EE;'>{total_ifs}</strong>"
        f"</div>",
        unsafe_allow_html=True,
    )

    for var in selected_vars:
        if var not in df_ranking.columns:
            st.info(f"{var}: dados indisponíveis")
            continue

        df_var = df_ranking[["NomeInstituicao", var]].dropna(subset=[var]).copy()

        if df_var.empty:
            continue

        is_desc = RANKING_DESC.get(var, True)

        # "Maiores" side
        if is_desc:
            df_top = df_var.sort_values(var, ascending=False).head(10)
            df_bottom = df_var.sort_values(var, ascending=True).head(10)
            label_left = t("ifd_largest", lang)
            label_right = t("ifd_smallest", lang)
        else:
            # Perda Esperada: "Maiores" = ascending (lower is better)
            df_top = df_var.sort_values(var, ascending=True).head(10)
            df_bottom = df_var.sort_values(var, ascending=False).head(10)
            label_left = t("ifd_largest_pec", lang)
            label_right = t("ifd_smallest_pec", lang)

        unit = UNITS.get(var, "")

        st.markdown(
            f"<div style='font-size:16px; font-weight:600; margin:24px 0 8px;'>"
            f"{var} <span style='font-size:12px; color:#64748B;'>{unit}</span></div>",
            unsafe_allow_html=True,
        )

        col_left, col_right = st.columns(2, gap="medium")

        with col_left:
            st.markdown(
                f"<div style='font-size:13px; font-weight:600; color:#34D399; margin-bottom:6px;'>"
                f"▲ {label_left}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(render_ranking_table(df_top.reset_index(drop=True), var, lang), unsafe_allow_html=True)

        with col_right:
            st.markdown(
                f"<div style='font-size:13px; font-weight:600; color:#FB7185; margin-bottom:6px;'>"
                f"▼ {label_right}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(render_ranking_table(df_bottom.reset_index(drop=True), var, lang), unsafe_allow_html=True)

        st.markdown("<hr style='border-color:rgba(148,163,184,0.06); margin:8px 0;'>", unsafe_allow_html=True)


# =============================================================================
# Tab: Banco Individual
# =============================================================================

def render_bank_tab(lang: str):
    """Render the individual bank sub-module."""

    query_btn = st.button(t("ifd_query", lang), key="query_bank", type="primary")

    if query_btn:
        with st.spinner(t("loading", lang)):
            data = _load_latest_data()
            if data is not None:
                st.session_state.ifd_bank_data = data

    if "ifd_bank_data" not in st.session_state:
        if "ifd_ranking_data" in st.session_state:
            st.session_state.ifd_bank_data = st.session_state.ifd_ranking_data
        else:
            st.info(f"👆 {t('ifd_query', lang)}")
            return

    df_ranking, anomes = st.session_state.ifd_bank_data

    if df_ranking.empty:
        st.warning(t("no_data", lang))
        return

    total_ifs = len(df_ranking)

    # Bank selector
    bank_names = sorted(df_ranking["NomeInstituicao"].dropna().unique().tolist())
    selected_bank = st.selectbox(
        t("ifd_select_bank", lang),
        options=bank_names,
        key="ifd_bank_select",
    )

    if not selected_bank:
        return

    bank_row = df_ranking[df_ranking["NomeInstituicao"] == selected_bank]
    if bank_row.empty:
        st.warning(t("no_data", lang))
        return

    st.markdown(
        f"<div style='font-size:20px; font-weight:700; margin:16px 0 8px;'>"
        f"🏦 {selected_bank}</div>"
        f"<div style='font-family:Space Mono,monospace; font-size:12px; color:#64748B; "
        f"margin-bottom:16px;'>"
        f"📅 {t('ifd_ref_date', lang)}: {anomes}</div>",
        unsafe_allow_html=True,
    )

    # Build overview table
    header = f"""
    <tr>
        <th>{t("ifd_variable", lang)}</th>
        <th style="text-align:right;">{t("ifd_value", lang)}</th>
        <th style="text-align:center;">{t("ifd_position", lang)}</th>
    </tr>"""

    rows_html = ""
    for var in ALL_VARIABLES:
        if var not in df_ranking.columns:
            continue

        val = bank_row[var].iloc[0]
        val_fmt = fmt_value(val, var)

        # Compute ranking position
        if pd.notna(val):
            is_desc = RANKING_DESC.get(var, True)
            df_var = df_ranking[[var]].dropna()
            if is_desc:
                rank = int((df_var[var] > val).sum() + 1)
            else:
                rank = int((df_var[var] < val).sum() + 1)
            n = len(df_var)
            pos_str = f"{rank}º {t('ifd_of_ifs', lang, n=n)}"
        else:
            pos_str = "—"

        rows_html += f"""
        <tr>
            <td style="font-weight:600; color:#F1F5F9;">{var}</td>
            <td style="text-align:right; font-family:Space Mono,monospace;">{val_fmt}</td>
            <td style="text-align:center; font-family:Space Mono,monospace; color:#22D3EE;">{pos_str}</td>
        </tr>"""

    table_html = f"""
    <table class="ifd-table">
        <thead>{header}</thead>
        <tbody>{rows_html}</tbody>
    </table>"""

    st.markdown(table_html, unsafe_allow_html=True)


# =============================================================================
# Tab: Download
# =============================================================================

def render_download_tab(lang: str):
    """Render the data download sub-module."""

    st.markdown(
        f'<div class="section-title">{t("ifd_download_title", lang)}</div>',
        unsafe_allow_html=True,
    )
    st.caption(t("ifd_download_desc", lang))

    # Variable selection (all available)
    selected_vars = st.multiselect(
        t("ifd_select_vars", lang),
        options=ALL_VARIABLES,
        default=ALL_VARIABLES,
        key="ifd_dl_vars",
    )

    col_start, col_end = st.columns(2)

    with col_start:
        dl_start = st.number_input(
            t("ifd_download_start", lang),
            min_value=200003,
            max_value=209912,
            value=202303,
            step=3,
            key="ifd_dl_start",
        )

    with col_end:
        dl_end = st.number_input(
            t("ifd_download_end", lang),
            min_value=200003,
            max_value=209912,
            value=202412,
            step=3,
            key="ifd_dl_end",
        )

    # Validate 24-month limit
    start_y, start_m = divmod(int(dl_start), 100)
    end_y, end_m = divmod(int(dl_end), 100)

    if start_m not in (3, 6, 9, 12) or end_m not in (3, 6, 9, 12):
        st.warning("⚠️ Meses válidos: 03, 06, 09, 12 (dados trimestrais)")
        return

    months_diff = (end_y - start_y) * 12 + (end_m - start_m)
    if months_diff > 24:
        st.warning(t("ifd_download_warn_24m", lang))
        return
    if months_diff < 0:
        st.warning("⚠️ Data final deve ser posterior à data inicial.")
        return

    # Generate quarterly periods
    periods = []
    y, m = start_y, start_m
    while y * 100 + m <= end_y * 100 + end_m:
        periods.append(y * 100 + m)
        m += 3
        if m > 12:
            m = 3
            y += 1

    st.caption(f"Trimestres: {', '.join(str(p) for p in periods)} ({len(periods)} consultas)")

    dl_btn = st.button(t("ifd_download_btn", lang), key="ifd_dl_btn", type="primary")

    if not dl_btn:
        return

    # Fetch cadastro
    progress = st.progress(0, text=t("ifd_downloading", lang))

    try:
        df_cadastro = fetch_cadastro(int(dl_end))
        df_filtered = filter_institutions(df_cadastro)
    except Exception as e:
        st.error(t("api_error", lang))
        st.code(str(e))
        progress.empty()
        return

    all_frames = []
    total_steps = len(periods) * 2  # 2 reports per period
    step = 0

    for period in periods:
        for rel_code, rel_name in [(1, "Resumo"), (2, "Ativo")]:
            try:
                df = fetch_valores(anomes=period, tipo=1, relatorio=rel_code)
                if not df.empty:
                    df["AnoMes"] = period
                    df["Relatorio"] = rel_name
                    all_frames.append(df)
            except Exception:
                pass

            step += 1
            progress.progress(step / total_steps, text=f"{t('ifd_downloading', lang)} {period} ({rel_name})")

    progress.empty()

    if not all_frames:
        st.warning(t("no_data", lang))
        return

    df_all = pd.concat(all_frames, ignore_index=True)

    # Filter to valid institutions
    valid_codes = set(df_filtered["CodInst"].tolist())
    df_all = df_all[df_all["CodInst"].isin(valid_codes)]

    # Merge names
    df_all = df_all.merge(
        df_filtered[["CodInst", "NomeInstituicao"]],
        on="CodInst",
        how="left",
    )

    st.success(f"✅ {len(df_all):,} registros baixados")
    st.caption(t("data_showing", lang, n=len(df_all)))

    dl1, dl2, _ = st.columns([1, 1, 4])
    with dl1:
        st.download_button(
            t("download_csv", lang),
            data=to_csv_bytes(df_all),
            file_name=f"ifdata_{dl_start}_{dl_end}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with dl2:
        st.download_button(
            t("download_xlsx", lang),
            data=to_excel_bytes(df_all),
            file_name=f"ifdata_{dl_start}_{dl_end}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    st.dataframe(df_all, use_container_width=True, hide_index=True, height=400)


# =============================================================================
# Helper: load latest data (shared between Ranking and Bank tabs)
# =============================================================================

def _load_latest_data():
    """
    Fetch latest available data: cadastro + resumo + ativo.
    Returns (df_ranking, anomes) or None on error.
    """
    try:
        # Get available periods
        anomes = find_latest_quarter()

        # Fetch cadastro and filter
        df_cadastro = fetch_cadastro(anomes)
        df_filtered = filter_institutions(df_cadastro)

        if df_filtered.empty:
            st.error("Nenhuma IF encontrada nos segmentos 1-4.")
            return None

        # Fetch Resumo and Ativo
        df_resumo = fetch_valores(anomes=anomes, tipo=1, relatorio=1)
        df_ativo = fetch_valores(anomes=anomes, tipo=1, relatorio=2)

        # Build merged data
        df_ranking = build_ranking_data(df_resumo, df_ativo, df_filtered)

        return (df_ranking, anomes)

    except Exception as e:
        st.error(t("api_error", "pt"))
        st.code(str(e))
        return None
