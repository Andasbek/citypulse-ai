import streamlit as st
import pandas as pd
import pydeck as pdk
from pathlib import Path

RECYCLING_CSV = Path(__file__).resolve().parent.parent / "data" / "recycling_points.csv"

_TYPE_COLORS = {
    "Пластик": [46, 204, 113],
    "Бумага": [52, 152, 219],
    "Пластик и бумага": [155, 89, 182],
    "Стекло и металл": [230, 126, 34],
    "Пластик и стекло": [26, 188, 156],
    "Все виды": [241, 196, 15],
}


def render_recycling_map():
    """Render recycling container map."""

    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:10px; margin:8px 0 18px;">
            <span style="font-size:1.4rem;">♻️</span>
            <span style="font-size:1.2rem; font-weight:700; color:#2d3436;">
                Карта контейнеров для сортировки отходов
            </span>
        </div>
        <div style="color:#636e72; font-size:0.9rem; margin-bottom:14px;">
            Ближайшие пункты приема вторсырья в Алматы.
            <span style="color:#f39c12; font-size:0.8rem;">(demo-данные)</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = pd.read_csv(RECYCLING_CSV)
    df["color"] = df["type"].map(lambda t: _TYPE_COLORS.get(t, [100, 100, 100]))

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["lon", "lat"],
        get_fill_color="color",
        get_radius=350,
        pickable=True,
        opacity=0.85,
        radius_min_pixels=6,
        radius_max_pixels=20,
    )

    view_state = pdk.ViewState(
        latitude=43.2520,
        longitude=76.8950,
        zoom=11.5,
        pitch=0,
    )

    tooltip = {
        "html": """
            <div style="font-family:Inter,sans-serif;">
                <b>{name}</b><br/>
                <span style="color:#aaa;">Тип:</span> {type}<br/>
                <span style="color:#aaa;">Адрес:</span> {address}
            </div>
        """,
        "style": {
            "backgroundColor": "#1a1a2e",
            "color": "#eee",
            "borderRadius": "10px",
            "padding": "10px 14px",
            "fontSize": "13px",
        },
    }

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="light",
    )

    st.pydeck_chart(deck, use_container_width=True, height=420)

    # Legend
    legend_items = "".join(
        f'<div style="display:flex; align-items:center; gap:6px; font-size:0.83rem; color:#555;">'
        f'<div style="width:12px; height:12px; border-radius:50%; '
        f'background:rgb({c[0]},{c[1]},{c[2]});"></div>{t}</div>'
        for t, c in _TYPE_COLORS.items()
    )
    st.markdown(
        f"""<div style="display:flex; gap:16px; justify-content:center; margin:10px 0;
                    flex-wrap:wrap;">{legend_items}</div>""",
        unsafe_allow_html=True,
    )

    # Point list
    with st.expander("📍 Список пунктов"):
        for _, row in df.iterrows():
            st.markdown(f"**{row['name']}** — {row['type']} — {row['address']}")
