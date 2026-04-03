"""
FastAPI backend for CityPulse AI.
Wraps existing Python services as REST API endpoints.
"""

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

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
from services.user_impact_service import calculate_impact, FUEL_TYPES, ENGINE_VOLUMES
from utils.constants import STATUS_CRITICAL, STATUS_WARNING

app = FastAPI(title="CityPulse AI API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parent / "data"

# --- Load data once at startup ---
transport_df = load_transport()
ecology_df = load_ecology()


def _compute_all():
    """Compute all derived data. Cached at module level."""
    t_kpis = get_transport_kpis(transport_df)
    e_kpis = get_ecology_kpis(ecology_df)
    t_status = get_transport_status(t_kpis["avg_congestion"])
    e_status = get_ecology_status(e_kpis["avg_aqi"])

    t_issues = detect_transport_issues(transport_df)
    e_issues = detect_ecology_issues(ecology_df)
    c_issues = detect_combined_issues(transport_df, ecology_df)
    all_issues = t_issues + e_issues + c_issues

    critical_count = sum(1 for i in all_issues if i["severity"] == STATUS_CRITICAL)
    warning_count = sum(1 for i in all_issues if i["severity"] == STATUS_WARNING)
    city_status = (
        STATUS_CRITICAL
        if critical_count > 0
        else STATUS_WARNING
        if warning_count > 0
        else "normal"
    )

    combined_df = get_combined_data(transport_df, ecology_df)
    ai_insight = build_ai_insight(
        transport_kpis=t_kpis,
        ecology_kpis=e_kpis,
        all_issues=all_issues,
        combined_issues=c_issues,
    )

    # Serialize timestamps
    for issue in all_issues:
        issue["timestamp"] = str(issue["timestamp"])
    for issue in c_issues:
        issue["timestamp"] = str(issue["timestamp"])

    return {
        "t_kpis": t_kpis,
        "e_kpis": e_kpis,
        "t_status": t_status,
        "e_status": e_status,
        "all_issues": all_issues,
        "c_issues": c_issues,
        "critical_count": critical_count,
        "warning_count": warning_count,
        "city_status": city_status,
        "combined_df": combined_df,
        "ai_insight": ai_insight,
    }


_cache = _compute_all()


def _get_city_context():
    return {
        **_cache["ai_insight"],
        "avg_aqi": _cache["e_kpis"]["avg_aqi"],
        "avg_pm25": _cache["e_kpis"]["avg_pm25"],
        "avg_congestion": _cache["t_kpis"]["avg_congestion"],
        "avg_speed": _cache["t_kpis"]["avg_speed"],
    }


# ─── Overview (new primary endpoint) ───────────────────────────

def _district_status(risk_score: float) -> str:
    if risk_score >= 60:
        return STATUS_CRITICAL
    if risk_score >= 35:
        return STATUS_WARNING
    return "normal"


def _district_recommendation(status: str, district: str) -> str:
    if status == STATUS_CRITICAL:
        return f"Избегайте {district} в часы пик. Высокая загрузка дорог и загрязнение воздуха."
    if status == STATUS_WARNING:
        return f"Будьте внимательны в {district}. Умеренная нагрузка на транспорт и воздух."
    return f"{district} — комфортный район для поездок и прогулок."


@app.get("/api/overview")
def get_overview():
    c = _cache
    combined = c["combined_df"]

    # Build district map data
    districts_data = []
    for _, row in combined.iterrows():
        name = row["district"]
        risk = round(row["risk_score"], 1)
        status = _district_status(risk)
        district_issues = [i for i in c["all_issues"] if i["district"] == name]
        critical_issues = [i for i in district_issues if i["severity"] == STATUS_CRITICAL]

        districts_data.append({
            "district": name,
            "avg_congestion": round(row["avg_congestion"], 1),
            "avg_aqi": round(row["avg_aqi"], 1),
            "avg_speed": round(row["avg_speed"], 1),
            "risk_score": risk,
            "status": status,
            "issue_count": len(district_issues),
            "critical_count": len(critical_issues),
            "recommendation": _district_recommendation(status, name),
        })

    districts_data.sort(key=lambda d: d["risk_score"], reverse=True)

    # Top 5 critical alerts
    critical_alerts = [
        i for i in c["all_issues"] if i["severity"] == STATUS_CRITICAL
    ][:5]

    # Top 3 recommendations
    recs = c["ai_insight"].get("recommendations", [])
    top_recs = recs[:3]

    # Safe districts (lowest risk)
    safe = [d for d in districts_data if d["status"] == "normal"]

    insight = c["ai_insight"]

    return {
        "city_status": c["city_status"],
        "risk_score": insight.get("risk_score", 0),
        "top_kpis": {
            "avg_congestion": c["t_kpis"]["avg_congestion"],
            "avg_aqi": c["e_kpis"]["avg_aqi"],
            "critical_count": c["critical_count"],
            "risk_score": insight.get("risk_score", 0),
        },
        "summary": insight.get("summary", ""),
        "severity": insight.get("severity", "normal"),
        "what_is_happening": insight.get("what_is_happening", ""),
        "why_critical": insight.get("why_critical", ""),
        "ai_powered": insight.get("ai_powered", False),
        "districts": districts_data,
        "top_problem_districts": districts_data[:3],
        "top_safe_districts": safe[:3],
        "critical_alerts": critical_alerts,
        "recommendations": top_recs,
        "total_issues": len(c["all_issues"]),
        "warning_count": c["warning_count"],
        "combined_count": len(c["c_issues"]),
    }


# ─── Legacy dashboard ──────────────────────────────────────────

@app.get("/api/dashboard")
def get_dashboard():
    c = _cache
    return {
        "city_status": c["city_status"],
        "total_issues": len(c["all_issues"]),
        "critical_count": c["critical_count"],
        "transport": {"kpis": c["t_kpis"], "status": c["t_status"]},
        "ecology": {"kpis": c["e_kpis"], "status": c["e_status"]},
        "ai_insight": c["ai_insight"],
        "issues": c["all_issues"],
        "combined_issues": c["c_issues"],
    }


# ─── Transport ─────────────────────────────────────────────────

@app.get("/api/transport/congestion-by-time")
def get_transport_congestion_by_time():
    return get_congestion_by_time(transport_df).to_dict(orient="records")


@app.get("/api/transport/congestion-by-district")
def get_transport_congestion_by_district():
    return get_congestion_by_district(transport_df).to_dict(orient="records")


# ─── Ecology ──────────────────────────────────────────────────

@app.get("/api/ecology/aqi-by-time")
def get_ecology_aqi_by_time():
    return get_aqi_by_time(ecology_df).to_dict(orient="records")


@app.get("/api/ecology/aqi-by-district")
def get_ecology_aqi_by_district():
    return get_aqi_by_district(ecology_df).to_dict(orient="records")


# ─── Combined ─────────────────────────────────────────────────

@app.get("/api/combined")
def get_combined():
    return _cache["combined_df"].to_dict(orient="records")


# ─── Geo & recycling ──────────────────────────────────────────

@app.get("/api/geojson")
def get_geojson():
    with open(DATA_DIR / "almaty_districts.geojson", "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/recycling")
def get_recycling():
    return pd.read_csv(DATA_DIR / "recycling_points.csv").to_dict(orient="records")


# ─── AI Assistant ──────────────────────────────────────────────

class AssistantRequest(BaseModel):
    question: str


@app.post("/api/assistant")
def post_assistant(req: AssistantRequest):
    answer = ask_assistant(req.question, _get_city_context())
    return {"answer": answer}


# ─── Impact calculator ────────────────────────────────────────

class ImpactRequest(BaseModel):
    fuel_type: str
    engine_volume: float
    daily_km: float


@app.post("/api/impact")
def post_impact(req: ImpactRequest):
    result = calculate_impact(req.fuel_type, req.engine_volume, req.daily_km)
    explanation = explain_impact(result, _get_city_context())
    return {**result, "explanation": explanation}


@app.get("/api/impact/options")
def get_impact_options():
    return {"fuel_types": FUEL_TYPES, "engine_volumes": ENGINE_VOLUMES}
