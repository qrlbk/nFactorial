# Deploy to Vercel

**Russian step-by-step:** [PUBLISH.ru.md](./PUBLISH.ru.md)

Vercel hosts the **Next.js frontend**. The **FastAPI + LangGraph API** must run elsewhere (long LLM runs exceed serverless limits).

## Architecture

```
Browser → Vercel (Next.js) → /api/* rewrite → API_URL (Railway / Render / Fly)
```

## 1. Deploy API (choose one)

### Render (simplest)

1. Push repo to GitHub.
2. [Render Dashboard](https://dashboard.render.com) → New → Blueprint → connect repo (`render.yaml` included).
3. Set secrets: `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`, `LLM_PROVIDER`.
4. Copy service URL, e.g. `https://editorial-engine-api.onrender.com`.

Build uses `requirements.txt` (see `render.yaml`). Optional: `ALLOWED_ORIGINS` for direct API access.

### Railway / Fly / local

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Use the public HTTPS URL as `API_URL`.

## 2. Deploy frontend on Vercel

### Option A — Root Directory `frontend` (recommended)

1. [vercel.com/new](https://vercel.com/new) → Import Git repository.
2. **Root Directory:** `frontend`
3. Framework: **Next.js** (auto-detected).
4. **Environment variables:**

| Name | Value | Environments |
|------|-------|--------------|
| `API_URL` | `https://your-api.onrender.com` | Production, Preview |
| `NEXT_PUBLIC_API_URL` | *(leave empty)* | Production |

Leaving `NEXT_PUBLIC_API_URL` empty makes the browser call `/api/...` on the same domain; Vercel rewrites to `API_URL`.

5. Deploy.

### Option B — Deploy from repo root

Uses root `vercel.json` with `outputDirectory: frontend/.next`. Set the same env vars in the Vercel project.

## 3. Verify

```bash
chmod +x scripts/verify_deploy.sh
./scripts/verify_deploy.sh https://your-app.vercel.app https://your-api.onrender.com
```

- `https://your-app.vercel.app/en` — UI loads
- `https://your-app.vercel.app/api/health` — should return `{"status":"ok",...}` (proxied to backend)
- Yellow banner in the UI means `API_URL` is missing or the API is down
- Generate a thread with real API keys on the backend host

## Environment reference

### Vercel (frontend)

| Variable | Required | Description |
|----------|----------|-------------|
| `API_URL` | **Yes** (prod) | Backend origin for `/api` rewrites |
| `NEXT_PUBLIC_API_URL` | No | Override client API base (usually leave empty) |

### Backend (Render/Railway/etc.)

| Variable | Required |
|----------|----------|
| `LLM_PROVIDER` | Yes (`openai` or `anthropic`) |
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | Yes |
| `LANGFUSE_*` | Optional |
| `ALLOWED_ORIGINS` | Optional (`*` default) |

## Local dev (unchanged)

```bash
# API
uvicorn app.main:app --reload --port 8000

# UI
cd frontend && npm run dev
# API_URL defaults to http://127.0.0.1:8000 via next.config rewrites
```

## Notes

- **CORS:** API already allows `*`; rewrites avoid browser CORS in production.
- **Persistent data** (`data/traces`, voices): lives on the API server filesystem, not Vercel.
- **Cold starts:** Render free tier may add latency on first request.
