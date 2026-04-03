"""
AI-сервис — единая точка AI-логики проекта.

Использует OpenAI Responses API со Structured Outputs для генерации
структурированных ответов. При отсутствии API или ошибке автоматически
переключается на rule-based fallback.
"""

import json
import os
import logging
from collections import Counter

from utils.constants import STATUS_NORMAL, STATUS_WARNING, STATUS_CRITICAL

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def _is_llm_enabled() -> bool:
    return os.getenv("LLM_ENABLED", "true").lower() in ("true", "1", "yes")


def _get_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _get_timeout() -> int:
    try:
        return int(os.getenv("LLM_TIMEOUT", "15"))
    except ValueError:
        return 15


# ---------------------------------------------------------------------------
# OpenAI client (lazy init)
# ---------------------------------------------------------------------------

_openai_client = None


def _get_openai_client():
    """Lazy-init OpenAI client. Returns None if unavailable."""
    global _openai_client
    if _openai_client is not None:
        return _openai_client

    if not _is_llm_enabled():
        return None

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI
        _openai_client = OpenAI(api_key=api_key, timeout=_get_timeout())
        return _openai_client
    except Exception as e:
        logger.warning("OpenAI client init failed: %s", e)
        return None


# ---------------------------------------------------------------------------
# Structured Outputs schemas
# ---------------------------------------------------------------------------

CITY_SUMMARY_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "city_summary",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "Краткая сводка по ситуации в городе, 1-2 предложения",
                },
                "what_is_happening": {
                    "type": "string",
                    "description": "Что сейчас происходит в городе, 2-3 предложения",
                },
                "why_critical": {
                    "type": "string",
                    "description": "Почему ситуация важна, 1-2 предложения",
                },
                "severity": {
                    "type": "string",
                    "enum": ["normal", "warning", "critical"],
                    "description": "Уровень серьезности ситуации",
                },
                "top_district": {
                    "type": "string",
                    "description": "Самый проблемный район",
                },
                "recommendations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low"],
                            },
                            "type": {"type": "string"},
                            "district": {"type": "string"},
                            "text": {"type": "string"},
                        },
                        "required": ["priority", "type", "district", "text"],
                        "additionalProperties": False,
                    },
                    "description": "3-5 рекомендаций",
                },
            },
            "required": [
                "summary",
                "what_is_happening",
                "why_critical",
                "severity",
                "top_district",
                "recommendations",
            ],
            "additionalProperties": False,
        },
    },
}

ASSISTANT_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "assistant_response",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "answer": {
                    "type": "string",
                    "description": "Ответ на вопрос пользователя",
                },
                "related_districts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Районы, упомянутые в ответе",
                },
                "confidence": {
                    "type": "string",
                    "enum": ["high", "medium", "low"],
                    "description": "Уверенность в ответе",
                },
            },
            "required": ["answer", "related_districts", "confidence"],
            "additionalProperties": False,
        },
    },
}

IMPACT_EXPLAINER_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "impact_explanation",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "level": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Уровень воздействия",
                },
                "comparison_text": {
                    "type": "string",
                    "description": "Сравнение со средним по Алматы, 1 предложение",
                },
                "explanation": {
                    "type": "string",
                    "description": "Объяснение результата, 2-3 предложения",
                },
                "tips": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "2-3 совета по снижению экологического следа",
                },
            },
            "required": ["level", "comparison_text", "explanation", "tips"],
            "additionalProperties": False,
        },
    },
}


# ---------------------------------------------------------------------------
# OpenAI Responses API calls with Structured Outputs
# ---------------------------------------------------------------------------

def _call_structured(
    system_prompt: str,
    user_prompt: str,
    response_format: dict,
) -> dict | None:
    """Call OpenAI Responses API with structured output. Returns parsed dict or None."""
    client = _get_openai_client()
    if client is None:
        return None

    try:
        resp = client.responses.create(
            model=_get_model(),
            instructions=system_prompt,
            input=user_prompt,
            text={
                "format": response_format,
            },
            temperature=0.4,
            max_output_tokens=1200,
        )
        raw = resp.output_text
        return json.loads(raw)
    except Exception as e:
        logger.warning("OpenAI Responses API call failed: %s", e)
        return None


# ---------------------------------------------------------------------------
# Context builder
# ---------------------------------------------------------------------------

