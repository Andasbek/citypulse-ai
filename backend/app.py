import sys
from pathlib import Path

import streamlit as st
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parent))

from services.data_loader import load_transport, load_ecology
from services.transport_service import (
    get_transport_kpis,
    get_transport_status,
    get_congestion_by_time,
    get_congestion_by_district,
)
from services.ecology_service import (
    get_ecology_kpis,
    get_ecology_status,
    get_aqi_by_time,
    get_aqi_by_district,
)
from services.anomaly_detector import detect_transport_issues, detect_ecology_issues
from services.combined_analysis import get_combined_data, detect_combined_issues
from services.ai_service import build_ai_insight, ask_assistant, explain_impact
from services.user_impact_service import calculate_impact
from components.header import render_header
from components.kpi_cards import render_transport_kpis, render_ecology_kpis
from components.transport_section import render_transport_section
from components.ecology_section import render_ecology_section
from components.issues_panel import render_issues_panel
from components.ai_panel import render_ai_panel
from components.city_map import render_city_map
from components.assistant_chat import render_assistant_chat
from components.impact_calculator import render_impact_calculator
from components.health_panel import render_health_panel
from components.routes_panel import render_routes_panel
from components.recycling_map import render_recycling_map
from utils.constants import STATUS_CRITICAL, STATUS_WARNING

st.set_page_config(
    page_title="CityPulse AI",
    page_icon="🏙️",
    layout="wide",
)

# --- Global CSS ---
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background: #f7f8fc;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background: #fff;
            padding: 6px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 600;
            font-size: 0.85rem;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #6c5ce7, #a29bfe) !important;
            color: #fff !important;
        }

        .streamlit-expanderHeader {
            font-weight: 600;
            font-size: 0.95rem;
        }

        [data-testid="stMetric"] {
            background: #fff;
            padding: 16px;
            border-radius: 10px;
            box-shadow: 0 1px 6px rgba(0,0,0,0.04);
        }

        hr {
            border: none;
            border-top: 1px solid rgba(0,0,0,0.06);
            margin: 24px 0;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Load data ---
transport_df = load_transport()
ecology_df = load_ecology()

# --- KPIs ---
t_kpis = get_transport_kpis(transport_df)
e_kpis = get_ecology_kpis(ecology_df)
t_status = get_transport_status(t_kpis["avg_congestion"])
e_status = get_ecology_status(e_kpis["avg_aqi"])

# --- Issues ---
t_issues = detect_transport_issues(transport_df)
e_issues = detect_ecology_issues(ecology_df)
c_issues = detect_combined_issues(transport_df, ecology_df)
all_issues = t_issues + e_issues + c_issues

critical_count = sum(1 for i in all_issues if i["severity"] == STATUS_CRITICAL)
city_status = (
    STATUS_CRITICAL
    if critical_count > 0
    else STATUS_WARNING
    if any(i["severity"] == STATUS_WARNING for i in all_issues)
    else "normal"
)

# --- Combined data ---
combined_df = get_combined_data(transport_df, ecology_df)

# --- AI Insight ---
ai_insight = build_ai_insight(
    transport_kpis=t_kpis,
    ecology_kpis=e_kpis,
    all_issues=all_issues,
    combined_issues=c_issues,
)

# City context for assistant/impact
city_context = {
    **ai_insight,
    "avg_aqi": e_kpis["avg_aqi"],
    "avg_pm25": e_kpis["avg_pm25"],
    "avg_congestion": t_kpis["avg_congestion"],
    "avg_speed": t_kpis["avg_speed"],
}

# --- Header ---
render_header(city_status, len(all_issues), critical_count)

# --- AI Panel ---
render_ai_panel(ai_insight)

st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

# --- Tabs ---
CHART_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#2d3436"),
    margin=dict(l=40, r=20, t=50, b=40),
    title_font=dict(size=15, color="#2d3436"),
    height=400,
)

tabs = st.tabs([
    "🚗 Транспорт",
    "🌿 Экология",
    "🔗 Карта и анализ",
    "💬 AI-ассистент",
    "🚗 Мой след",
    "🏥 Здоровье",
    "🛣️ Маршруты",
    "♻️ Переработка",
])

# ── Tab: Transport ──
with tabs[0]:
    render_transport_kpis(t_kpis, t_status)
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    render_transport_section(
        get_congestion_by_time(transport_df),
        get_congestion_by_district(transport_df),
        all_issues,
    )

