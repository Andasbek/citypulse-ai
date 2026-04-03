import streamlit as st


def render_issues_panel(recommendations: list[dict]):
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:10px; margin:8px 0 18px;">
            <span style="font-size:1.4rem;">📋</span>
            <span style="font-size:1.2rem; font-weight:700; color:#2d3436;">
                Проблемные ситуации и рекомендации
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not recommendations:
        st.success("Проблемных ситуаций не обнаружено.")
        return

    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    sorted_recs = sorted(recommendations, key=lambda r: priority_order.get(r["priority"], 99))

    groups = {
        "critical": ("🔴 Критические", "#e74c3c"),
        "high": ("🟠 Высокий приоритет", "#e17055"),
        "medium": ("🟡 Средний приоритет", "#f39c12"),
        "low": ("🟢 Стандартные", "#2ecc71"),
    }

    current_priority = None
    for rec in sorted_recs:
        p = rec["priority"]
        if p != current_priority:
            current_priority = p
            group_label, group_color = groups.get(p, ("📌 Прочее", "#636e72"))
            count = sum(1 for r in sorted_recs if r["priority"] == p)
            st.markdown(
                f"""<div style="color:{group_color}; font-weight:600; font-size:0.85rem;
                            text-transform:uppercase; letter-spacing:1px; margin:18px 0 10px;">
                    {group_label} ({count})
                </div>""",
                unsafe_allow_html=True,
            )

        _render_rec_card(rec)


_TYPE_ICONS = {
    "Транспорт": "🚗",
    "Экология": "🌿",
    "Комбинированная": "🔗",
    "Мониторинг": "👁️",
    "Общая": "📌",
}

_PRIORITY_STYLES = {
    "critical": ("#e74c3c", "rgba(231,76,60,0.04)"),
    "high": ("#e17055", "rgba(225,112,85,0.04)"),
    "medium": ("#f39c12", "rgba(243,156,18,0.04)"),
    "low": ("#2ecc71", "rgba(46,204,113,0.04)"),
}


def _render_rec_card(rec: dict):
    icon = _TYPE_ICONS.get(rec["type"], "📌")
    border_color, bg_color = _PRIORITY_STYLES.get(rec["priority"], ("#636e72", "rgba(0,0,0,0.02)"))

    priority_label = {
        "critical": "КРИТИЧНО",
        "high": "ВЫСОКИЙ",
        "medium": "СРЕДНИЙ",
        "low": "НИЗКИЙ",
    }.get(rec["priority"], rec["priority"].upper())

    st.markdown(
        f"""
        <div style="border-left:4px solid {border_color}; background:{bg_color};
                    padding:14px 18px; margin:8px 0; border-radius:0 12px 12px 0;
                    box-shadow:0 1px 6px rgba(0,0,0,0.04);">
            <div style="display:flex; justify-content:space-between; align-items:center;
                        margin-bottom:6px; flex-wrap:wrap; gap:6px;">
                <span style="font-weight:700; font-size:0.95rem; color:#2d3436;">
                    {icon} {rec['type']} — {rec['district']}
                </span>
                <span style="background:{border_color}; color:#fff; padding:2px 10px;
                            border-radius:20px; font-size:0.72rem; font-weight:600;">
                    {priority_label}
                </span>
            </div>
            <div style="color:#0984e3; font-size:0.88rem; font-style:italic;
                        padding-top:6px; border-top:1px solid rgba(0,0,0,0.05);">
                💡 {rec['text']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
