# MangaQA

Web-based manga translation QA tool using LLMs and vector embeddings.

## Project Structure

- `backend/` — FastAPI (Python 3.12)
- `frontend/` — React + Vite + TypeScript + Tailwind CSS
- Monorepo, no shared packages

## Setup

### Backend
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm run dev
```

### Environment Files
- `backend/.env.example` — all backend env vars
- `frontend/.env.example` — all frontend env vars
- **IMPORTANT**: When adding a new config/env var to either backend or frontend, always update the corresponding `.env.example` file with the new variable name and a sensible placeholder value.

## Conventions

### Backend
- Async SQLAlchemy + asyncpg (all DB operations are async)
- Use `logging.getLogger(__name__)` for logging — centralized config in `app/logging_config.py`
- All DB tables use UUID primary keys
- Pydantic models for request/response schemas in `app/schemas/`
- SQLAlchemy models in `app/models/`
- Routes in `app/routers/`
- Config via pydantic-settings in `app/config.py` — all settings come from env vars
- Database: Supabase PostgreSQL + pgvector
- Migrations: Alembic (async) in `backend/alembic/`
- DB connection uses Session Pooler (pgbouncer) — requires `statement_cache_size=0` in connect_args

### Database Migrations
```bash
cd backend

# Generate a new migration after changing models
.venv/bin/alembic revision --autogenerate -m "describe change"

# Apply migrations
.venv/bin/alembic upgrade head

# Check current migration state
.venv/bin/alembic current

# Rollback one migration
.venv/bin/alembic downgrade -1
```

### Frontend
- Vite + React + TypeScript
- Tailwind CSS for styling
- Axios API client in `src/api/client.ts`
- Pages in `src/pages/`, components in `src/components/`
- React Router for routing

## Key Decisions
- Embeddings stored in pgvector (not local ChromaDB) for deployment simplicity
- OpenRouter API for both LLM and embeddings (free tier)
- Job queue for async QA analysis (not synchronous)
- Input format: structured JSON upload
