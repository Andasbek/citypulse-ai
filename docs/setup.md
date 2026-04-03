# Установка и запуск

## Требования

- Python 3.10+
- Node.js 18+
- npm

## Быстрый старт

### 1. Клонирование

```bash
git clone <repo-url>
cd citypulse-ai
```

### 2. Backend

```bash
# Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows

# Установить зависимости
pip install -r backend/requirements.txt

# (Опционально) Настроить OpenAI API
cp backend/.env.example backend/.env
# Отредактировать backend/.env:
#   OPENAI_API_KEY=sk-...
#   OPENAI_MODEL=gpt-4o-mini

# Запустить API сервер
cd backend
uvicorn api:app --reload --port 8000
```

API будет доступен на http://localhost:8000.

### 3. Frontend

```bash
# В другом терминале
cd frontend

# Установить зависимости
npm install

# Запустить dev-сервер
npm run dev
```

Frontend будет доступен на http://localhost:3000 (или 3001 если 3000 занят).

### 4. Открыть в браузере

http://localhost:3000

---

## Переменные окружения

### Backend (`backend/.env`)

| Переменная | По умолчанию | Описание |
|-----------|-------------|----------|
| `OPENAI_API_KEY` | — | Ключ OpenAI API (опционально) |
| `OPENAI_MODEL` | `gpt-4o-mini` | Модель OpenAI |

Приложение работает и без OpenAI API — в этом случае используется rule-based fallback.

### Frontend

| Переменная | По умолчанию | Описание |
|-----------|-------------|----------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | URL бэкенда |

Создайте `frontend/.env.local` для переопределения:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Python-зависимости

```
streamlit==1.45.0
pandas==2.2.3
plotly==6.0.1
pydeck==0.9.1
python-dotenv==1.1.0
openai==1.82.0
fastapi==0.115.0
uvicorn==0.30.0
```

## Node.js зависимости

- next, react, react-dom
- recharts
- leaflet, react-leaflet, @types/leaflet
- tailwindcss
- typescript, eslint

---

## Streamlit (legacy)

Оригинальный Streamlit UI все ещё доступен:

```bash
cd backend
streamlit run app.py
```

---

## Частые проблемы

### CORS ошибка

Если frontend не может подключиться к API — убедитесь что порт фронтенда указан в `api.py`:

```python
allow_origins=["http://localhost:3000", "http://localhost:3001"]
```

### API не отвечает

1. Проверьте что backend запущен: `curl http://localhost:8000/api/dashboard`
2. Проверьте что вы в директории `backend/` при запуске uvicorn
3. Проверьте что virtual environment активирован

### Данные не обновились

Backend кеширует данные при старте. Перезапустите uvicorn после изменения CSV:

```bash
pkill -f "uvicorn api:app"
cd backend && uvicorn api:app --reload --port 8000
```
