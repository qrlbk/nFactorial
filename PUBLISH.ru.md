# Публикация проекта (Vercel + Render)

Пошаговый чеклист для бесплатного деплоя: **UI на Vercel**, **API на Render** (или Railway / Docker).

## Архитектура

```
Браузер → Vercel (Next.js) → /api/* → API_URL (Render)
```

Долгие LLM-запросы выполняются только на бэкенде. Vercel проксирует `/api` на ваш API.

## Что уже подготовлено в репозитории

| Файл | Назначение |
|------|------------|
| `requirements.txt` | Зависимости Python для Render |
| `render.yaml` | Blueprint Render (один клик) |
| `Dockerfile` | Альтернатива: любой хостинг с Docker |
| `Procfile` / `runtime.txt` | Heroku-совместимые стартеры |
| `frontend/vercel.json` | Сборка Next.js на Vercel |
| `frontend/next.config.ts` | Rewrite `/api` → `API_URL` |
| `frontend/.env.example` | Переменные для Vercel |
| `.env.example` | Переменные для API |
| `scripts/verify_deploy.sh` | Проверка после деплоя |

---

## Шаг 0. Репозиторий на GitHub

```bash
git remote -v   # должен быть origin → GitHub
git push -u origin main
```

Без публичного репозитория Vercel/Render не подключатся автоматически.

---

## Шаг 1. API на Render (бесплатный план)

1. [dashboard.render.com](https://dashboard.render.com) → **New** → **Blueprint**.
2. Подключите GitHub-репозиторий — подтянется `render.yaml`.
3. Создайте сервис `editorial-engine-api`.
4. В **Environment** добавьте секреты:

| Переменная | Обязательно | Пример |
|------------|-------------|--------|
| `LLM_PROVIDER` | Да | `openai` или `anthropic` |
| `OPENAI_API_KEY` | Если OpenAI | `sk-...` |
| `ANTHROPIC_API_KEY` | Если Anthropic | `sk-ant-...` |
| `ALLOWED_ORIGINS` | Нет | `https://your-app.vercel.app` или `*` |
| `LANGFUSE_PUBLIC_KEY` | Нет | для трейсинга |
| `LANGFUSE_SECRET_KEY` | Нет | |

5. **Manual Deploy → Deploy latest commit** (не старый `56fb746`). Дождитесь зелёной сборки.
6. Скопируйте URL, например:  
   `https://editorial-engine-api.onrender.com`

6. Проверка:

```bash
curl https://editorial-engine-api.onrender.com/health
# {"status":"ok","service":"adversarial-editorial-engine"}
```

**Важно:** на free tier Render «засыпает» — первый запрос после простоя может занять 30–60 с.

### Альтернатива: Docker

```bash
docker build -t editorial-api .
docker run -p 8000:8000 -e OPENAI_API_KEY=... -e LLM_PROVIDER=openai editorial-api
```

---

## Шаг 2. Frontend на Vercel

**Важно:** если в логе сборки видите `Using Python 3.12 from pyproject.toml` — Vercel деплоит **не** Next.js, а Python API. Это даёт `FUNCTION_INVOCATION_FAILED`. Нужен **Next.js** (см. ниже).

1. [vercel.com/new](https://vercel.com/new) → Import репозитория.
2. **Settings → General → Root Directory:** `frontend` (обязательно).  
   Либо оставьте корень репо — сработает корневой `vercel.json` (сборка `cd frontend && npm run build`).
3. **Settings → General → Framework Preset:** **Next.js** (не Python).
4. **Environment Variables:**

| Имя | Значение | Среды |
|-----|----------|-------|
| `API_URL` | `https://editorial-engine-api.onrender.com` | Production, Preview |
| `NEXT_PUBLIC_API_URL` | *(пусто)* | Production |

Пустой `NEXT_PUBLIC_API_URL` — браузер ходит на `/api/...` того же домена; Vercel проксирует на `API_URL`.

5. **Deploy**.

6. Проверка:

```bash
./scripts/verify_deploy.sh https://your-app.vercel.app
```

Или вручную:

- `https://your-app.vercel.app/en` — интерфейс
- `https://your-app.vercel.app/api/health` — прокси на бэкенд

Если API не настроен, вверху страницы появится жёлтый баннер «Backend API недоступен».

---

## Шаг 3. CORS (опционально)

При прямых запросах к API (без rewrite) задайте на Render:

```
ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-app-*.vercel.app
```

Через Vercel rewrite CORS обычно не мешает.

---

## Шаг 4. Демо для сдачи / портфолио

1. Откройте Production URL Vercel.
2. **Workspace** — вставьте контекст, выберите Thread / QRT / Essay, сгенерируйте.
3. **Discover** — лента arXiv/HN (без ключей).
4. **Voice Studio** — профиль стиля.
5. **Launch** — очередь публикации (mock X).

Убедитесь, что на Render задан рабочий LLM-ключ — иначе генерация упадёт с ошибкой.

---

## Локальная разработка (как было)

```bash
# Терминал 1 — API
cd /path/to/nFactorial
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Терминал 2 — UI
cd frontend && npm run dev
```

`API_URL` по умолчанию `http://127.0.0.1:8000` в `next.config.ts`.

---

## Частые проблемы

| Симптом | Решение |
|---------|---------|
| Баннер «API недоступен» | Проверьте `API_URL` на Vercel, `/api/health`, что Render-сервис Running |
| 502 на `/api/generate` | Cold start Render — подождите и повторите |
| Ошибка LLM | `LLM_PROVIDER` и ключ на **Render**, не на Vercel |
| История/голоса пропали | Данные на диске API; на free Render диск эфемерен при redeploy |
| Сборка Vercel падает | Root Directory = `frontend`, Node 20+ |

---

## CI перед пушем

```bash
source .venv/bin/activate && pytest -q
cd frontend && npm run build
```

GitHub Actions: `.github/workflows/ci.yml` (если включён в репо).

---

## Краткий чеклист «готово к публикации»

- [ ] Код на GitHub
- [ ] Render: API задеплоен, `/health` OK
- [ ] Render: `OPENAI_API_KEY` или `ANTHROPIC_API_KEY`
- [ ] Vercel: Root = `frontend`
- [ ] Vercel: `API_URL` = URL Render
- [ ] `/api/health` на домене Vercel OK
- [ ] Тестовая генерация thread на Production

Подробности на английском: [DEPLOY.md](./DEPLOY.md).
