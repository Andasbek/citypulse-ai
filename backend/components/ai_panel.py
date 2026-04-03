import streamlit as st

from utils.constants import STATUS_COLORS, STATUS_LABELS


def render_ai_panel(insight: dict):
    severity = insight["severity"]
    color = STATUS_COLORS[severity]
    label = STATUS_LABELS[severity]

    severity_badge = (
        f'<span style="background:{color}; color:#fff; padding:3px 14px; '
        f'border-radius:20px; font-size:0.78rem; font-weight:600; '
        f'letter-spacing:0.5px;">{label.upper()}</span>'
    )

    top_district_html = ""
    if insight["top_district"]:
        top_district_html = f"""
        <div style="display:flex; align-items:center; gap:8px; margin-top:10px;">
            <span style="color:rgba(255,255,255,0.5); font-size:0.8rem;">Наиболее проблемный район:</span>
            <span style="color:#ffeaa7; font-weight:600; font-size:0.95rem;">
                📍 {insight['top_district']}
            </span>
        </div>
        """

    risk_pct = min(100, insight["risk_score"])
    risk_color = color

    recs_html = ""
    for rec in insight["recommendations"][:6]:
        priority = rec["priority"]
        if priority == "critical":
            rec_icon, rec_border = "🔴", "#e74c3c"
        elif priority == "high":
            rec_icon, rec_border = "🟠", "#e17055"
        elif priority == "medium":
            rec_icon, rec_border = "🟡", "#f39c12"
        else:
            rec_icon, rec_border = "🟢", "#2ecc71"
        recs_html += f"""
        <div style="border-left:3px solid {rec_border}; padding:6px 12px;
                    margin:6px 0; background:rgba(255,255,255,0.03);
                    border-radius:0 6px 6px 0; font-size:0.88rem;">
            {rec_icon} {rec['text']}
        </div>
        """

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
                    color: #dfe6e9; padding: 28px 32px; border-radius: 16px;
                    margin: 8px 0 16px;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.15);
                    border: 1px solid rgba(255,255,255,0.06);
                    line-height: 1.7; font-size: 0.95rem;">

            <!-- Header -->
            <div style="display:flex; align-items:center; justify-content:space-between;
                        margin-bottom:18px; padding-bottom:14px;
                        border-bottom:1px solid rgba(255,255,255,0.1); flex-wrap:wrap; gap:10px;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="font-size:1.5rem;">🤖</span>
                    <span style="font-size:1.15rem; font-weight:700; color:#fff;">
                        AI-анализ и рекомендации
                    </span>
                </div>
                <div style="display:flex; align-items:center; gap:12px;">
                    {severity_badge}
                    <span style="color:rgba(255,255,255,0.5); font-size:0.82rem;">
                        Риск: <strong style="color:{risk_color};">{insight['risk_score']}</strong>/100
                    </span>
                </div>
            </div>

            <!-- Summary -->
            <div style="background:rgba(255,255,255,0.05); border-radius:10px;
                        padding:14px 18px; margin-bottom:18px;">
                <div style="color:#fff; font-size:1.02rem; font-weight:600;
                            margin-bottom:4px;">
                    {insight['summary']}
                </div>
                {top_district_html}
            </div>

            <!-- What is happening -->
            <h4 style="color:#a29bfe; margin:16px 0 8px; font-size:1rem;">
                📊 Что происходит?
            </h4>
            <div style="color:#b2bec3; margin-bottom:14px; font-size:0.92rem;">
                {insight['what_is_happening']}
            </div>

            <!-- Why critical -->
            <h4 style="color:#a29bfe; margin:16px 0 8px; font-size:1rem;">
                ⚡ Насколько это критично?
            </h4>
            <div style="margin-bottom:6px;">
                <div style="background:rgba(255,255,255,0.08); border-radius:8px;
                            height:8px; overflow:hidden; margin:8px 0 12px;">
                    <div style="width:{risk_pct}%; height:100%; background:{risk_color};
                                border-radius:8px; transition:width 0.5s;"></div>
                </div>
            </div>
            <div style="color:#b2bec3; margin-bottom:14px; font-size:0.92rem;">
                {insight['why_critical']}
            </div>

            <!-- Recommendations -->
            <h4 style="color:#a29bfe; margin:16px 0 8px; font-size:1rem;">
                💡 Что рекомендуется сделать?
            </h4>
            {recs_html}

        </div>
        """,
        unsafe_allow_html=True,
    )
