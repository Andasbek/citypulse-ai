# Frontend (Next.js)

## Стек

- **Next.js 16** (App Router, `"use client"`)
- **React 19** + TypeScript
- **Tailwind CSS 4** — стилизация
- **Recharts** — графики
- **Inter** — шрифт (Latin + Cyrillic)

## Структура страницы

```
Home (page.tsx)
├── Header          — логотип, статус города, счетчик проблем
├── KpiCards         — 6 метрик (скорость, загрузка, инциденты, AQI, PM2.5, PM10)
├── AiPanel          — AI-анализ с risk score кольцом
├── Tabs             — 8 вкладок навигации
├── [Active Tab]     — контент текущей вкладки
├── Recommendations  — панель рекомендаций
└── Footer
```

Приложение — SPA (Single Page Application) с клиентской навигацией по табам.

---

## Компоненты

### Header.tsx

| Prop | Тип | Описание |
|------|-----|----------|
| `data` | `DashboardData` | Полные данные дашборда |

Отображает: логотип CityPulse AI, статус города (пульсирующая точка), количество проблем, бейдж AI.

### KpiCards.tsx

| Prop | Тип | Описание |
|------|-----|----------|
| `data` | `DashboardData` | Полные данные дашборда |

6 карточек с иконками SVG, значениями и цветовой индикацией статуса. Glassmorphism-стиль с glow-эффектом.

### AiPanel.tsx

| Prop | Тип | Описание |
|------|-----|----------|
| `insight` | `AiInsight` | AI-анализ ситуации |

SVG ring chart для risk score, текстовые блоки (summary, what_is_happening, why_critical), статистика (total, critical, warning, combined).

### Tabs.tsx

| Prop | Тип | Описание |
|------|-----|----------|
| `activeTab` | `string` | ID активной вкладки |
| `onTabChange` | `(id: string) => void` | Callback смены вкладки |

**ID вкладок:** `transport`, `ecology`, `map`, `assistant`, `impact`, `health`, `routes`, `recycling`.

### TransportTab.tsx

| Prop | Тип | Описание |
|------|-----|----------|
| `issues` | `Issue[]` | Все проблемы (фильтрует по type="Транспорт") |

Графики:
- **AreaChart** — загруженность по времени (градиент фиолетовый)
- **BarChart** — загруженность по районам (горизонтальный, цвет по значению)
- Список транспортных проблем

### EcologyTab.tsx

| Prop | Тип | Описание |
|------|-----|----------|
| `issues` | `Issue[]` | Все проблемы (фильтрует по type="Экология") |

Графики:
- **AreaChart** — AQI по времени (градиент зеленый)
- **BarChart** — AQI по районам (горизонтальный)
- Список экологических проблем

### CombinedTab.tsx

| Prop | Тип | Описание |
|------|-----|----------|
| `combinedIssues` | `Issue[]` | Комбинированные проблемы |

Графики:
- **BarChart** — risk score по районам (вертикальный с LabelList)
- **ScatterChart** — загруженность vs AQI (размер = risk)
- Список комбинированных проблем

### AssistantChat.tsx

Пропсов нет. Самодостаточный компонент.

Функционал:
- Чат-интерфейс с историей сообщений
- Кнопки-подсказки для быстрых вопросов
- Анимация загрузки (bouncing dots)
- Auto-scroll к последнему сообщению

### ImpactCalculator.tsx

Пропсов нет. Загружает опции через API.

Функционал:
- Форма: тип топлива, объем двигателя, пробег
- SVG ring chart для impact score
- 4 метрики CO₂ (на км, день, месяц, год)
- AI-интерпретация результата

### HealthPanel.tsx

Пропсов нет. Загружает combined data через API.

Функционал:
- Рейтинг районов для прогулок (progress bars)
- 3 карточки рекомендаций (для всех, группы риска, спортсменам)

### RoutesPanel.tsx

Пропсов нет. Загружает combined data через API.

Функционал:
- Список проблемных участков (congestion ≥ 70%)
- Ссылки на 2GIS для каждого района
- Пронумерованные рекомендации

