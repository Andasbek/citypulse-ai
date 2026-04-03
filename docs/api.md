# REST API

Базовый URL: `http://localhost:8000`

## Обзор эндпоинтов

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/dashboard` | Полные данные дашборда |
| GET | `/api/transport/congestion-by-time` | Загруженность по времени |
| GET | `/api/transport/congestion-by-district` | Загруженность по районам |
| GET | `/api/ecology/aqi-by-time` | AQI по времени |
| GET | `/api/ecology/aqi-by-district` | AQI по районам |
| GET | `/api/combined` | Комбинированный анализ по районам |
| GET | `/api/geojson` | GeoJSON полигоны районов |
| GET | `/api/recycling` | Пункты переработки |
| POST | `/api/assistant` | AI-ассистент (вопрос-ответ) |
| POST | `/api/impact` | Расчет экологического следа |
| GET | `/api/impact/options` | Варианты для калькулятора |

---

## GET /api/dashboard

Главный эндпоинт — возвращает все данные для дашборда одним запросом.

**Ответ:**

```json
{
  "city_status": "critical",
  "total_issues": 227,
  "critical_count": 6,
  "transport": {
    "kpis": {
      "avg_speed": 47.8,
      "avg_congestion": 30.0,
      "total_incidents": 156
    },
    "status": "normal"
  },
  "ecology": {
    "kpis": {
      "avg_aqi": 41.7,
      "avg_pm25": 15.2,
      "avg_pm10": 28.6
    },
    "status": "normal"
  },
  "ai_insight": {
    "summary": "Описание текущей ситуации...",
    "severity": "critical",
    "what_is_happening": "Детали происходящего...",
    "why_critical": "Почему это важно...",
    "top_district": "Медеуский",
    "risk_score": 45,
    "recommendations": [
      {
        "priority": "high",
        "type": "Транспорт",
        "district": "Медеуский",
        "text": "Рекомендация..."
      }
    ],
    "total_issues": 227,
    "critical_count": 6,
    "warning_count": 120,
    "combined_count": 0,
    "ai_powered": false
  },
  "issues": [
    {
      "type": "Транспорт",
      "district": "Бостандыкский",
      "timestamp": "2026-03-21 17:00:00",
      "severity": "critical",
      "description": "Загруженность 92%, скорость 15 км/ч"
    }
  ],
  "combined_issues": []
}
```

**Поля city_status:**
- `"normal"` — нет критических проблем
- `"warning"` — есть предупреждения
- `"critical"` — есть критические проблемы

---

## GET /api/transport/congestion-by-time

Средняя загруженность дорог по временным точкам.

**Ответ:**
```json
[
  { "timestamp": "2026-03-21 06:00:00", "congestion_level": 15.5 },
  { "timestamp": "2026-03-21 08:00:00", "congestion_level": 38.2 },
  ...
]
```

## GET /api/transport/congestion-by-district

Средняя загруженность по районам (отсортировано по убыванию).

**Ответ:**
```json
[
  { "district": "Медеуский", "congestion_level": 48.3 },
  { "district": "Бостандыкский", "congestion_level": 45.1 },
  ...
]
```

---

## GET /api/ecology/aqi-by-time

Средний AQI по временным точкам.

**Ответ:**
```json
[
  { "timestamp": "2026-03-21 06:00:00", "aqi": 28.5 },
  ...
]
```

## GET /api/ecology/aqi-by-district

Средний AQI по районам (отсортировано по убыванию).

**Ответ:**
```json
[
  { "district": "Медеуский", "aqi": 58.2 },
  ...
]
```

---

## GET /api/combined

Комбинированный анализ транспорта и экологии по районам.

**Ответ:**
```json
[
  {
    "district": "Медеуский",
    "avg_congestion": 48.3,
    "avg_speed": 35.2,
    "avg_aqi": 58.2,
    "avg_pm25": 22.1,
    "risk_score": 54.2
  },
  ...
]
```

**Формула risk_score:**
```
risk_score = avg_congestion * 0.4 + avg_aqi * 0.6
```

---

## GET /api/geojson

GeoJSON FeatureCollection с полигонами 8 районов Алматы.

**Ответ:** Стандартный GeoJSON.

**Районы:** Бостандыкский, Алмалинский, Медеуский, Ауэзовский, Наурызбайский, Алатауский, Жетысуский, Турксибский.

---

## GET /api/recycling

Пункты приема вторсырья.

**Ответ:**
```json
[
  {
    "name": "ЭкоПункт Бостандык",
    "lat": 43.228,
    "lon": 76.905,
    "type": "Пластик и бумага",
    "address": "ул. Ауэзова 1"
  },
  ...
]
```

---

## POST /api/assistant

AI-ассистент для вопросов о городе.

**Запрос:**
```json
{
  "question": "Где сейчас самый чистый воздух?"
}
```

**Ответ:**
```json
{
  "answer": "По текущим данным, самый чистый воздух в Наурызбайском районе..."
}
```

**Категории вопросов (fallback):**
- Возможности платформы: `"что умеет"`, `"возможности"`, `"функци"`
- Состояние города: `"состояни"`, `"ситуаци"`, `"что происходит"`
- Проблемные районы: `"район"`, `"где опасно"`, `"проблемн"`
- Прогулки: `"прогулк"`, `"гулять"`, `"бегать"`, `"спорт"`
- Планы развития: `"будущ"`, `"план"`, `"roadmap"`

---

## POST /api/impact

Расчет персонального экологического следа.

**Запрос:**
```json
{
  "fuel_type": "Бензин",
  "engine_volume": 2.0,
  "daily_km": 40
}
```

**Ответ:**
```json
{
  "fuel_type": "Бензин",
  "engine_volume": 2.0,
  "daily_km": 40,
  "co2_per_km": 190,
  "co2_daily_kg": 7.6,
  "co2_monthly_kg": 228.0,
  "co2_yearly_kg": 2774.0,
  "impact_score": 69,
  "comparison": 38.2,
  "level": "high",
  "explanation": "AI-интерпретация результата..."
}
```

**Уровни impact_score:**
| Score | Level | Описание |
|-------|-------|----------|
| 0–29 | `low` | Ниже среднего по городу |
| 30–59 | `medium` | Около среднего |
| 60–100 | `high` | Выше среднего |

---

## GET /api/impact/options

Доступные варианты для калькулятора.

**Ответ:**
```json
{
  "fuel_types": ["Бензин", "Дизель", "Газ (LPG)", "Гибрид", "Электро"],
  "engine_volumes": [1.0, 1.4, 1.6, 1.8, 2.0, 2.5, 3.0, 3.5, 4.0]
}
```

---

## CORS

Разрешенные origins:
- `http://localhost:3000`
- `http://localhost:3001`
