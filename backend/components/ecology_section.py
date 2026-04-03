import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

CHART_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#2d3436"),
    margin=dict(l=40, r=20, t=50, b=40),
    title_font=dict(size=15, color="#2d3436"),
    height=380,
)


def render_ecology_section(
    aqi_time: pd.DataFrame,
    aqi_district: pd.DataFrame,
    issues: list[dict],
):
    st.markdown("")
    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=aqi_time["timestamp"],
            y=aqi_time["aqi"],
            mode="lines+markers",
            line=dict(color="#00b894", width=3),
            marker=dict(size=7),
            fill="tozeroy",
            fillcolor="rgba(0,184,148,0.08)",
            name="AQI",
        ))
        fig.add_hline(y=100, line_dash="dash", line_color="#e74c3c",
                      annotation_text="Критично", annotation_font_color="#e74c3c")
        fig.add_hline(y=50, line_dash="dash", line_color="#f39c12",
                      annotation_text="Внимание", annotation_font_color="#f39c12")
        fig.update_layout(
            title="Индекс качества воздуха (AQI) по времени",
            xaxis_title="Время",
            yaxis_title="AQI",
            **CHART_LAYOUT,
        )
        fig.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
        fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        colors = [
            "#e74c3c" if v > 100 else "#f39c12" if v > 50 else "#2ecc71"
            for v in aqi_district["aqi"]
        ]
        fig = go.Figure(go.Bar(
            x=aqi_district["district"],
            y=aqi_district["aqi"],
            marker_color=colors,
            marker_line=dict(width=0),
            text=aqi_district["aqi"].round(1).astype(str),
            textposition="outside",
        ))
        fig.update_layout(
            title="AQI по районам",
            xaxis_title="Район",
            yaxis_title="AQI",
            **CHART_LAYOUT,
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
        st.plotly_chart(fig, use_container_width=True)

    ecology_issues = [i for i in issues if i["type"] == "Экология"]
    if ecology_issues:
        with st.expander(f"🚨 Экологические проблемы ({len(ecology_issues)})", expanded=False):
            for issue in ecology_issues:
                sev = issue["severity"]
                icon = "🔴" if sev == "critical" else "🟡"
                bg = "rgba(231,76,60,0.06)" if sev == "critical" else "rgba(243,156,18,0.06)"
                border = "#e74c3c" if sev == "critical" else "#f39c12"
                st.markdown(
                    f"""<div style="border-left:3px solid {border}; background:{bg};
                                padding:8px 14px; margin:6px 0; border-radius:0 8px 8px 0;
                                font-size:0.9rem;">
                        {icon} <strong>{issue['district']}</strong>
                        <span style="color:#888;">({issue['timestamp']})</span>
                        — {issue['description']}
                    </div>""",
                    unsafe_allow_html=True,
                )
