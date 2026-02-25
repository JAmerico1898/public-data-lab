"""
Funções auxiliares para formatação de valores e componentes reutilizáveis.
"""

import streamlit as st
import pandas as pd
from io import BytesIO


# =============================================================================
# Formatação de números
# =============================================================================

def fmt_number(value: float, decimals: int = 0) -> str:
    """
    Formata um número grande com sufixos (M, B, T) em notação brasileira.
    Exemplos: 1_234_567 → '1,23M'  |  1_234_567_890 → '1,23B'
    """
    if pd.isna(value):
        return "—"

    abs_val = abs(value)

    if abs_val >= 1e12:
        formatted = f"{value / 1e12:,.2f}T"
    elif abs_val >= 1e9:
        formatted = f"{value / 1e9:,.2f}B"
    elif abs_val >= 1e6:
        formatted = f"{value / 1e6:,.2f}M"
    elif abs_val >= 1e3:
        formatted = f"{value / 1e3:,.1f}K"
    else:
        formatted = f"{value:,.{decimals}f}"

    # Converte para notação brasileira (. → temp, , → ., temp → ,)
    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")

    return formatted


def fmt_brl(value: float) -> str:
    """Formata valor monetário brasileiro. Ex: 37621450000 → 'R$ 37,62B'"""
    if pd.isna(value):
        return "—"
    return f"R$ {fmt_number(value)}"


def fmt_pct(value: float) -> str:
    """Formata percentual. Ex: 0.1234 → '+12,34%'"""
    if pd.isna(value):
        return "—"
    sign = "+" if value > 0 else ""
    return f"{sign}{value * 100:,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")


# =============================================================================
# Componentes HTML reutilizáveis
# =============================================================================

def render_kpi_card(label: str, value: str, sub: str, color: str) -> str:
    """Gera o HTML de um card KPI."""
    return f"""
    <div class="kpi-card kpi-{color}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value kpi-value-{color}">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """


def render_module_card(
    icon: str,
    title: str,
    desc: str,
    color: str,
    tag: str,
    active: bool = False,
) -> str:
    """Gera o HTML de um card de módulo no hub."""
    disabled = "" if active else "disabled"
    tag_class = "tag-active" if active else "tag-soon"

    return f"""
    <div class="module-card module-card-{color} {disabled}">
        <div class="icon">{icon}</div>
        <div class="title">{title}</div>
        <div class="desc">{desc}</div>
        <div class="module-tag {tag_class}">{tag}</div>
    </div>
    """


def render_comparison_item(
    label: str, val_a: str, val_b: str, delta: float
) -> str:
    """Gera HTML de um item de comparação."""
    if pd.isna(delta):
        delta_html = '<span style="color:#64748B;">—</span>'
    else:
        delta_class = "comp-delta-pos" if delta >= 0 else "comp-delta-neg"
        arrow = "▲" if delta >= 0 else "▼"
        delta_html = f'<span class="{delta_class}">{arrow} {fmt_pct(delta)}</span>'

    return f"""
    <div class="comp-item">
        <div class="comp-label">{label}</div>
        <div style="display:flex; justify-content:center; gap:20px; margin-bottom:8px;">
            <span class="comp-val-a">{val_a}</span>
            <span class="comp-val-b">{val_b}</span>
        </div>
        {delta_html}
    </div>
    """


# =============================================================================
# Exportação de dados
# =============================================================================

def to_excel_bytes(df: pd.DataFrame) -> bytes:
    """Converte DataFrame para bytes XLSX."""
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Dados SPI")
    return buffer.getvalue()


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Converte DataFrame para bytes CSV (encoding UTF-8 BOM para Excel)."""
    return df.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")
