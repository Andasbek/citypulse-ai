import streamlit as st

from utils.constants import STATUS_COLORS, STATUS_LABELS


def _render_card(label: str, value: str, icon: str, accent: str = "#6c5ce7"):
    return f"""
    <div style="background:#fff; border-radius:12px; padding:20px 24px;
                box-shadow:0 2px 12px rgba(0,0,0,0.06); border-top:3px solid {accent};
                text-align:center;">
        <div style="font-size:1.6rem; margin-bottom:4px;">{icon}</div>
        <div style="color:#888; font-size:0.78rem; text-transform:uppercase;
                    letter-spacing:0.8px; margin-bottom:4px;">{label}</div>
        <div style="font-size:1.5rem; font-weight:700; color:#2d3436;">{value}</div>
    </div>
    """


def render_transport_kpis(kpis: dict, status: str):
    color = STATUS_COLORS[status]
    label = STATUS_LABELS[status]
    emoji = {"normal": "🟢", "warning": "🟡", "critical": "🔴"}[status]

    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:16px;">
            <span style="font-size:1.3rem;">{emoji}</span>
            <span style="font-size:1.1rem; font-weight:600; color:{color};">
                Статус: {label}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(3)
    cards = [
        ("Средняя скорость", f"{kpis['avg_speed']} км/ч", "🚗", "#0984e3"),
        ("Загруженность", f"{kpis['avg_congestion']}%", "📊", "#e17055"),
        ("Инциденты", str(kpis["total_incidents"]), "⚠️", "#fdcb6e"),
    ]
    for col, (lbl, val, ico, clr) in zip(cols, cards):
        with col:
            st.markdown(_render_card(lbl, val, ico, clr), unsafe_allow_html=True)


def render_ecology_kpis(kpis: dict, status: str):
    color = STATUS_COLORS[status]
    label = STATUS_LABELS[status]
    emoji = {"normal": "🟢", "warning": "🟡", "critical": "🔴"}[status]

    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:16px;">
            <span style="font-size:1.3rem;">{emoji}</span>
            <span style="font-size:1.1rem; font-weight:600; color:{color};">
                Статус: {label}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(3)
    cards = [
        ("Средний AQI", str(kpis["avg_aqi"]), "🌫️", "#6c5ce7"),
        ("Средний PM2.5", str(kpis["avg_pm25"]), "🔬", "#00b894"),
        ("Средний PM10", str(kpis["avg_pm10"]), "💨", "#0984e3"),
    ]
    for col, (lbl, val, ico, clr) in zip(cols, cards):
        with col:
            st.markdown(_render_card(lbl, val, ico, clr), unsafe_allow_html=True)