### RecyclingMap.tsx

Пропсов нет. Загружает recycling points через API.

Функционал:
- Grid карточек пунктов переработки
- Тип принимаемых материалов
- Ссылки на 2GIS

### RecommendationsPanel.tsx

| Prop | Тип | Описание |
|------|-----|----------|
| `recommendations` | `Recommendation[]` | AI-рекомендации |

Список рекомендаций с приоритетом (high/medium/low), типом и районом.

---

## API-клиент (lib/api.ts)

### Конфигурация

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
```

### Функции

| Функция | Метод | Эндпоинт | Возвращает |
|---------|-------|----------|-----------|
| `getDashboard()` | GET | `/api/dashboard` | `DashboardData` |
| `getCongestionByTime()` | GET | `/api/transport/congestion-by-time` | `TimeSeriesRecord[]` |
| `getCongestionByDistrict()` | GET | `/api/transport/congestion-by-district` | `DistrictRecord[]` |
| `getAqiByTime()` | GET | `/api/ecology/aqi-by-time` | `TimeSeriesRecord[]` |
| `getAqiByDistrict()` | GET | `/api/ecology/aqi-by-district` | `DistrictRecord[]` |
| `getCombined()` | GET | `/api/combined` | `CombinedRecord[]` |
| `getGeoJSON()` | GET | `/api/geojson` | `GeoJSON.FeatureCollection` |
| `getRecycling()` | GET | `/api/recycling` | `RecyclingPoint[]` |
| `askAssistant(question)` | POST | `/api/assistant` | `{answer: string}` |
| `calculateImpact(data)` | POST | `/api/impact` | `ImpactResult` |
| `getImpactOptions()` | GET | `/api/impact/options` | `{fuel_types, engine_volumes}` |

### Основные типы

```typescript
interface DashboardData {
  city_status: "normal" | "warning" | "critical"
  total_issues: number
  critical_count: number
  transport: { kpis: {...}, status: string }
  ecology: { kpis: {...}, status: string }
  ai_insight: AiInsight
  issues: Issue[]
  combined_issues: Issue[]
}

interface AiInsight {
  summary: string
  severity: string
  risk_score: number
  recommendations: Recommendation[]
  ai_powered: boolean
  // ...
}

interface Issue {
  type: string          // "Транспорт" | "Экология" | "Комбинированная"
  district: string
  timestamp: string
  severity: string      // "normal" | "warning" | "critical"
  description: string
}

interface CombinedRecord {
  district: string
  avg_congestion: number
  avg_aqi: number
  risk_score: number
}

interface ImpactResult {
  co2_per_km: number
  co2_daily_kg: number
  impact_score: number  // 0-100
  level: string         // "low" | "medium" | "high"
  explanation: string
  // ...
}
```

---

## Дизайн-система

### Цветовая палитра (темная тема)

| Переменная | Значение | Назначение |
|-----------|----------|------------|
| `--background` | `#0f0f14` | Фон страницы |
| `--card` | `rgba(22,22,30,0.8)` | Фон карточек (glass) |
| `--green` | `#00d68f` | Норма |
| `--orange` | `#ffaa00` | Предупреждение |
| `--red` | `#ff3d71` | Критично |
| `--purple` | `#7c5cfc` | Акцентный (кнопки, табы) |
| `--muted` | `#8b8b9e` | Вторичный текст |

### CSS-классы

| Класс | Описание |
|-------|----------|
| `.glass` | Glassmorphism: полупрозрачный фон + backdrop-filter + border |
| `.glow-*` | Box-shadow glow эффект (green, orange, red, purple) |
| `.animate-pulse-dot` | Пульсация для индикаторов статуса |
| `.animate-shimmer` | Shimmer для загрузки |

### Принципы

- Темная тема с neon-акцентами
- Glassmorphism для карточек
- SVG-иконки вместо emoji (в KPI и заголовках)
- Градиентные кнопки и активные табы
- Минимум анимаций — только статус и загрузка