def _build_city_context_text(
    transport_kpis: dict,
    ecology_kpis: dict,
    all_issues: list[dict],
    combined_issues: list[dict],
    critical: list[dict],
    warnings: list[dict],
    top_district: str | None,
    risk_score: int,
) -> str:
    """Build compact text context from service data for LLM."""
    ctx = (
        f"=== Состояние Алматы ===\n"
        f"Транспорт: скорость {transport_kpis['avg_speed']} км/ч, "
        f"загруженность {transport_kpis['avg_congestion']}%, "
        f"инцидентов {transport_kpis['total_incidents']}.\n"
        f"Экология: AQI {ecology_kpis['avg_aqi']}, "
        f"PM2.5 {ecology_kpis['avg_pm25']}, PM10 {ecology_kpis['avg_pm10']}.\n"
        f"Проблемы: всего {len(all_issues)}, критических {len(critical)}, "
        f"предупреждений {len(warnings)}, комбинированных {len(combined_issues)}.\n"
        f"Risk Score: {risk_score}/100.\n"
        f"Наиболее проблемный район: {top_district or 'не определен'}.\n"
    )
    if combined_issues:
        districts = sorted({i["district"] for i in combined_issues})
        ctx += f"Комбинированные проблемы (транспорт + экология): {', '.join(districts)}.\n"

    if critical:
        by_district = {}
        for i in critical[:10]:
            d = i["district"]
            by_district.setdefault(d, []).append(i["description"])
        ctx += "Критические проблемы:\n"
        for d, descs in by_district.items():
            ctx += f"  {d}: {'; '.join(descs[:2])}\n"

    return ctx


# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------

CITY_SUMMARY_SYSTEM = (
    "Ты — AI-аналитик городской среды Алматы в платформе CityPulse AI.\n"
    "ПРАВИЛА:\n"
    "- Отвечай ТОЛЬКО на русском языке.\n"
    "- Используй ТОЛЬКО данные из переданного контекста. Не выдумывай цифры.\n"
    "- Пиши кратко, понятно, пригодно для дашборда.\n"
    "- В recommendations давай конкретные, actionable советы.\n"
    "- severity определяй строго по данным: если есть критические проблемы — 'critical', "
    "если только предупреждения — 'warning', иначе — 'normal'.\n"
    "- top_district — район с наибольшим количеством проблем."
)

ASSISTANT_SYSTEM = (
    "Ты — AI-ассистент платформы CityPulse AI для мониторинга городской среды Алматы.\n\n"
    "Платформа анализирует:\n"
    "- Транспорт: скорость, загруженность дорог, инциденты по районам\n"
    "- Экология: AQI, PM2.5, PM10 по районам\n"
    "- Комбинированный анализ связи транспорта и экологии\n"
    "- Карту города с уровнями риска\n"
    "- Личный экологический калькулятор\n"
    "- Рекомендации по прогулкам и маршрутам\n\n"
    "ПРАВИЛА:\n"
    "- Отвечай ТОЛЬКО на русском языке.\n"
    "- Используй ТОЛЬКО данные из контекста. Не выдумывай.\n"
    "- Кратко и по делу, 2-5 предложений.\n"
    "- related_districts — районы, о которых идет речь в ответе.\n"
    "- confidence: high — если ответ полностью основан на данных, "
    "medium — если частично, low — если вопрос выходит за рамки данных."
)

IMPACT_SYSTEM = (
    "Ты — экологический консультант платформы CityPulse AI.\n\n"
    "ПРАВИЛА:\n"
    "- Отвечай ТОЛЬКО на русском языке.\n"
    "- Используй ТОЛЬКО переданные данные.\n"
    "- explanation: объясни что означает impact score, 2-3 предложения.\n"
    "- comparison_text: сравни с средним по Алматы (5.5 кг CO₂/день), 1 предложение.\n"
    "- tips: 2-3 конкретных совета по снижению следа.\n"
    "- level: low (<30), medium (30-59), high (60+)."
)


# ---------------------------------------------------------------------------
# Public API: build_ai_insight
# ---------------------------------------------------------------------------

