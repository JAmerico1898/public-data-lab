"""
🏠 Laboratório de Dados Públicos — Hub Central
================================================
Página principal com acesso aos módulos de consulta
às APIs de dados abertos do Banco Central do Brasil.

Para executar:
    pip install -r requirements.txt
    streamlit run app.py
"""

import streamlit as st
from utils.i18n import t
from utils.styles import get_custom_css
from utils.helpers import render_module_card


# =============================================================================
# Page config
# =============================================================================
st.set_page_config(
    page_title="Laboratório de Dados Públicos",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# =============================================================================
# Session state initialization
# =============================================================================
if "lang" not in st.session_state:
    st.session_state.lang = "pt"

if "current_page" not in st.session_state:
    st.session_state.current_page = "hub"

lang = st.session_state.lang


# =============================================================================
# Navigation helper
# =============================================================================
def go_to(page: str):
    """Navega para uma página específica."""
    st.session_state.current_page = page


# =============================================================================
# Top Bar
# =============================================================================
col_logo, col_lang = st.columns([8, 2])

with col_logo:
    st.markdown(
        f"""
        <div class="top-bar-logo">
            <div class="top-bar-icon">LDP</div>
            <div>
                <div class="top-bar-title">{t("app_title", lang)}</div>
                <div class="top-bar-subtitle">{t("app_subtitle", lang)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_lang:
    lang_options = {"Português 🇧🇷": "pt", "English 🇺🇸": "en"}
    selected_lang = st.selectbox(
        t("language", lang),
        options=list(lang_options.keys()),
        index=0 if lang == "pt" else 1,
        label_visibility="collapsed",
    )
    new_lang = lang_options[selected_lang]
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

st.markdown("<hr style='border-color: rgba(148,163,184,0.1); margin: 0 0 20px;'>", unsafe_allow_html=True)

# =============================================================================
# Router — decide qual página exibir
# =============================================================================
if st.session_state.current_page == "spi":
    # Importa e executa o módulo SPI
    from pages import modulo_spi
    modulo_spi.render(lang)

elif st.session_state.current_page == "sgs":
    # Importa e executa o módulo SGS
    from pages import modulo_sgs
    modulo_sgs.render(lang)

elif st.session_state.current_page == "exp":
    # Importa e executa o módulo Expectativas
    from pages import modulo_exp
    modulo_exp.render(lang)

elif st.session_state.current_page == "ifdata":
    # Importa e executa o módulo IF.Data
    from pages import modulo_ifdata
    modulo_ifdata.render(lang)

elif st.session_state.current_page == "taxas":
    # Importa e executa o módulo Taxas de Juros
    from pages import modulo_taxas
    modulo_taxas.render(lang)

elif st.session_state.current_page == "inad":
    # Importa e executa o módulo Inadimplência
    from pages import modulo_inad
    modulo_inad.render(lang)

elif st.session_state.current_page == "feedback":
    from pages import modulo_feedback
    modulo_feedback.render(lang)

else:
    # =========================================================================
    # HUB — Página principal
    # =========================================================================

    # Hero
    st.markdown(
        f"""
        <div style="display:flex; flex-direction:column; align-items:center; padding: 40px 0 10px;">
            <div class="api-badge">{t("badge_api", lang)}</div>
            <h1 class="hub-title">{t("app_title", lang)}</h1>
            <p class="hub-desc">{t("app_description", lang)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Module cards — Row 1 (3 cards)
    st.markdown(
        f"<p style='text-align:center; color:#64748B; margin-bottom:24px;'>"
        f"{t('select_module', lang)}</p>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown(
            render_module_card(
                "⚡",
                t("spi_title", lang).replace("⚡ ", ""),
                t("spi_desc", lang),
                "cyan",
                t("active", lang),
                active=True,
            ),
            unsafe_allow_html=True,
        )
        if st.button(
            t("spi_title", lang),
            key="btn_spi",
            use_container_width=True,
            type="primary",
        ):
            go_to("spi")
            st.rerun()

    with col2:
        st.markdown(
            render_module_card(
                "📈",
                t("sgs_title", lang).replace("📈 ", ""),
                t("sgs_desc", lang),
                "emerald",
                t("active", lang),
                active=True,
            ),
            unsafe_allow_html=True,
        )
        if st.button(
            t("sgs_title", lang),
            key="btn_sgs",
            use_container_width=True,
            type="primary",
        ):
            go_to("sgs")
            st.rerun()

    with col3:
        st.markdown(
            render_module_card(
                "🔮",
                t("exp_title", lang).replace("🔮 ", ""),
                t("exp_desc", lang),
                "amber",
                t("active", lang),
                active=True,
            ),
            unsafe_allow_html=True,
        )
        if st.button(
            t("exp_title", lang),
            key="btn_exp",
            use_container_width=True,
            type="primary",
        ):
            go_to("exp")
            st.rerun()

    # Module cards — Row 2 (3 cards)
    col4, col5, col6 = st.columns(3, gap="medium")

    with col4:
        st.markdown(
            render_module_card(
                "🏦",
                t("ifdata_title", lang).replace("🏦 ", ""),
                t("ifdata_desc", lang),
                "rose",
                t("active", lang),
                active=True,
            ),
            unsafe_allow_html=True,
        )
        if st.button(
            t("ifdata_title", lang),
            key="btn_ifdata",
            use_container_width=True,
            type="primary",
        ):
            go_to("ifdata")
            st.rerun()

    with col5:
        st.markdown(
            render_module_card(
                "💹",
                t("taxas_title", lang).replace("💹 ", ""),
                t("taxas_desc", lang),
                "violet",
                t("active", lang),
                active=True,
            ),
            unsafe_allow_html=True,
        )
        if st.button(
            t("taxas_title", lang),
            key="btn_taxas",
            use_container_width=True,
            type="primary",
        ):
            go_to("taxas")
            st.rerun()

    with col6:
        st.markdown(
            render_module_card(
                "📍",
                "Inadimplência" if lang == "pt" else "NPL",
                (
                    "Inadimplência de operações de crédito por região e estado — modalidades PF e PJ."
                    if lang == "pt"
                    else "Non-performing loans by region and state. Households and Enterprises"
                ),
                "cyan",
                t("active", lang),
                active=True,
            ),
            unsafe_allow_html=True,
        )
        if st.button(
            "📍 Inadimplência" if lang == "pt" else "📍 NPL",
            key="btn_inad",
            use_container_width=True,
            type="primary",
        ):
            go_to("inad")
            st.rerun()

    # Feedback button — centered, smaller
    _, col_fb, _ = st.columns([2, 1, 2])
    with col_fb:
        if st.button(
            "💬 Sugestões e Feedback" if lang == "pt" else "💬 Suggestions & Feedback",
            key="btn_feedback",
            use_container_width=True,
        ):
            go_to("feedback")
            st.rerun()

    # Footer
    st.markdown(
        f"""
        <div class="footer">
            {t("source", lang)}:
            <a href="https://dadosabertos.bcb.gov.br/" target="_blank">
                dadosabertos.bcb.gov.br
            </a>
            · {t("built_with", lang)}
            <br>{t("author", lang)}
        </div>
        """,
        unsafe_allow_html=True,
    )
