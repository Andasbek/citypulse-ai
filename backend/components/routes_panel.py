import streamlit as st
import pandas as pd


# Mock data for traffic hotspots
_TRAFFIC_HOTSPOTS = [
    {"street": "пр. Аль-Фараби", "district": "Бостандыкский", "congestion": 92, "direction": "восток → запад",
     "alternative": "ул. Тимирязева или ул. Жандосова"},
    {"street": "пр. Абая", "district": "Алмалинский", "congestion": 85, "direction": "запад → восток",
     "alternative": "ул. Гоголя или ул. Кабанбай батыра"},
    {"street": "пр. Назарбаева", "district": "Медеуский", "congestion": 78, "direction": "юг → север",
     "alternative": "ул. Фурманова или ул. Байтурсынова"},
    {"street": "ул. Толе би", "district": "Алмалинский", "congestion": 72, "direction": "запад → восток",
     "alternative": "ул. Макатаева или ул. Шевченко"},
    {"street": "ул. Саина", "district": "Ауэзовский", "congestion": 68, "direction": "север → юг",
     "alternative": "ул. Момышулы или ул. Алтынсарина"},
]


def render_routes_panel(transport_df: pd.DataFrame, combined_df: pd.DataFrame):
    """Render smart routes and traffic hints panel."""

    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:10px; margin:8px 0 18px;">
            <span style="font-size:1.4rem;">🛣️</span>
            <span style="font-size:1.2rem; font-weight:700; color:#2d3436;">
                Пробки и маршруты
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Overall traffic status
    avg_speed = transport_df["avg_speed"].mean()
    avg_congestion = transport_df["congestion_level"].mean()

    if avg_congestion >= 80:
        traffic_status, traffic_color = "Высокая загруженность", "#e74c3c"
    elif avg_congestion >= 50:
        traffic_status, traffic_color = "Умеренная загруженность", "#f39c12"
    else:
        traffic_status, traffic_color = "Свободное движение", "#2ecc71"

    st.markdown(
        f"""
        <div style="background:{traffic_color}10; border:1px solid {traffic_color}30;
                    border-radius:12px; padding:16px 20px; margin-bottom:16px;">
            <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
                <span style="font-size:1.3rem;">🚦</span>
                <span style="font-weight:700; color:{traffic_color}; font-size:1.05rem;">
                    {traffic_status}
                </span>
                <span style="color:#888; font-size:0.85rem; margin-left:auto;">
                    Средняя скорость: {avg_speed:.0f} км/ч &nbsp;|&nbsp;
                    Загруженность: {avg_congestion:.0f}%
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Traffic hotspots
    st.markdown(
        """<div style="font-weight:700; font-size:1rem; color:#2d3436; margin:16px 0 10px;">
            🔥 Проблемные участки
        </div>""",
        unsafe_allow_html=True,
    )

    for spot in _TRAFFIC_HOTSPOTS:
        cong = spot["congestion"]
        if cong >= 80:
            color = "#e74c3c"
        elif cong >= 60:
            color = "#f39c12"
        else:
            color = "#2ecc71"

        st.markdown(
            f"""
            <div style="border-left:4px solid {color}; background:rgba(0,0,0,0.01);
                        padding:12px 16px; margin:8px 0; border-radius:0 10px 10px 0;">
                <div style="display:flex; justify-content:space-between; align-items:center;
                            flex-wrap:wrap; gap:6px;">
                    <span style="font-weight:700; font-size:0.93rem; color:#2d3436;">
                        {spot['street']}
                    </span>
                    <span style="background:{color}; color:#fff; padding:2px 10px;
                                border-radius:20px; font-size:0.72rem; font-weight:600;">
                        {cong}%
                    </span>
                </div>
                <div style="color:#888; font-size:0.82rem; margin:4px 0;">
                    {spot['district']} &nbsp;•&nbsp; {spot['direction']}
                </div>
                <div style="color:#0984e3; font-size:0.85rem;">
                    🔄 Альтернатива: {spot['alternative']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # District congestion ranking
    st.markdown(
        """<div style="font-weight:700; font-size:1rem; color:#2d3436; margin:12px 0 10px;">
            📊 Загруженность по районам
        </div>""",
        unsafe_allow_html=True,
    )

    district_stats = (
        transport_df.groupby("district")
        .agg(avg_speed=("avg_speed", "mean"), avg_congestion=("congestion_level", "mean"))
        .reset_index()
        .sort_values("avg_congestion", ascending=False)
    )

    for _, row in district_stats.iterrows():
        cong = row["avg_congestion"]
        speed = row["avg_speed"]
        if cong >= 80:
            color = "#e74c3c"
        elif cong >= 50:
            color = "#f39c12"
        else:
            color = "#2ecc71"

        pct = min(100, cong)
        st.markdown(
            f"""
            <div style="margin:6px 0;">
                <div style="display:flex; justify-content:space-between; font-size:0.88rem;">
                    <span style="font-weight:600; color:#2d3436;">{row['district']}</span>
                    <span style="color:#888;">{cong:.0f}% &nbsp;|&nbsp; {speed:.0f} км/ч</span>
                </div>
                <div style="background:rgba(0,0,0,0.04); border-radius:4px;
                            height:6px; overflow:hidden; margin-top:4px;">
                    <div style="width:{pct:.0f}%; height:100%; background:{color};
                                border-radius:4px;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 2GIS link
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background:#fff; border-radius:12px; padding:16px 20px;
                    box-shadow:0 1px 6px rgba(0,0,0,0.04); text-align:center;">
            <div style="font-size:0.9rem; color:#636e72; margin-bottom:8px;">
                Для построения маршрута используйте
            </div>
            <a href="https://2gis.kz/almaty" target="_blank"
               style="display:inline-block; background:#2ecc71; color:#fff;
                      padding:8px 24px; border-radius:8px; text-decoration:none;
                      font-weight:600; font-size:0.9rem;">
                🗺️ Открыть 2GIS Алматы
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )
