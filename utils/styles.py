"""
Estilos CSS customizados para o Laboratório de Dados Públicos.
"""


def get_custom_css() -> str:
    """Retorna o CSS customizado para injetar via st.markdown."""
    return """
    <style>
    /* ===== Imports ===== */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

    /* ===== Variables ===== */
    :root {
        --accent-cyan: #22D3EE;
        --accent-emerald: #34D399;
        --accent-amber: #FBBF24;
        --accent-rose: #FB7185;
        --accent-violet: #A78BFA;
        --bg-card: #1A2332;
        --bg-card-hover: #1F2B3E;
        --border-subtle: rgba(148, 163, 184, 0.1);
        --text-muted: #64748B;
    }

    /* ===== Global ===== */
    .stApp {
        font-family: 'DM Sans', sans-serif !important;
    }

    /* Hide default Streamlit elements */
    #MainMenu, footer, header {visibility: hidden;}

    /* ===== Top Bar ===== */
    .top-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid var(--border-subtle);
        margin-bottom: 20px;
    }

    .top-bar-logo {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .top-bar-icon {
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-emerald));
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Space Mono', monospace;
        font-weight: 700;
        font-size: 15px;
        color: #0B1120;
    }

    .top-bar-title {
        font-weight: 600;
        font-size: 16px;
        color: #F1F5F9;
        letter-spacing: -0.02em;
    }

    .top-bar-subtitle {
        font-size: 12px;
        color: var(--text-muted);
        font-family: 'Space Mono', monospace;
    }

    /* ===== Badge ===== */
    .api-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 16px;
        border-radius: 20px;
        border: 1px solid rgba(34, 211, 238, 0.3);
        background: rgba(34, 211, 238, 0.05);
        font-family: 'Space Mono', monospace;
        font-size: 12px;
        color: var(--accent-cyan);
        margin-bottom: 16px;
    }

    .api-badge::before {
        content: '';
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--accent-emerald);
        animation: pulse-dot 2s ease-in-out infinite;
    }

    @keyframes pulse-dot {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    /* ===== Hub Title ===== */
    .hub-title {
        font-size: 44px;
        font-weight: 700;
        letter-spacing: -0.03em;
        line-height: 1.1;
        margin-bottom: 12px;
        background: linear-gradient(135deg, #F1F5F9 0%, #94A3B8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hub-desc {
        font-size: 16px;
        color: #94A3B8;
        max-width: 600px;
        line-height: 1.6;
        margin: 0 auto 40px;
        text-align: center;
    }

    /* ===== Module Cards ===== */
    .module-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 28px 24px;
        cursor: pointer;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        height: 100%;
    }

    .module-card:hover {
        background: var(--bg-card-hover);
        transform: translateY(-4px);
    }

    .module-card-cyan:hover    { border-color: var(--accent-cyan);    box-shadow: 0 0 20px rgba(34,211,238,0.15); }
    .module-card-emerald:hover { border-color: var(--accent-emerald); box-shadow: 0 0 20px rgba(52,211,153,0.15); }
    .module-card-amber:hover   { border-color: var(--accent-amber);   box-shadow: 0 0 20px rgba(251,191,36,0.15); }
    .module-card-rose:hover    { border-color: var(--accent-rose);    box-shadow: 0 0 20px rgba(251,113,133,0.15); }
    .module-card-violet:hover  { border-color: var(--accent-violet);  box-shadow: 0 0 20px rgba(167,139,250,0.15); }

    .module-card .icon {
        font-size: 28px;
        margin-bottom: 16px;
    }

    .module-card .title {
        font-size: 17px;
        font-weight: 600;
        color: #F1F5F9;
        margin-bottom: 8px;
        letter-spacing: -0.01em;
    }

    .module-card .desc {
        font-size: 13px;
        color: var(--text-muted);
        line-height: 1.5;
    }

    .module-tag {
        display: inline-block;
        margin-top: 14px;
        padding: 3px 10px;
        border-radius: 6px;
        font-family: 'Space Mono', monospace;
        font-size: 10px;
        font-weight: 700;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
    }

    .tag-active  { color: var(--accent-cyan); }
    .tag-soon    { color: var(--text-muted); }

    .module-card.disabled {
        opacity: 0.4;
        pointer-events: none;
    }

    /* ===== KPI Cards ===== */
    .kpi-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 20px;
        position: relative;
        overflow: hidden;
    }

    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
    }

    .kpi-cyan::before    { background: var(--accent-cyan); }
    .kpi-emerald::before { background: var(--accent-emerald); }
    .kpi-amber::before   { background: var(--accent-amber); }
    .kpi-rose::before    { background: var(--accent-rose); }

    .kpi-label {
        font-size: 12px;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.04em;
        font-family: 'Space Mono', monospace;
        margin-bottom: 6px;
    }

    .kpi-value {
        font-size: 26px;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    .kpi-value-cyan    { color: var(--accent-cyan); }
    .kpi-value-emerald { color: var(--accent-emerald); }
    .kpi-value-amber   { color: var(--accent-amber); }
    .kpi-value-rose    { color: var(--accent-rose); }

    .kpi-sub {
        font-size: 11px;
        color: var(--text-muted);
        margin-top: 2px;
    }

    /* ===== Section titles ===== */
    .section-title {
        font-size: 15px;
        font-weight: 600;
        color: #F1F5F9;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* ===== Comparison ===== */
    .comp-item {
        text-align: center;
        padding: 18px;
        border-radius: 10px;
        background: rgba(255,255,255,0.02);
        border: 1px solid var(--border-subtle);
    }

    .comp-label {
        font-size: 11px;
        color: var(--text-muted);
        text-transform: uppercase;
        font-family: 'Space Mono', monospace;
        margin-bottom: 8px;
    }

    .comp-val-a { color: var(--accent-cyan); font-size: 18px; font-weight: 700; }
    .comp-val-b { color: var(--accent-violet); font-size: 18px; font-weight: 700; }

    .comp-delta-pos { color: var(--accent-emerald); font-size: 12px; font-family: 'Space Mono', monospace; }
    .comp-delta-neg { color: var(--accent-rose); font-size: 12px; font-family: 'Space Mono', monospace; }

    /* ===== Footer ===== */
    .footer {
        text-align: center;
        padding: 30px 0;
        font-size: 12px;
        color: var(--text-muted);
        font-family: 'Space Mono', monospace;
        border-top: 1px solid var(--border-subtle);
        margin-top: 40px;
    }

    .footer a {
        color: var(--accent-cyan);
        text-decoration: none;
    }

    /* ===== Streamlit overrides ===== */
    .stButton > button {
        font-family: 'DM Sans', sans-serif !important;
    }

    div[data-testid="stExpander"] {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
    }

    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    </style>
    """
