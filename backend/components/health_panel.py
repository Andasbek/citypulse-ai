import streamlit as st
import pandas as pd


def render_health_panel(combined_df: pd.DataFrame, ecology_kpis: dict):
    """Render health recommendations and walk safety panel."""

    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:10px; margin:8px 0 18px;">
            <span style="font-size:1.4rem;">🏥</span>
            <span style="font-size:1.2rem; font-weight:700; color:#2d3436;">
                Здоровье и рекомендации по прогулкам
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    avg_aqi = ecology_kpis["avg_aqi"]
    _render_general_health(avg_aqi)

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # Districts ranked by walk safety
    st.markdown(
        """<div style="font-weight:700; font-size:1rem; color:#2d3436; margin:12px 0 10px;">
            🚶 Рейтинг районов для прогулок
        </div>""",
        unsafe_allow_html=True,
    )

    sorted_df = combined_df.sort_values("risk_score", ascending=True)
    for _, row in sorted_df.iterrows():
        risk = float(row["risk_score"])
        aqi = float(row["avg_aqi"])
        district = row["district"]

        if risk < 45:
            safety = "Безопасно"
            safety_color = "#2ecc71"
            icon = "🟢"
            rec = "Хорошие условия для прогулок и занятий спортом на открытом воздухе."
        elif risk < 70:
            safety = "Умеренно"
            safety_color = "#f39c12"
            icon = "🟡"
            rec = "Прогулки возможны, но людям с чувствительным здоровьем рекомендуется сократить время."
        else:
            safety = "Неблагоприятно"
            safety_color = "#e74c3c"
            icon = "🔴"
            rec = "Не рекомендуется для длительных прогулок. Особенно опасно для детей, пожилых и астматиков."

        groups_html = _risk_groups_html(aqi, risk)

        st.markdown(
            f"""
            <div style="border-left:4px solid {safety_color}; background:rgba(0,0,0,0.01);
                        padding:14px 18px; margin:8px 0; border-radius:0 12px 12px 0;
                        box-shadow:0 1px 4px rgba(0,0,0,0.03);">
                <div style="display:flex; justify-content:space-between; align-items:center;
                            flex-wrap:wrap; gap:6px; margin-bottom:6px;">
                    <span style="font-weight:700; font-size:0.95rem; color:#2d3436;">
                        {icon} {district}
                    </span>
                    <div style="display:flex; gap:8px; align-items:center;">
                        <span style="color:#888; font-size:0.8rem;">AQI: {aqi:.0f}</span>
                        <span style="background:{safety_color}; color:#fff; padding:2px 10px;
                                    border-radius:20px; font-size:0.72rem; font-weight:600;">
                            {safety}
                        </span>
                    </div>
                </div>
                <div style="color:#636e72; font-size:0.87rem; margin-bottom:6px;">{rec}</div>
                {groups_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # General tips
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    _render_general_tips()


def _render_general_health(avg_aqi: float):
    if avg_aqi <= 50:
        status, color, text = "Благоприятно", "#2ecc71", (
            "Качество воздуха в городе хорошее. Прогулки и занятия спортом "
            "на открытом воздухе безопасны для всех групп населения."
        )
    elif avg_aqi <= 100:
        status, color, text = "Умеренно", "#f39c12", (
            "Качество воздуха приемлемое, но чувствительным группам "
            "(дети, пожилые, астматики) рекомендуется сократить "
            "длительные нагрузки на открытом воздухе."
        )
    else:
        status, color, text = "Неблагоприятно", "#e74c3c", (
            "Качество воздуха ухудшено. Всем жителям рекомендуется "
            "сократить время на открытом воздухе. Группам риска — "
            "оставаться в помещении."
        )

    st.markdown(
        f"""
        <div style="background:{color}10; border:1px solid {color}30;
                    border-radius:12px; padding:16px 20px;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
                <span style="font-size:1.2rem;">🌡️</span>
                <span style="font-weight:700; color:{color};">
                    Общая оценка: {status}
                </span>
                <span style="color:#888; font-size:0.85rem; margin-left:auto;">
                    Средний AQI: {avg_aqi}
                </span>
            </div>
            <div style="color:#555; font-size:0.9rem;">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _risk_groups_html(aqi: float, risk: float) -> str:
    if risk < 45:
        return ""

    groups = []
    if risk >= 70:
        groups = [
            ("👶 Дети", "#e74c3c", "Не рекомендуется"),
            ("👴 Пожилые", "#e74c3c", "Не рекомендуется"),
            ("🫁 Астматики", "#e74c3c", "Опасно"),
            ("🏃 Спортсмены", "#f39c12", "С осторожностью"),
        ]
    elif risk >= 45:
        groups = [
            ("👶 Дети", "#f39c12", "С осторожностью"),
            ("👴 Пожилые", "#f39c12", "С осторожностью"),
            ("🫁 Астматики", "#e74c3c", "Не рекомендуется"),
        ]

    if not groups:
        return ""

    items = "".join(
        f'<span style="background:{c}15; color:{c}; padding:2px 8px; '
        f'border-radius:12px; font-size:0.75rem; font-weight:600; '
        f'border:1px solid {c}30;">{icon} {label}</span>'
        for icon, c, label in groups
    )
    return (
        f'<div style="display:flex; gap:6px; flex-wrap:wrap; margin-top:6px; '
        f'padding-top:6px; border-top:1px solid rgba(0,0,0,0.04);">{items}</div>'
    )


def _render_general_tips():
    st.markdown(
        """
        <div style="background:#fff; border-radius:12px; padding:18px 22px;
                    box-shadow:0 1px 6px rgba(0,0,0,0.04);">
            <div style="font-weight:700; font-size:0.95rem; color:#2d3436; margin-bottom:10px;">
                💡 Общие рекомендации
            </div>
            <div style="color:#636e72; font-size:0.88rem; line-height:1.8;">
                • Лучшее время для прогулок — раннее утро (до 9:00), когда загруженность дорог минимальна<br>
                • Выбирайте парковые зоны вдали от крупных магистралей<br>
                • При AQI > 100 используйте защитную маску при длительном нахождении на улице<br>
                • Следите за обновлениями показателей — ситуация может меняться в течение дня<br>
                • Детям и пожилым рекомендуется сократить время на улице при AQI > 75
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
