import json
from pathlib import Path

import pydeck as pdk
import streamlit as st
import pandas as pd


GEOJSON_PATH = Path(__file__).resolve().parent.parent / "data" / "almaty_districts.geojson"

# District centroids for labels and issue points
DISTRICT_CENTERS = {
    "Бостандыкский": [76.9100, 43.2330],
    "Алмалинский": [76.9430, 43.2680],
    "Медеуский": [76.9800, 43.2430],
    "Ауэзовский": [76.8530, 43.2600],
    "Наурызбайский": [76.7870, 43.2660],
}


def _risk_to_rgb(score: float) -> list[int]:
    """Map risk_score (0-100) to RGB color: green -> yellow -> red."""
    if score < 35:
        t = score / 35
        r = int(46 + (243 - 46) * t)
        g = int(204 + (156 - 204) * t)
        b = int(113 + (18 - 113) * t)
    else:
        t = min(1.0, (score - 35) / 65)
        r = int(243 + (231 - 243) * t)
        g = int(156 - 156 * t)
        b = int(18 - 18 * t)
    return [r, g, b]


def _build_geojson_with_risk(combined_df: pd.DataFrame) -> dict:
    """Merge risk data into GeoJSON properties."""
    with open(GEOJSON_PATH, encoding="utf-8") as f:
        geojson = json.load(f)

    risk_map = {}
    for _, row in combined_df.iterrows():
        risk_map[row["district"]] = {
            "risk_score": float(row["risk_score"]),
            "avg_congestion": round(float(row["avg_congestion"]), 1),
            "avg_aqi": round(float(row["avg_aqi"]), 1),
            "avg_speed": round(float(row["avg_speed"]), 1),
        }

    for feature in geojson["features"]:
        district = feature["properties"]["district"]
        data = risk_map.get(district, {})
        risk = data.get("risk_score", 0)
        rgb = _risk_to_rgb(risk)

        feature["properties"].update({
            "risk_score": data.get("risk_score", 0),
            "avg_congestion": data.get("avg_congestion", 0),
            "avg_aqi": data.get("avg_aqi", 0),
            "avg_speed": data.get("avg_speed", 0),
            "fill_r": rgb[0],
            "fill_g": rgb[1],
            "fill_b": rgb[2],
        })

    return geojson


def _build_issues_points(all_issues: list[dict]) -> pd.DataFrame:
    """Create a DataFrame of issue points for the ScatterplotLayer."""
    rows = []
    for issue in all_issues:
        center = DISTRICT_CENTERS.get(issue["district"])
        if not center:
            continue

        if issue["type"] == "Комбинированная":
            color = [231, 76, 60]
            radius = 500
        elif issue["severity"] == "critical":
            color = [230, 100, 50]
            radius = 380
        else:
            color = [243, 156, 18]
            radius = 280

        # Offset points slightly so they don't fully overlap
        import random
        random.seed(hash(f"{issue['district']}_{issue['timestamp']}_{issue['type']}"))
        lon_offset = random.uniform(-0.008, 0.008)
        lat_offset = random.uniform(-0.006, 0.006)

        rows.append({
            "lon": center[0] + lon_offset,
            "lat": center[1] + lat_offset,
            "color": color,
            "radius": radius,
            "district": issue["district"],
            "type": issue["type"],
            "severity": issue["severity"],
            "description": issue["description"],
        })

    return pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=["lon", "lat", "color", "radius", "district", "type", "severity", "description"]
    )


def _build_labels_data(combined_df: pd.DataFrame) -> pd.DataFrame:
    """Create label points for TextLayer."""
    rows = []
    for _, row in combined_df.iterrows():
        center = DISTRICT_CENTERS.get(row["district"])
        if not center:
            continue
        risk = float(row["risk_score"])
        rows.append({
            "lon": center[0],
            "lat": center[1],
            "text": f"{row['district']}\nРиск: {risk:.0f}",
            "size": 14 if risk > 60 else 12,
        })
    return pd.DataFrame(rows)


