"""
💬 Módulo Feedback — Sugestões, Dúvidas e Bug Reports
"""

import streamlit as st
from datetime import datetime


def render(lang: str):
    from utils.i18n import t

    if st.button(t("back_to_hub", lang), key="back_feedback"):
        st.session_state.current_page = "hub"
        st.rerun()

    st.markdown(
        "<h1 style='font-size:24px; font-weight:700;'>💬 "
        + ("Sugestões e Feedback" if lang == "pt" else "Suggestions & Feedback")
        + "</h1>"
        "<p style='color:#94A3B8; font-size:13px;'>"
        + (
            "Encontrou um bug, tem uma ideia ou quer tirar uma dúvida? Envie aqui."
            if lang == "pt"
            else "Found a bug, have an idea or a question? Send it here."
        )
        + "</p>",
        unsafe_allow_html=True,
    )

    with st.form("form_feedback", clear_on_submit=True):
        col_n, col_e = st.columns(2)
        with col_n:
            nome = st.text_input(
                "Nome (opcional)" if lang == "pt" else "Name (optional)",
                placeholder="Ex.: Maria Silva",
            )
        with col_e:
            email = st.text_input(
                "E-mail (opcional)" if lang == "pt" else "Email (optional)",
                placeholder="Ex.: maria@email.com",
            )

        tipo_opts = (
            ["💡 Sugestão", "❓ Dúvida", "🐛 Bug", "⭐ Elogio"]
            if lang == "pt"
            else ["💡 Suggestion", "❓ Question", "🐛 Bug", "⭐ Praise"]
        )
        tipo = st.selectbox("Tipo" if lang == "pt" else "Type", options=tipo_opts)

        msg = st.text_area(
            "Mensagem" if lang == "pt" else "Message",
            height=150,
            placeholder=(
                "Descreva sua sugestão, dúvida ou problema..."
                if lang == "pt"
                else "Describe your suggestion, question or issue..."
            ),
        )

        enviado = st.form_submit_button(
            "📤 Enviar" if lang == "pt" else "📤 Send",
            use_container_width=True,
        )

    if enviado:
        if not msg.strip():
            st.warning(
                "Por favor, escreva uma mensagem." if lang == "pt"
                else "Please write a message."
            )
        else:
            corpo = (
                f"📨 {tipo}\n"
                f"👤 {nome or 'Anônimo'}\n"
                f"📧 {email or '—'}\n"
                f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                f"{msg}"
            )

            sucesso = False
            push_token = st.secrets.get("PUSHOVER_API_TOKEN", "")
            push_user = st.secrets.get("PUSHOVER_USER_KEY", "")

            if push_token and push_user:
                try:
                    import requests
                    resp = requests.post(
                        "https://api.pushover.net/1/messages.json",
                        data={
                            "token": push_token,
                            "user": push_user,
                            "title": f"[Lab BCB] {tipo}",
                            "message": corpo,
                            "priority": 0,
                        },
                        timeout=10,
                    )
                    sucesso = resp.status_code == 200
                except Exception:
                    sucesso = False

            if sucesso:
                st.success(
                    "✅ Enviado com sucesso!" if lang == "pt"
                    else "✅ Sent successfully!"
                )
            else:
                st.info(
                    "📝 Mensagem registrada. (Configure PUSHOVER_API_TOKEN e "
                    "PUSHOVER_USER_KEY em st.secrets para notificações.)"
                    if lang == "pt"
                    else "📝 Recorded. (Set PUSHOVER keys in st.secrets for notifications.)"
                )
