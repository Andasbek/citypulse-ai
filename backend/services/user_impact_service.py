"""
Сервис расчета личного экологического воздействия.

Принимает параметры автомобиля пользователя и рассчитывает оценочный
Air Impact Score — индекс вклада в загрязнение воздуха.
"""

# Средние коэффициенты выброса CO2 (г/км) по типу топлива и объему двигателя
_EMISSION_FACTORS = {
    "Бензин": {1.0: 120, 1.4: 140, 1.6: 155, 1.8: 170, 2.0: 190, 2.5: 220, 3.0: 260, 3.5: 290, 4.0: 320},
    "Дизель": {1.0: 100, 1.4: 115, 1.6: 130, 1.8: 145, 2.0: 160, 2.5: 185, 3.0: 210, 3.5: 235, 4.0: 260},
    "Газ (LPG)": {1.0: 105, 1.4: 125, 1.6: 138, 1.8: 150, 2.0: 168, 2.5: 195, 3.0: 230, 3.5: 255, 4.0: 280},
    "Гибрид": {1.0: 60, 1.4: 75, 1.6: 85, 1.8: 95, 2.0: 110, 2.5: 130, 3.0: 155, 3.5: 175, 4.0: 200},
    "Электро": {1.0: 0, 1.4: 0, 1.6: 0, 1.8: 0, 2.0: 0, 2.5: 0, 3.0: 0, 3.5: 0, 4.0: 0},
}

# Средний пробег жителя Алматы (оценочно)
_AVG_DAILY_KM = 35
_AVG_CO2_DAILY_KG = 5.5  # ~155 г/км * 35 км / 1000


def _get_emission_factor(fuel_type: str, engine_volume: float) -> float:
    """Get emission factor (g/km) for given fuel type and engine volume."""
    factors = _EMISSION_FACTORS.get(fuel_type, _EMISSION_FACTORS["Бензин"])
    volumes = sorted(factors.keys())
    # Find closest volume
    closest = min(volumes, key=lambda v: abs(v - engine_volume))
    return factors[closest]


def calculate_impact(fuel_type: str, engine_volume: float, daily_km: float) -> dict:
    """
    Calculate personal Air Impact Score.

    Returns dict with:
    - co2_per_km: grams of CO2 per km
    - co2_daily_kg: daily CO2 in kg
    - co2_monthly_kg: monthly CO2 in kg
    - co2_yearly_kg: yearly CO2 in kg
    - impact_score: 0-100 score relative to city average
    - comparison: how much more/less than average
    - level: low / medium / high
    """
    emission_g_km = _get_emission_factor(fuel_type, engine_volume)
    co2_daily_kg = emission_g_km * daily_km / 1000
    co2_monthly_kg = co2_daily_kg * 30
    co2_yearly_kg = co2_daily_kg * 365

    # Impact score: ratio to city average, scaled 0-100
    ratio = co2_daily_kg / _AVG_CO2_DAILY_KG if _AVG_CO2_DAILY_KG > 0 else 0
    impact_score = min(100, max(0, round(ratio * 50)))

    if impact_score < 30:
        level = "low"
    elif impact_score < 60:
        level = "medium"
    else:
        level = "high"

    comparison = round((ratio - 1) * 100, 1)

    return {
        "fuel_type": fuel_type,
        "engine_volume": engine_volume,
        "daily_km": daily_km,
        "co2_per_km": emission_g_km,
        "co2_daily_kg": round(co2_daily_kg, 2),
        "co2_monthly_kg": round(co2_monthly_kg, 1),
        "co2_yearly_kg": round(co2_yearly_kg, 1),
        "impact_score": impact_score,
        "comparison": comparison,
        "level": level,
    }


FUEL_TYPES = list(_EMISSION_FACTORS.keys())
ENGINE_VOLUMES = [1.0, 1.4, 1.6, 1.8, 2.0, 2.5, 3.0, 3.5, 4.0]