def render_city_map(combined_df: pd.DataFrame, all_issues: list[dict]):
    """Render the interactive pydeck map of Almaty districts."""

    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:10px; margin:20px 0 14px;">
            <span style="font-size:1.4rem;">🗺️</span>
            <span style="font-size:1.1rem; font-weight:700; color:#2d3436;">
                Карта города — распределение рисков по районам
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    geojson = _build_geojson_with_risk(combined_df)
    issues_df = _build_issues_points(all_issues)
    labels_df = _build_labels_data(combined_df)

    # Layer 1: District polygons colored by risk
    polygon_layer = pdk.Layer(
        "GeoJsonLayer",
        data=geojson,
        stroked=True,
        filled=True,
        pickable=True,
        opacity=0.55,
        get_fill_color="[properties.fill_r, properties.fill_g, properties.fill_b, 160]",
        get_line_color=[60, 60, 60, 200],
        line_width_min_pixels=2,
    )

    layers = [polygon_layer]

    # Layer 2: Issue points
    if not issues_df.empty:
        scatter_layer = pdk.Layer(
            "ScatterplotLayer",
            data=issues_df,
            get_position=["lon", "lat"],
            get_fill_color="color",
            get_radius="radius",
            pickable=True,
            opacity=0.7,
            radius_min_pixels=4,
            radius_max_pixels=18,
        )
        layers.append(scatter_layer)

    # Layer 3: District labels
    if not labels_df.empty:
        text_layer = pdk.Layer(
            "TextLayer",
            data=labels_df,
            get_position=["lon", "lat"],
            get_text="text",
            get_size="size",
            get_color=[30, 30, 30, 220],
            get_alignment_baseline="'center'",
            font_family="'Inter', 'Arial', sans-serif",
            font_weight=700,
            background=True,
            get_background_color=[255, 255, 255, 200],
            background_padding=[6, 4],
        )
        layers.append(text_layer)

    view_state = pdk.ViewState(
        latitude=43.2520,
        longitude=76.8950,
        zoom=11.2,
        pitch=0,
    )

    tooltip = {
        "html": """
            <div style="font-family:Inter,sans-serif; padding:4px 0;">
                <b style="font-size:14px;">{district}</b><br/>
                <span style="color:#aaa;">Тип:</span> {type}<br/>
                <span style="color:#aaa;">Критичность:</span> {severity}<br/>
                <span style="color:#aaa;">Описание:</span> {description}
            </div>
        """,
        "style": {
            "backgroundColor": "#1a1a2e",
            "color": "#eee",
            "border": "1px solid rgba(255,255,255,0.15)",
            "borderRadius": "10px",
            "padding": "10px 14px",
            "fontSize": "13px",
        },
    }

    deck = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="light",
    )

    st.pydeck_chart(deck, use_container_width=True, height=520)

    # Legend
    st.markdown(
        """
        <div style="display:flex; gap:20px; justify-content:center; margin:12px 0 6px;
                    flex-wrap:wrap;">
            <div style="display:flex; align-items:center; gap:6px; font-size:0.85rem; color:#555;">
                <div style="width:14px; height:14px; border-radius:3px; background:#2ecc71;"></div>
                Низкий риск (&lt;35)
            </div>
            <div style="display:flex; align-items:center; gap:6px; font-size:0.85rem; color:#555;">
                <div style="width:14px; height:14px; border-radius:3px; background:#f39c12;"></div>
                Средний риск (35–70)
            </div>
            <div style="display:flex; align-items:center; gap:6px; font-size:0.85rem; color:#555;">
                <div style="width:14px; height:14px; border-radius:3px; background:#e74c3c;"></div>
                Высокий риск (&gt;70)
            </div>
            <div style="display:flex; align-items:center; gap:6px; font-size:0.85rem; color:#555;">
                <div style="width:10px; height:10px; border-radius:50%; background:#e74c3c;"></div>
                Комбинированная проблема
            </div>
            <div style="display:flex; align-items:center; gap:6px; font-size:0.85rem; color:#555;">
                <div style="width:8px; height:8px; border-radius:50%; background:#e66432;"></div>
                Критическая проблема
            </div>
            <div style="display:flex; align-items:center; gap:6px; font-size:0.85rem; color:#555;">
                <div style="width:7px; height:7px; border-radius:50%; background:#f39c12;"></div>
                Предупреждение
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
