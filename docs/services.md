# Сервисы (бизнес-логика)

Все сервисы расположены в `backend/services/`.

---

## data_loader.py

Загрузка CSV-данных с парсингом дат.

```python
load_transport() -> pd.DataFrame
load_ecology() -> pd.DataFrame
```

Путь к данным: `backend/data/`.

---

## transport_service.py

KPI и агрегации транспортных данных.

### Функции

| Функция | Возвращает | Описание |
|---------|-----------|----------|
| `get_transport_kpis(df)` | `{avg_speed, avg_congestion, total_incidents}` | Средние показатели по всем данным |
| `get_transport_status(avg_congestion)` | `"normal" / "warning" / "critical"` | Статус по загруженности |
| `get_congestion_by_time(df)` | DataFrame | Загруженность, сгруппированная по timestamp |
| `get_congestion_by_district(df)` | DataFrame | Загруженность по районам (desc) |
| `get_district_stats(df)` | DataFrame | Полная статистика по каждому району |

### Логика статуса

```
congestion < 50  → "normal"
50 ≤ congestion < 80  → "warning"
congestion ≥ 80  → "critical"
```

---

## ecology_service.py

KPI и агрегации экологических данных.

### Функции

| Функция | Возвращает | Описание |
|---------|-----------|----------|
| `get_ecology_kpis(df)` | `{avg_aqi, avg_pm25, avg_pm10}` | Средние показатели |
| `get_ecology_status(avg_aqi)` | `"normal" / "warning" / "critical"` | Статус по AQI |
| `get_aqi_by_time(df)` | DataFrame | AQI, сгруппированный по timestamp |
| `get_aqi_by_district(df)` | DataFrame | AQI по районам (desc) |
| `get_district_stats(df)` | DataFrame | Полная статистика по каждому району |

### Логика статуса

```
AQI ≤ 50  → "normal"
50 < AQI ≤ 100  → "warning"
AQI > 100  → "critical"
```

---

## anomaly_detector.py

Обнаружение проблем в данных.

### Функции

```python
detect_transport_issues(df) -> list[dict]
detect_ecology_issues(df) -> list[dict]
```

### Формат issue

```json
{
  "type": "Транспорт",
  "district": "Бостандыкский",
  "timestamp": "2026-03-21 17:00:00",
  "severity": "critical",
  "description": "Загруженность 92%, скорость 15 км/ч, 5 инцидентов"
}
```

### Пороговые значения (транспорт)

| Показатель | Норма | Внимание | Критично |
|---|---|---|---|
| Загруженность | < 50% | 50–80% | ≥ 80% |
| Средняя скорость | > 25 км/ч | — | < 25 км/ч (усиливает) |
| Инциденты | < 3 | — | ≥ 3 (усиливает) |

### Пороговые значения (экология)

| Показатель | Норма | Внимание | Критично |
|---|---|---|---|
| AQI | ≤ 50 | 51–100 | > 100 |
| PM2.5 | ≤ 35 | — | > 35 (усиливает) |
| PM10 | ≤ 50 | — | > 50 (усиливает) |

---

## combined_analysis.py

Связь транспорта и экологии.

### Функции

```python
get_combined_data(transport_df, ecology_df) -> pd.DataFrame
detect_combined_issues(transport_df, ecology_df) -> list[dict]
```

### Risk Score

```
risk_score = avg_congestion × 0.4 + avg_aqi × 0.6
```

Отсортировано по `risk_score` (desc).

### Комбинированные проблемы

Фиксируются когда в одном районе и в одно время:
- **Загруженность ≥ 80%** И **AQI > 100**

Severity всегда `"critical"`, type = `"Комбинированная"`.

---

## ai_service.py

AI-сервис с двумя режимами работы.

### Функции

| Функция | Описание |
|---------|----------|
| `build_ai_insight(transport_kpis, ecology_kpis, all_issues, combined_issues)` | Генерация полного AI-анализа |
| `ask_assistant(question, city_context)` | Ответ на вопрос пользователя |
| `explain_impact(impact_data, city_context)` | AI-интерпретация экологического следа |

### Режим OpenAI

- Модель: `gpt-4o-mini` (настраивается через `OPENAI_MODEL`)
- Timeout: 15 секунд
- System prompt на русском языке с контекстом города

### Fallback (rule-based)

Если OpenAI API недоступен:
- `build_ai_insight` — логика на основе пороговых значений
- `ask_assistant` — keyword matching по категориям вопросов
- `explain_impact` — шаблонные ответы по уровню impact

### Risk Score (в ai_service)

```
base_risk = avg_congestion × 0.35
         + avg_aqi × 0.35
         + critical_count × 3
         + combined_count × 5

risk_score = clamp(0, 100, round(base_risk))
```

### Формат AI Insight

```json
{
  "summary": "string",
  "severity": "normal | warning | critical",
  "what_is_happening": "string",
  "why_critical": "string",
  "top_district": "string | null",
  "risk_score": 0-100,
  "recommendations": [{"priority", "type", "district", "text"}],
  "total_issues": 227,
  "critical_count": 6,
  "warning_count": 120,
  "combined_count": 0,
  "ai_powered": true/false
}
```

---

## user_impact_service.py

Расчет персонального экологического следа.

### Функция

```python
calculate_impact(fuel_type, engine_volume, daily_km) -> dict
```

### Коэффициенты выброса CO₂ (г/км)

| Топливо | 1.0 л | 1.6 л | 2.0 л | 3.0 л | 4.0 л |
|---------|-------|-------|-------|-------|-------|
| Бензин | 120 | 155 | 190 | 260 | 320 |
| Дизель | 100 | 130 | 160 | 210 | 260 |
| Газ (LPG) | 105 | 138 | 168 | 230 | 280 |
| Гибрид | 60 | 85 | 110 | 155 | 200 |
| Электро | 0 | 0 | 0 | 0 | 0 |

### Формулы

```
co2_daily_kg = emission_g_km × daily_km / 1000
co2_monthly  = co2_daily_kg × 30
co2_yearly   = co2_daily_kg × 365

ratio = co2_daily_kg / 5.5  (среднее по Алматы)
impact_score = clamp(0, 100, round(ratio × 50))
comparison = (ratio - 1) × 100  (% отклонения от среднего)
```

### Уровни

| Score | Уровень | Описание |
|-------|---------|----------|
| 0–29 | `low` | Ниже среднего |
| 30–59 | `medium` | Около среднего |
| 60–100 | `high` | Выше среднего |

---

## Константы (utils/constants.py)

```python
# Транспорт
TRANSPORT_CONGESTION_NORMAL = 50
TRANSPORT_CONGESTION_WARNING = 80
TRANSPORT_SPEED_CRITICAL = 25
TRANSPORT_INCIDENTS_HIGH = 3

# Экология
ECOLOGY_AQI_NORMAL = 50
ECOLOGY_AQI_WARNING = 100

# Статусы
STATUS_NORMAL = "normal"
STATUS_WARNING = "warning"
STATUS_CRITICAL = "critical"

# Цвета
STATUS_COLORS = {
    "normal": "#2ecc71",
    "warning": "#f39c12",
    "critical": "#e74c3c",
}

# Лейблы
STATUS_LABELS = {
    "normal": "Норма",
    "warning": "Внимание",
    "critical": "Критично",
}
```
