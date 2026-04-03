import streamlit as st

from utils.constants import STATUS_COLORS, STATUS_LABELS


def render_header(city_status: str, total_issues: int, critical_issues: int):
    color = STATUS_COLORS[city_status]
    label = STATUS_LABELS[city_status]

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
                    padding: 40px 30px 30px; border-radius: 16px; margin-bottom: 24px;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.18);">
            <h1 style="text-align:center; margin:0; color:#fff; font-size:2.6rem;
                        font-weight:800; letter-spacing:-0.5px;">
                🏙️ CityPulse AI
            </h1>
            <p style="text-align:center; color:rgba(255,255,255,0.6); margin:4px 0 28px;
                      font-size:1.05rem;">
                Интеллектуальный мониторинг города — транспорт и экология
            </p>
            <div style="display:flex; justify-content:center; gap:16px; flex-wrap:wrap;">
                <div style="background:rgba(255,255,255,0.08); backdrop-filter:blur(10px);
                            border:1px solid rgba(255,255,255,0.12); border-radius:12px;
                            padding:18px 32px; text-align:center; min-width:180px;">
                    <div style="color:rgba(255,255,255,0.55); font-size:0.8rem;
                                text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">
                        Статус города
                    </div>
                    <div style="color:{color}; font-size:1.5rem; font-weight:700;">
                        {label}
                    </div>
                    <div style="height:3px; background:{color}; border-radius:2px;
                                margin-top:10px; opacity:0.8;"></div>
                </div>
                <div style="background:rgba(255,255,255,0.08); backdrop-filter:blur(10px);
                            border:1px solid rgba(255,255,255,0.12); border-radius:12px;
                            padding:18px 32px; text-align:center; min-width:180px;">
                    <div style="color:rgba(255,255,255,0.55); font-size:0.8rem;
                                text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">
                        Активных проблем
                    </div>
                    <div style="color:#f8f8f8; font-size:1.5rem; font-weight:700;">
                        {total_issues}
                    </div>
                </div>
                <div style="background:rgba(255,255,255,0.08); backdrop-filter:blur(10px);
                            border:1px solid rgba(255,255,255,0.12); border-radius:12px;
                            padding:18px 32px; text-align:center; min-width:180px;">
                    <div style="color:rgba(255,255,255,0.55); font-size:0.8rem;
                                text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">
                        Критических
                    </div>
                    <div style="color:#e74c3c; font-size:1.5rem; font-weight:700;">
                        {critical_issues}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
