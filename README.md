# Adversarial Editorial Engine — Editorial OS

Multi-agent platform for high-insight X/Twitter content: threads, quote retweets, essays — with content discovery, voice profiles, fact-checking, and distribution.

**Not** a generic AI writer. Quality emerges from rejection pressure, not generation volume.

## Assignment mapping

| TZ requirement | Feature | API |
|---|---|---|
| Content Discovery | arXiv, HN, Substack RSS, mock tweets | `GET /discover` |
| Quote Retweets | QRT pipeline + evaluators | `POST /generate` (`output_type=quote_retweet`) |
| Thread / Essay generation | Thread (existing) + essay pipeline | `POST /generate` |
| Multiple thesis angles | Thesis generator + user pick | `POST /generate/thesis-angles` |
| Iterative refinement | Critic + rewrite loop | built into pipeline |
| Upload / voice | File ingest + voice CRUD | `POST /upload`, `/voices` |
| Fact-checking | Claim extractor + grounding | post-pipeline `fact_checker` node |
| Multi-agent | retrieval, thesis_angles, fact_checker, hooks, distribution | LangGraph |
| Autonomous research | discover → retrieve → generate | `POST /research/run` |
| Memory | favorites, hooks, preferences | `app/services/memory.py` |
| Evaluation | benchmarks + `scripts/run_benchmark.py` | `tests/benchmarks/` |
| Distribution | Mock X publisher + launch queue | `POST /launch`, `GET /launch/queue` |
| X API (later) | `TwitterAPIPublisher` stub | set `X_BEARER_TOKEN` |

## Architecture

```
Discovery/Upload → Retrieval Agent → Context Gate → Research → Thesis Angles
  → Thesis → Narrative → Writer (thread|qrt|essay) → Evaluators → Critic
  → Fact Check → Hooks → Distribution
```

## Deploy (Vercel)

Frontend → **Vercel**, API → **Render / Railway** (LLM pipeline is too long for Vercel serverless).

- English: [DEPLOY.md](DEPLOY.md)
- Русский чеклист: [PUBLISH.ru.md](PUBLISH.ru.md)
- Verify: `./scripts/verify_deploy.sh https://your-app.vercel.app`

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

### Environment

| Variable | Description |
|----------|-------------|
| `LLM_PROVIDER` | `anthropic` or `openai` |
| `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` | LLM keys |
| `LANGFUSE_*` | Optional tracing |
| `X_BEARER_TOKEN` | Optional — enables Twitter API publisher stub |

## API (highlights)

```bash
uvicorn app.main:app --reload --port 8000
```

| Endpoint | Description |
|----------|-------------|
| `POST /generate` | Full pipeline — `{ context, mode, output_type, thesis_id, voice_profile_id, source_urls, quoted_tweet }` |
| `POST /generate/thesis-angles` | Generate 3–5 thesis candidates |
| `POST /generate/hooks` | Hook variants for a draft |
| `GET /discover?source=arxiv\|hackernews\|substack\|tweets&q=...` | Content discovery |
| `POST /discover/ingest` | Fetch URL → chunks |
| `POST /research/run` | Autonomous research workflow |
| `POST /upload` | PDF/txt/md upload → chunk store |
| `GET/POST /voices` | Voice profile CRUD |
| `POST /launch` | Queue draft for mock X publish |
| `GET /launch/queue` | List launch queue |

## Frontend

```bash
cd frontend && npm install && npm run dev
```

| Route | Purpose |
|-------|---------|
| `/` | Workspace — Thread / QRT / Essay |
| `/discover` | Browse sources |
| `/voice` | Voice Studio |
| `/launch` | Distribution queue |
| `/history`, `/templates`, `/settings` | existing |

## Demo script (for judges)

1. **Weak input → refusal:** paste generic hype → expect fail-closed
2. **Discovery → thread:** `/discover` → "Use as context" → generate thread
3. **Autonomous research:** `POST /research/run` with topic `"LLM inference economics"`
4. **QRT:** `output_type=quote_retweet` + quoted tweet + context
5. **Trace replay:** open trace in Langfuse or `/traces/{id}` — show rejection chain

## Benchmarks

```bash
python scripts/run_benchmark.py
pytest -v
```

## Tech stack

Python 3.12+, FastAPI, LangGraph, SQLite (chunks/memory), Next.js 16, Langfuse
