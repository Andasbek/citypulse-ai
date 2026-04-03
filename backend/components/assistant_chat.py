import streamlit as st


QUICK_QUESTIONS = [
    "Что умеет CityPulse AI?",
    "Какое сейчас состояние города?",
    "Где сейчас опасно гулять?",
    "Какие планы развития платформы?",
    "Стоит ли сейчас идти на прогулку?",
]


def render_assistant_chat(ask_fn, city_context: dict):
    """Render the AI assistant chat interface."""

    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:10px; margin:8px 0 18px;">
            <span style="font-size:1.4rem;">💬</span>
            <span style="font-size:1.2rem; font-weight:700; color:#2d3436;">
                AI-ассистент CityPulse
            </span>
        </div>
        <div style="color:#636e72; font-size:0.9rem; margin-bottom:16px;">
            Задайте вопрос о состоянии города, возможностях платформы
            или получите рекомендации по прогулкам и маршрутам.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Quick question buttons
    st.markdown(
        '<div style="color:#888; font-size:0.8rem; margin-bottom:8px;">Быстрые вопросы:</div>',
        unsafe_allow_html=True,
    )
    cols = st.columns(len(QUICK_QUESTIONS))
    for i, (col, q) in enumerate(zip(cols, QUICK_QUESTIONS)):
        with col:
            if st.button(q, key=f"quick_q_{i}", use_container_width=True):
                st.session_state["assistant_question"] = q

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # Input
    question = st.text_input(
        "Ваш вопрос:",
        value=st.session_state.get("assistant_question", ""),
        placeholder="Например: Где сейчас лучше гулять?",
        key="assistant_input",
    )

    if st.button("🤖 Спросить AI", type="primary", use_container_width=False):
        if question.strip():
            with st.spinner("AI думает..."):
                answer = ask_fn(question.strip(), city_context)
            st.session_state["assistant_answer"] = answer
            st.session_state["assistant_last_q"] = question.strip()

    # Display answer
    if "assistant_answer" in st.session_state:
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
                        color: #dfe6e9; padding: 20px 24px; border-radius: 14px;
                        margin: 16px 0; box-shadow: 0 4px 20px rgba(0,0,0,0.12);
                        border: 1px solid rgba(255,255,255,0.06);
                        line-height: 1.7; font-size: 0.93rem;">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;
                            padding-bottom:10px; border-bottom:1px solid rgba(255,255,255,0.08);">
                    <span style="font-size:1.1rem;">🤖</span>
                    <span style="color:#a29bfe; font-weight:600; font-size:0.85rem;">
                        CityPulse AI
                    </span>
                    <span style="color:rgba(255,255,255,0.3); font-size:0.8rem; margin-left:auto;">
                        {st.session_state.get('assistant_last_q', '')}
                    </span>
                </div>
                <div style="white-space:pre-wrap;">{st.session_state['assistant_answer']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