def build_ai_insight(
    transport_kpis: dict,
    ecology_kpis: dict,
    all_issues: list[dict],
    combined_issues: list[dict],
) -> dict:
    """Build AI-powered city insight. Falls back to rule-based if LLM unavailable."""

    critical = [i for i in all_issues if i["severity"] == STATUS_CRITICAL]
    warnings = [i for i in all_issues if i["severity"] == STATUS_WARNING]

    top_district = _find_top_district(all_issues, combined_issues)
    risk_score = _compute_risk_score(transport_kpis, ecology_kpis, critical, combined_issues)
    severity = _determine_severity(combined_issues, critical, warnings)

    # Try OpenAI Responses API with Structured Outputs
    context_text = _build_city_context_text(
        transport_kpis, ecology_kpis, all_issues, combined_issues,
        critical, warnings, top_district, risk_score,
    )

    ai_result = _call_structured(
        CITY_SUMMARY_SYSTEM,
        context_text,
        CITY_SUMMARY_SCHEMA,
    )

    if ai_result and "summary" in ai_result and "recommendations" in ai_result:
        ai_result.update({
            "top_district": ai_result.get("top_district", top_district),
            "risk_score": risk_score,
            "severity": severity,  # keep computed severity as ground truth
            "total_issues": len(all_issues),
            "critical_count": len(critical),
            "warning_count": len(warnings),
            "combined_count": len(combined_issues),
            "ai_powered": True,
        })
        return ai_result

    # Fallback to rule-based
    return {
        "summary": _build_summary(severity, top_district, combined_issues, critical),
        "severity": severity,
        "what_is_happening": _build_what_is_happening(
            transport_kpis, ecology_kpis, all_issues, critical, warnings,
        ),
        "why_critical": _build_why_critical(severity, combined_issues, critical, top_district),
        "top_district": top_district,
        "risk_score": risk_score,
        "recommendations": _build_recommendations(
            severity, all_issues, combined_issues, critical, top_district,
        ),
        "total_issues": len(all_issues),
        "critical_count": len(critical),
        "warning_count": len(warnings),
        "combined_count": len(combined_issues),
        "ai_powered": False,
    }


# ---------------------------------------------------------------------------
# Public API: ask_assistant
# ---------------------------------------------------------------------------

def ask_assistant(question: str, city_context: dict) -> str:
    """Answer user question via OpenAI or fallback."""
    context_text = (
        f"Текущее состояние города:\n"
        f"- Risk Score: {city_context.get('risk_score', '?')}/100\n"
        f"- Severity: {city_context.get('severity', '?')}\n"
        f"- Всего проблем: {city_context.get('total_issues', '?')}\n"
        f"- Критических: {city_context.get('critical_count', '?')}\n"
        f"- Комбинированных: {city_context.get('combined_count', '?')}\n"
        f"- Проблемный район: {city_context.get('top_district', '?')}\n"
        f"- AQI: {city_context.get('avg_aqi', '?')}\n"
        f"- PM2.5: {city_context.get('avg_pm25', '?')}\n"
        f"- Загруженность: {city_context.get('avg_congestion', '?')}%\n"
        f"- Скорость: {city_context.get('avg_speed', '?')} км/ч\n"
        f"- Сводка: {city_context.get('summary', '')}\n"
    )

    user_prompt = f"{context_text}\nВопрос пользователя: {question}"

    ai_result = _call_structured(
        ASSISTANT_SYSTEM,
        user_prompt,
        ASSISTANT_SCHEMA,
    )

    if ai_result and "answer" in ai_result:
        return ai_result["answer"]

    return _fallback_assistant(question, city_context)


# ---------------------------------------------------------------------------
# Public API: explain_impact
# ---------------------------------------------------------------------------

def explain_impact(impact_data: dict, city_context: dict) -> str:
    """Generate AI explanation for personal impact score."""
    user_prompt = (
        f"Результат расчета экологического следа:\n"
        f"- Тип топлива: {impact_data.get('fuel_type', '?')}\n"
        f"- Объем двигателя: {impact_data.get('engine_volume', '?')} л\n"
        f"- Пробег в день: {impact_data.get('daily_km', '?')} км\n"
        f"- CO₂ на км: {impact_data.get('co2_per_km', '?')} г\n"
        f"- CO₂ в день: {impact_data.get('co2_daily_kg', '?')} кг\n"
        f"- CO₂ в год: {impact_data.get('co2_yearly_kg', '?')} кг\n"
        f"- Impact Score: {impact_data.get('impact_score', '?')}/100\n"
        f"- Уровень: {impact_data.get('level', '?')}\n"
        f"- Сравнение: {impact_data.get('comparison', '?')}% к среднему\n"
        f"- Средний CO₂/день по Алматы: 5.5 кг\n"
        f"- Текущий AQI города: {city_context.get('avg_aqi', '?')}\n"
    )

    ai_result = _call_structured(
        IMPACT_SYSTEM,
        user_prompt,
        IMPACT_EXPLAINER_SCHEMA,
    )

    if ai_result and "explanation" in ai_result:
        parts = [ai_result["explanation"]]
        if ai_result.get("comparison_text"):
            parts.append(ai_result["comparison_text"])
        if ai_result.get("tips"):
            parts.append("Советы: " + "; ".join(ai_result["tips"]) + ".")
        return " ".join(parts)

    return _fallback_explain_impact(impact_data)


