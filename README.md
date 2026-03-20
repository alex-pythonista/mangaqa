# MangaQA

A web-based manga translation QA tool that automatically evaluates translated manga text for quality issues using LLMs and vector embeddings.

## What It Does

- **Consistency Checker** — Detects terms/names translated differently across chapters
- **Character Voice Checker** — Flags when a character's dialogue deviates from their established speech patterns
- **Tone Checker** — Identifies dialogue that doesn't match the scene's mood
- **Untranslated Text Detector** — Catches Japanese text left in the translation

## Tech Stack

- **Frontend**: React (Vite + TypeScript) + Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL + pgvector (Supabase)
- **AI**: OpenRouter API (LLM + embeddings)

## Setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Supabase and OpenRouter credentials
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### Database

1. Create a [Supabase](https://supabase.com) project
2. Copy the **Session Pooler** connection string to `backend/.env` (use `postgresql+asyncpg://` prefix)
3. Run migrations: `cd backend && .venv/bin/alembic upgrade head`

#### Schema

![Database schema](mangaqa_db_schema.png)

6 tables: `projects` → `chapters` → `dialogue_lines` → `embeddings`, `projects` → `analysis_jobs` → `qa_results`, with `qa_results` also referencing `dialogue_lines`.
