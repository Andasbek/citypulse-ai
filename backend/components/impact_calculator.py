import streamlit as st

from services.user_impact_service import FUEL_TYPES, ENGINE_VOLUMES


def render_impact_calculator(calculate_fn, explain_fn, city_context: dict):
    """Render the personal eco impact calculator."""

    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:10px; margin:8px 0 18px;">
            <span style="font-size:1.4rem;">🚗</span>
            <span style="font-size:1.2rem; font-weight:700; color:#2d3436;">
                Личный экологический калькулятор
            </span>
        </div>
        <div style="color:#636e72; font-size:0.9rem; margin-bottom:16px;">
            Рассчитайте ваш Air Impact Score — оценочный индекс вклада
            вашего автомобиля в загрязнение воздуха города.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        fuel_type = st.selectbox("Тип топлива", FUEL_TYPES, key="fuel_type")
    with col2:
        engine_vol = st.select_slider(
            "Объем двигателя (л)",
            options=ENGINE_VOLUMES,
            value=2.0,
            key="engine_vol",
        )
    with col3:
        daily_km = st.number_input(
            "Пробег в день (км)",
            min_value=0,
            max_value=500,
            value=35,
            step=5,
            key="daily_km",
        )

    if st.button("📊 Рассчитать Air Impact", type="primary"):
        result = calculate_fn(fuel_type, engine_vol, daily_km)
        st.session_state["impact_result"] = result

        with st.spinner("AI анализирует ваш результат..."):
            explanation = explain_fn(result, city_context)
        st.session_state["impact_explanation"] = explanation

    if "impact_result" in st.session_state:
        result = st.session_state["impact_result"]
        _render_impact_result(result)

        if "impact_explanation" in st.session_state:
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
                            color: #dfe6e9; padding: 18px 22px; border-radius: 14px;
                            margin: 16px 0; box-shadow: 0 4px 16px rgba(0,0,0,0.12);
                            border: 1px solid rgba(255,255,255,0.06);
                            line-height: 1.7; font-size: 0.92rem;">
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:10px;">
                        <span style="font-size:1rem;">🤖</span>
                        <span style="color:#a29bfe; font-weight:600; font-size:0.85rem;">
                            AI-интерпретация
                        </span>
                    </div>
                    <div style="white-space:pre-wrap;">{st.session_state['impact_explanation']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_impact_result(result: dict):
    score = result["impact_score"]
    level = result["level"]
    comparison = result["comparison"]

    if level == "low":
        score_color, score_label = "#2ecc71", "Низкий"
    elif level == "medium":
        score_color, score_label = "#f39c12", "Умеренный"
    else:
        score_color, score_label = "#e74c3c", "Высокий"

    comp_text = f"+{comparison}%" if comparison > 0 else f"{comparison}%"
    comp_color = "#e74c3c" if comparison > 0 else "#2ecc71"

    st.markdown(
        f"""
        <div style="background:#fff; border-radius:14px; padding:24px;
                    box-shadow:0 2px 12px rgba(0,0,0,0.06); margin:16px 0;
                    border-top:4px solid {score_color};">
            <div style="text-align:center; margin-bottom:18px;">
                <div style="font-size:0.8rem; color:#888; text-transform:uppercase;
                            letter-spacing:1px; margin-bottom:6px;">Air Impact Score</div>
                <div style="font-size:3rem; font-weight:800; color:{score_color};">{score}</div>
                <div style="font-size:0.95rem; color:{score_color}; font-weight:600;">{score_label}</div>
            </div>
            <div style="background:rgba(0,0,0,0.03); border-radius:8px;
                        height:10px; overflow:hidden; margin:0 20px 18px;">
                <div style="width:{score}%; height:100%; background:{score_color};
                            border-radius:8px;"></div>
            </div>
            <div style="display:flex; justify-content:space-around; flex-wrap:wrap; gap:12px;">
                <div style="text-align:center;">
                    <div style="color:#888; font-size:0.75rem;">CO₂ / день</div>
                    <div style="font-weight:700; font-size:1.1rem;">{result['co2_daily_kg']} кг</div>
                </div>
                <div style="text-align:center;">
                    <div style="color:#888; font-size:0.75rem;">CO₂ / месяц</div>
                    <div style="font-weight:700; font-size:1.1rem;">{result['co2_monthly_kg']} кг</div>
                </div>
                <div style="text-align:center;">
                    <div style="color:#888; font-size:0.75rem;">CO₂ / год</div>
                    <div style="font-weight:700; font-size:1.1rem;">{result['co2_yearly_kg']} кг</div>
                </div>
                <div style="text-align:center;">
                    <div style="color:#888; font-size:0.75rem;">vs среднее</div>
                    <div style="font-weight:700; font-size:1.1rem; color:{comp_color};">{comp_text}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