# ---------------------------------------------------------------------------
# Fallback: assistant
# ---------------------------------------------------------------------------

def _fallback_assistant(question: str, ctx: dict) -> str:
    q = question.lower()

    if any(w in q for w in ["что умеет", "возможности", "функци", "что делает", "что может"]):
        return (
            "CityPulse AI — платформа мониторинга городской среды Алматы. "
            "Возможности:\n"
            "- Анализ транспортной ситуации (скорость, загруженность, инциденты)\n"
            "- Экологический мониторинг (AQI, PM2.5, PM10)\n"
            "- Комбинированный анализ связи транспорта и экологии\n"
            "- Интерактивная карта города с уровнями риска\n"
            "- Личный экологический калькулятор\n"
            "- AI-рекомендации по прогулкам и маршрутам"
        )

    if any(w in q for w in ["воздух", "грязн", "чист", "aqi", "экологи", "pm"]):
        return (
            f"Средний AQI по городу: {ctx.get('avg_aqi', '?')}. "
            f"Наиболее проблемный район — {ctx.get('top_district', '?')}. "
            f"Уровень риска: {ctx.get('risk_score', '?')}/100."
        )

    if any(w in q for w in ["пробк", "загруж", "транспорт", "скорость", "дорог"]):
        return (
            f"Средняя загруженность: {ctx.get('avg_congestion', '?')}%, "
            f"скорость: {ctx.get('avg_speed', '?')} км/ч. "
            f"Критических проблем: {ctx.get('critical_count', '?')}."
        )

    if any(w in q for w in ["район", "где опасно", "где плохо", "проблемн", "рискован"]):
        return (
            f"Наиболее проблемный район: {ctx.get('top_district', 'не определен')}. "
            f"Всего {ctx.get('total_issues', '?')} проблем, "
            f"из них {ctx.get('critical_count', '?')} критических."
        )

    if any(w in q for w in ["состояни", "ситуаци", "что происходит", "как город"]):
        return (
            f"Risk Score: {ctx.get('risk_score', '?')}/100. "
            f"{ctx.get('summary', 'Данные загружаются...')}"
        )

    if any(w in q for w in ["прогулк", "гулять", "бегать", "спорт"]):
        risk = ctx.get("risk_score", 50)
        if risk > 70:
            return (
                "Сейчас не лучшее время для прогулок. "
                f"Избегайте района {ctx.get('top_district', '?')}."
            )
        if risk > 45:
            return "Прогулки возможны, но избегайте районов с загруженными дорогами."
        return "Обстановка благоприятна для прогулок."

    if any(w in q for w in ["будущ", "план", "roadmap", "скоро", "новые функци"]):
        return (
            "Планы CityPulse AI:\n"
            "- Real-time данные с датчиков\n"
            "- Push-уведомления при ухудшении\n"
            "- Расширение на другие города Казахстана"
        )

    return (
        f"Я — AI-ассистент CityPulse AI. Risk Score города: "
        f"{ctx.get('risk_score', '?')}/100. "
        "Спросите о состоянии города, районах, прогулках или возможностях платформы."
    )


# ---------------------------------------------------------------------------
# Fallback: impact explainer
# ---------------------------------------------------------------------------

def _fallback_explain_impact(data: dict) -> str:
    score = data.get("impact_score", 0)
    co2 = data.get("co2_daily_kg", 0)
    comparison = data.get("comparison", 0)

    if score < 30:
        level_text = "низкий"
        advice = "Ваш вклад в загрязнение минимален."
    elif score < 60:
        level_text = "умеренный"
        advice = "Рассмотрите сокращение поездок или переход на общественный транспорт."
    else:
        level_text = "высокий"
        advice = "Рекомендуется сократить использование автомобиля."

    comp_text = (
        f"Это {'на ' + str(abs(comparison)) + '% выше' if comparison > 0 else 'на ' + str(abs(comparison)) + '% ниже'} "
        "среднего по Алматы (5.5 кг CO₂/день)."
    )

    return (
        f"Impact Score: {score}/100 ({level_text}). "
        f"Ваш автомобиль выбрасывает {co2:.1f} кг CO₂ в день. "
        f"{comp_text} {advice} "
        "Советы: объединяйте поездки; используйте общественный транспорт; "
        "рассмотрите велосипед для коротких дистанций."
    )