# ── Tab: Ecology ──
with tabs[1]:
    render_ecology_kpis(e_kpis, e_status)
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    render_ecology_section(
        get_aqi_by_time(ecology_df),
        get_aqi_by_district(ecology_df),
        all_issues,
    )

# ── Tab: Map & Combined ──
with tabs[2]:
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:10px; margin:8px 0 18px;">
            <span style="font-size:1.4rem;">🔗</span>
            <span style="font-size:1.2rem; font-weight:700; color:#2d3436;">
                Связь транспорта и экологии
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        colors = [
            "#e74c3c" if v > 70 else "#f39c12" if v > 45 else "#2ecc71"
            for v in combined_df["risk_score"]
        ]
        fig = go.Figure(go.Bar(
            x=combined_df["district"],
            y=combined_df["risk_score"],
            marker_color=colors,
            text=combined_df["risk_score"].astype(str),
            textposition="outside",
        ))
        fig.update_layout(
            title="Комбинированный индекс риска по районам",
            xaxis_title="Район",
            yaxis_title="Индекс риска",
            **CHART_LAYOUT,
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=combined_df["avg_congestion"],
            y=combined_df["avg_aqi"],
            mode="markers+text",
            text=combined_df["district"],
            textposition="top center",
            textfont=dict(size=11, color="#2d3436"),
            marker=dict(
                size=combined_df["risk_score"] * 0.6,
                color=combined_df["risk_score"],
                colorscale=[[0, "#2ecc71"], [0.5, "#f39c12"], [1, "#e74c3c"]],
                showscale=True,
                colorbar=dict(title="Риск", thickness=12),
                line=dict(width=1, color="rgba(255,255,255,0.6)"),
            ),
        ))
        fig.update_layout(
            title="Загруженность vs Качество воздуха",
            xaxis_title="Загруженность (%)",
            yaxis_title="AQI",
            **CHART_LAYOUT,
        )
        fig.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
        fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
        st.plotly_chart(fig, use_container_width=True)

    if c_issues:
        st.markdown(
            f"""
            <div style="background:rgba(231,76,60,0.06); border:1px solid rgba(231,76,60,0.15);
                        border-radius:12px; padding:18px 22px; margin:8px 0;">
                <div style="font-weight:700; color:#e74c3c; margin-bottom:10px; font-size:1rem;">
                    ⚠️ Обнаружено {len(c_issues)} комбинированных проблем высокого приоритета
                </div>
            """,
            unsafe_allow_html=True,
        )
        for issue in c_issues:
            st.markdown(
                f"""<div style="padding:6px 0 6px 14px; border-left:3px solid #e74c3c;
                            margin:6px 0; font-size:0.9rem;">
                    🔴 <strong>{issue['district']}</strong>
                    <span style="color:#888;">({issue['timestamp']})</span>
                    — {issue['description']}
                </div>""",
                unsafe_allow_html=True,
            )
        st.markdown(
            """
                <div style="margin-top:14px; padding-top:12px;
                            border-top:1px solid rgba(231,76,60,0.12);
                            color:#2d3436; font-size:0.92rem;">
                    <strong>Вывод:</strong> В указанных районах наблюдается одновременно
                    высокая транспортная нагрузка и ухудшение качества воздуха.
                    Это может свидетельствовать о прямой связи между загруженностью
                    дорог и экологической обстановкой.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.success("Комбинированных проблем высокого приоритета не обнаружено.")

    render_city_map(combined_df, all_issues)

# ── Tab: AI Assistant ──
with tabs[3]:
    render_assistant_chat(ask_assistant, city_context)

# ── Tab: Personal Impact ──
with tabs[4]:
    render_impact_calculator(calculate_impact, explain_impact, city_context)

# ── Tab: Health ──
with tabs[5]:
    render_health_panel(combined_df, e_kpis)

# ── Tab: Routes ──
with tabs[6]:
    render_routes_panel(transport_df, combined_df)

# ── Tab: Recycling ──
with tabs[7]:
    render_recycling_map()

st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

# --- Issues panel ---
render_issues_panel(ai_insight["recommendations"])

# --- Footer ---
st.markdown(
    f"""
    <div style="text-align:center; color:#b2bec3; font-size:0.8rem;
                padding:30px 0 10px; margin-top:40px;
                border-top:1px solid rgba(0,0,0,0.05);">
        CityPulse AI — Интеллектуальный мониторинг городской среды
        {"&nbsp;•&nbsp; 🤖 OpenAI подключен" if ai_insight.get("ai_powered") else ""}
    </div>
    """,
    unsafe_allow_html=True,
)
