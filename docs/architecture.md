# Архитектура проекта

## Технологический стек

### Backend
- **Python 3.10+**
- **FastAPI** — REST API сервер
- **Pandas** — обработка и агрегация данных
- **OpenAI API** — генерация AI-выводов (опционально, есть fallback)
- **Streamlit** — альтернативный UI (оригинальное приложение)

### Frontend
- **Next.js 16** (App Router)
- **React 19** + TypeScript
- **Tailwind CSS 4** — стилизация
- **Recharts** — графики (AreaChart, BarChart, ScatterChart)

### Инфраструктура
- **Uvicorn** — ASGI-сервер для FastAPI
- **npm** — менеджер пакетов фронтенда

## Структура директорий

```
citypulse-ai/
├── docs/                            # Документация
├── backend/                         # Python-бэкенд
│   ├── api.py                       # FastAPI REST API
│   ├── app.py                       # Streamlit-приложение (legacy UI)
│   ├── requirements.txt             # Python-зависимости
│   ├── services/                    # Бизнес-логика
│   │   ├── data_loader.py           # Загрузка CSV-данных
│   │   ├── transport_service.py     # KPI и агрегации транспорта
│   │   ├── ecology_service.py       # KPI и агрегации экологии
│   │   ├── anomaly_detector.py      # Обнаружение аномалий и проблем
│   │   ├── combined_analysis.py     # Комбинированный анализ
│   │   ├── ai_service.py            # AI-сервис (OpenAI + fallback)
│   │   └── user_impact_service.py   # Калькулятор экологического следа
│   ├── components/                  # Streamlit-компоненты (legacy)
│   ├── data/                        # Данные
│   │   ├── transport.csv            # Транспортные данные (672 записи)
│   │   ├── ecology.csv              # Экологические данные (672 записи)
│   │   ├── almaty_districts.geojson # Полигоны 8 районов Алматы
│   │   └── recycling_points.csv     # Пункты переработки (20 точек)
│   └── utils/
│       └── constants.py             # Пороговые значения и константы
├── frontend/                        # Next.js-фронтенд
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx           # Корневой layout (шрифт Inter, мета)
│   │   │   ├── page.tsx             # Главная страница (SPA с табами)
│   │   │   └── globals.css          # Глобальные стили, CSS-переменные
│   │   ├── lib/
│   │   │   └── api.ts               # API-клиент + TypeScript-типы
│   │   └── components/              # React-компоненты
│   │       ├── Header.tsx
│   │       ├── KpiCards.tsx
│   │       ├── AiPanel.tsx
│   │       ├── Tabs.tsx
│   │       ├── TransportTab.tsx
│   │       ├── EcologyTab.tsx
│   │       ├── CombinedTab.tsx
│   │       ├── AssistantChat.tsx
│   │       ├── ImpactCalculator.tsx
│   │       ├── HealthPanel.tsx
│   │       ├── RoutesPanel.tsx
│   │       ├── RecyclingMap.tsx
│   │       └── RecommendationsPanel.tsx
│   └── package.json
├── venv/                            # Python virtual environment
├── .gitignore
└── README.md
```

## Схема взаимодействия

```
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│              (Next.js / React)                   │
│                                                  │
│  page.tsx ──> lib/api.ts ──> fetch("/api/...")   │
└───────────────────────┬─────────────────────────┘
                        │ HTTP (localhost:3000 → 8000)
                        ▼
┌─────────────────────────────────────────────────┐
│                   Backend                        │
│              (FastAPI / Python)                   │
│                                                  │
│  api.py                                          │
│    ├── /api/dashboard ──► services/*             │
│    ├── /api/transport/* ──► transport_service    │
│    ├── /api/ecology/*   ──► ecology_service      │
│    ├── /api/combined    ──► combined_analysis    │
│    ├── /api/assistant   ──► ai_service           │
│    ├── /api/impact      ──► user_impact_service  │
│    ├── /api/geojson     ──► data/*.geojson       │
│    └── /api/recycling   ──► data/*.csv           │
│                                                  │
│  services/                                       │
│    ├── data_loader ──► data/*.csv                │
│    ├── anomaly_detector                          │
│    └── ai_service ──► OpenAI API (optional)      │
└─────────────────────────────────────────────────┘
```

## Принципы архитектуры

1. **Разделение frontend/backend** — фронтенд общается с бэкендом исключительно через REST API
2. **Сервисный слой** — бизнес-логика изолирована в `services/`, не зависит от UI
3. **Graceful degradation** — AI-сервис работает и без OpenAI API (rule-based fallback)
4. **Данные загружаются один раз** при старте сервера и кешируются в памяти
5. **CORS** — настроен для `localhost:3000` и `localhost:3001`