# ---------------------------------------------------------------------------
# Rule-based helpers
# ---------------------------------------------------------------------------

def _find_top_district(
    all_issues: list[dict],
    combined_issues: list[dict],
) -> str | None:
    if combined_issues:
        counts = Counter(i["district"] for i in combined_issues)
        return counts.most_common(1)[0][0]
    if all_issues:
        critical = [i for i in all_issues if i["severity"] == STATUS_CRITICAL]
        pool = critical if critical else all_issues
        counts = Counter(i["district"] for i in pool)
        return counts.most_common(1)[0][0]
    return None


def _compute_risk_score(
    transport_kpis: dict,
    ecology_kpis: dict,
    critical: list[dict],
    combined_issues: list[dict],
) -> int:
    base = transport_kpis["avg_congestion"] * 0.35 + ecology_kpis["avg_aqi"] * 0.35
    base += len(critical) * 3
    base += len(combined_issues) * 5
    return min(100, max(0, round(base)))


def _determine_severity(
    combined_issues: list[dict],
    critical: list[dict],
    warnings: list[dict],
) -> str:
    if combined_issues or critical:
        return STATUS_CRITICAL
    if warnings:
        return STATUS_WARNING
    return STATUS_NORMAL


def _build_what_is_happening(t_kpis, e_kpis, all_issues, critical, warnings) -> str:
    if not all_issues:
        return "Городская обстановка в пределах нормы."
    return (
        f"Зафиксировано {len(all_issues)} проблем: "
        f"{len(critical)} критических, {len(warnings)} предупреждений. "
        f"Скорость {t_kpis['avg_speed']} км/ч, загруженность {t_kpis['avg_congestion']}%. "
        f"AQI {e_kpis['avg_aqi']}, PM2.5 {e_kpis['avg_pm25']}."
    )


def _build_why_critical(severity, combined_issues, critical, top_district) -> str:
    if severity == STATUS_NORMAL:
        return "Ситуация стабильная."
    if combined_issues:
        districts = sorted({i["district"] for i in combined_issues})
        return (
            f"В {', '.join(districts)} одновременно высокая транспортная нагрузка "
            "и превышение AQI. Требуется межведомственное реагирование."
        )
    if critical:
        return f"Критические проблемы в районе {top_district}. Требуется вмешательство."
    return "Отклонения от нормы требуют наблюдения."


def _build_summary(severity, top_district, combined_issues, critical) -> str:
    if severity == STATUS_NORMAL:
        return "Городская обстановка стабильна."
    if combined_issues:
        districts = sorted({i["district"] for i in combined_issues})
        return f"В {', '.join(districts)} критическая ситуация: пробки и загрязнение воздуха."
    if critical and top_district:
        return f"В {top_district} зафиксированы критические отклонения."
    return "В ряде районов отклонения от нормы. Ситуация под контролем."


def _build_recommendations(severity, all_issues, combined_issues, critical, top_district) -> list[dict]:
    recs = []

    if severity == STATUS_NORMAL:
        recs.append({"priority": "low", "type": "Общая", "district": "-", "text": "Продолжать стандартный мониторинг."})
        return recs

    seen = set()
    for issue in combined_issues:
        d = issue["district"]
        if d not in seen:
            seen.add(d)
            recs.append({"priority": "high", "type": "Комбинированная", "district": d,
                         "text": f"Перераспределить транспортный поток в {d}, усилить экомониторинг."})

    for issue in critical:
        d = issue["district"]
        if d not in seen:
            seen.add(d)
            t = issue["type"]
            recs.append({"priority": "high", "type": t, "district": d,
                         "text": f"Срочное реагирование по направлению '{t}' в {d}."})

    warning_districts = {i["district"] for i in all_issues if i["severity"] == STATUS_WARNING and i["district"] not in seen}
    for d in sorted(warning_districts):
        recs.append({"priority": "medium", "type": "Мониторинг", "district": d,
                     "text": f"Усилить наблюдение в {d}."})

    return recs
