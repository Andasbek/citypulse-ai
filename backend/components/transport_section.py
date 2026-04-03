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


def render_transport_section(
    congestion_time: pd.DataFrame,
    congestion_district: pd.DataFrame,
    issues: list[dict],
):
    st.markdown("")
    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=congestion_time["timestamp"],
            y=congestion_time["congestion_level"],
            mode="lines+markers",
            line=dict(color="#6c5ce7", width=3),
            marker=dict(size=7),
            fill="tozeroy",
            fillcolor="rgba(108,92,231,0.08)",
            name="Загруженность",
        ))
        fig.add_hline(y=80, line_dash="dash", line_color="#e74c3c",
                      annotation_text="Критично", annotation_font_color="#e74c3c")
        fig.add_hline(y=50, line_dash="dash", line_color="#f39c12",
                      annotation_text="Внимание", annotation_font_color="#f39c12")
        fig.update_layout(
            title="Загруженность дорог по времени",
            xaxis_title="Время",
            yaxis_title="Загруженность (%)",
            **CHART_LAYOUT,
        )
        fig.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
        fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        colors = [
            "#e74c3c" if v >= 80 else "#f39c12" if v >= 50 else "#2ecc71"
            for v in congestion_district["congestion_level"]
        ]
        fig = go.Figure(go.Bar(
            x=congestion_district["district"],
            y=congestion_district["congestion_level"],
            marker_color=colors,
            marker_line=dict(width=0),
            text=congestion_district["congestion_level"].round(1).astype(str) + "%",
            textposition="outside",
        ))
        fig.update_layout(
            title="Загруженность по районам",
            xaxis_title="Район",
            yaxis_title="Загруженность (%)",
            **CHART_LAYOUT,
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
        st.plotly_chart(fig, use_container_width=True)

    transport_issues = [i for i in issues if i["type"] == "Транспорт"]
    if transport_issues:
        with st.expander(f"🚨 Транспортные проблемы ({len(transport_issues)})", expanded=False):
            for issue in transport_issues:
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
