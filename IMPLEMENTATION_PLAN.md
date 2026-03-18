# MangaQA — Implementation & Deployment Plan

## Project Overview

A web-based manga translation QA tool that analyzes translated manga text for consistency errors, tone mismatches, untranslated text, and character voice inconsistencies using LLMs and embeddings.

**Tech Stack:**
- Frontend: React (Vite) → Deployed on Vercel
- Backend: FastAPI (Python) → Deployed on Render
- Database: Supabase (PostgreSQL + pgvector)
- AI: OpenRouter API (LLM + embeddings)

**Architecture:**
```
Vercel (React) → Render (FastAPI) → Supabase (Postgres + pgvector)
                                   → OpenRouter (LLM + embeddings)
```

---

## Phase 1: Project Setup & Infrastructure

**Goal:** Repo structure, dev environment, database schema, basic API skeleton.

### 1.1 Repository Setup
- [ ] Initialize git repo
- [ ] Create monorepo structure: `/frontend` (React) + `/backend` (FastAPI)
- [ ] Add `.gitignore` for Python + Node
- [ ] Add `README.md` with project description

### 1.2 Backend Scaffold
- [ ] Set up Python virtual environment
- [ ] Install core dependencies: `fastapi`, `uvicorn`, `sqlalchemy`, `asyncpg`, `alembic`, `httpx`, `pydantic`
- [ ] Create FastAPI app with health check endpoint
- [ ] Set up project config / environment variables (`.env`)
- [ ] Set up Alembic for database migrations

### 1.3 Database Setup (Supabase)
- [ ] Create Supabase project
- [ ] Enable pgvector extension
- [ ] Design and create schema:
  - `projects` — manga series/project metadata
  - `chapters` — chapter metadata per project
  - `dialogue_lines` — individual lines (speaker, text, type, page, panel)
  - `embeddings` — vector embeddings linked to dialogue lines
  - `analysis_jobs` — job queue tracking (status, timestamps)
  - `qa_results` — QA findings (checker type, severity, details)
- [ ] Run initial migration

### 1.4 Frontend Scaffold
- [ ] Initialize React app with Vite + TypeScript
- [ ] Install dependencies: `react-router-dom`, `axios`, `tailwindcss`
- [ ] Set up routing skeleton (Dashboard, Project, Upload, Report pages)
- [ ] Set up API client utility

---

## Phase 2: Data Upload & Storage Pipeline

**Goal:** Users can create projects, upload structured manga JSON, and persist it to the database.

### 2.1 Upload API
- [ ] `POST /api/projects` — create a project (title, description, language pair)
- [ ] `GET /api/projects` — list all projects
- [ ] `GET /api/projects/{id}` — get project details
- [ ] `DELETE /api/projects/{id}` — delete a project and its data
- [ ] `POST /api/projects/{id}/chapters` — upload chapter data (JSON)
- [ ] `GET /api/projects/{id}/chapters` — list chapters for a project

### 2.2 JSON Validation & Parsing
- [ ] Define Pydantic models for upload schema:
  ```json
  {
    "chapter_number": 1,
    "title": "The Beginning",
    "pages": [
      {
        "page_number": 1,
        "panels": [
          {
            "panel_id": 1,
            "speaker": "Takeshi",
            "text": "Let's go!",
            "type": "dialogue | sfx | narration | sign"
          }
        ]
      }
    ]
  }
  ```
- [ ] Validate and reject malformed uploads with clear error messages
- [ ] Store parsed data into `chapters` + `dialogue_lines` tables

### 2.3 Frontend — Upload Flow
- [ ] Dashboard page: list projects, create new project button
- [ ] Create project form (title, description)
- [ ] Project view: list chapters, upload button
- [ ] Upload page: JSON file drop zone + preview before submit
- [ ] Display upload success/error feedback

---

## Phase 3: Embedding Generation

**Goal:** Generate and store vector embeddings for all dialogue lines via OpenRouter API.

### 3.1 OpenRouter Integration
- [ ] Set up OpenRouter API client (httpx)
- [ ] Identify free embedding model on OpenRouter
- [ ] Implement embedding generation function (text → vector)
- [ ] Handle rate limiting and retries

### 3.2 Embedding Pipeline
- [ ] On chapter upload, trigger embedding generation for all dialogue lines
- [ ] Store embeddings in `embeddings` table (pgvector column)
- [ ] Build similarity search query (cosine distance via pgvector)
- [ ] Test: upload a chapter → verify embeddings stored → run a similarity query

---

## Phase 4: QA Engine — The 4 Checkers

**Goal:** Implement all four QA checkers that analyze the translated text.

### 4.1 Untranslated Text Checker (no LLM needed)
- [ ] Detect Japanese characters (hiragana, katakana, kanji) in translated text via Unicode ranges
- [ ] Flag dialogue lines containing untranslated text
- [ ] Assign severity: `critical` if in dialogue, `warning` if in SFX/signs
- [ ] Store results in `qa_results`

### 4.2 Consistency Checker (embeddings + LLM confirmation)
- [ ] Extract key terms: character names, place names, technique names per project
- [ ] Use pgvector similarity search to find near-duplicate terms across chapters
- [ ] Flag inconsistencies (e.g., "Ryuji" in ch.1 vs "Ryuuji" in ch.5)
- [ ] Send flagged pairs to LLM for confirmation: "Are these the same entity translated inconsistently?"
- [ ] Store confirmed inconsistencies in `qa_results`

### 4.3 Character Voice Checker (embeddings + LLM)
- [ ] Group all dialogue lines by speaker
- [ ] Compute centroid embedding per character (average of all their lines)
- [ ] Find outlier lines that deviate significantly from the character's centroid
- [ ] Send outliers to LLM with character context: "Does this line match this character's established voice?"
- [ ] Store flagged voice breaks in `qa_results`

### 4.4 Tone Checker (LLM-heavy)
- [ ] Group dialogue by scene/page context
- [ ] Send scene text to LLM with prompt: "Analyze the tone of this manga dialogue. Flag any lines where the tone feels inconsistent with the scene context."
- [ ] Parse LLM response into structured findings
- [ ] Store tone mismatches in `qa_results`

---

## Phase 5: Job Queue & Analysis Orchestration

**Goal:** Background job system so analysis doesn't block the API.

### 5.1 Job Queue Implementation
- [ ] Create `POST /api/projects/{id}/analyze` — triggers full QA analysis
- [ ] Create job record in `analysis_jobs` table (status: `pending`)
- [ ] Use FastAPI `BackgroundTasks` (or a simple worker loop) to process jobs
- [ ] Job runner picks up pending jobs, runs all 4 checkers sequentially
- [ ] Update job status: `pending` → `running` → `completed` / `failed`
- [ ] Store timestamps: `created_at`, `started_at`, `completed_at`

### 5.2 Job Status API
- [ ] `GET /api/projects/{id}/jobs` — list analysis jobs
- [ ] `GET /api/projects/{id}/jobs/{job_id}` — job status + progress
- [ ] Frontend: polling for job status until completion

---

## Phase 6: QA Report & Frontend

**Goal:** Display analysis results in a useful, filterable report UI.

### 6.1 Report API
- [ ] `GET /api/projects/{id}/report` — full QA report for latest analysis
- [ ] `GET /api/projects/{id}/report?checker=consistency&severity=critical` — filtered
- [ ] Response structure:
  ```json
  {
    "project_id": "...",
    "job_id": "...",
    "summary": {
      "total_issues": 42,
      "critical": 5,
      "warning": 20,
      "info": 17
    },
    "by_checker": {
      "untranslated": { "count": 3, "issues": [...] },
      "consistency": { "count": 15, "issues": [...] },
      "voice": { "count": 12, "issues": [...] },
      "tone": { "count": 12, "issues": [...] }
    }
  }
  ```

### 6.2 Frontend — Report View
- [ ] Report dashboard with summary cards (total issues, by severity, by checker)
- [ ] Filter controls: by checker type, severity, chapter
- [ ] Issue list: expandable cards showing the flagged text, context, suggestion, severity
- [ ] Link each issue back to chapter/page/panel for easy reference

### 6.3 Frontend — Job Status
- [ ] Show "Analysis Running..." state with progress indicator
- [ ] Auto-refresh when job completes
- [ ] Show job history (past analyses)

---

## Phase 7: Testing & Polish

**Goal:** Ensure reliability, create test data, polish the UX.

### 7.1 Synthetic Test Data
- [ ] Create 2-3 fake manga series JSON files with intentional QA errors:
  - Inconsistent character names
  - Voice breaks (formal character speaking casually)
  - Untranslated Japanese text left in
  - Tone mismatches in scenes
- [ ] Use these as demo data and for testing

### 7.2 Backend Tests
- [ ] Unit tests for each checker
- [ ] Integration tests for upload → analyze → report pipeline
- [ ] API endpoint tests

### 7.3 Frontend Polish
- [ ] Responsive design (mobile-friendly)
- [ ] Loading states and error handling
- [ ] Empty states (no projects, no reports yet)
- [ ] Toast notifications for actions (upload success, analysis started)

---

## Phase 8: Deployment

**Goal:** Deploy the full stack to free-tier services.

### 8.1 Supabase (already running from Phase 1)
- [ ] Verify production schema and pgvector extension
- [ ] Set up Row Level Security if needed
- [ ] Confirm connection pooling settings

### 8.2 Backend → Render
- [ ] Create `Dockerfile` or `render.yaml` for FastAPI
- [ ] Set environment variables on Render (Supabase URL, OpenRouter key)
- [ ] Deploy and verify health check endpoint
- [ ] Test API endpoints against production DB

### 8.3 Frontend → Vercel
- [ ] Set up Vercel project linked to GitHub repo
- [ ] Configure environment variable for API base URL
- [ ] Deploy and verify frontend loads
- [ ] Test full flow: create project → upload → analyze → view report

### 8.4 Post-Deployment
- [ ] Smoke test the entire pipeline end-to-end
- [ ] Add CORS configuration (Vercel domain → Render API)
- [ ] Add basic rate limiting on API
- [ ] Write deployment notes in README

---

## Future Enhancements (Post-MVP)
- OCR pipeline to extract text from manga images directly
- Source text (Japanese) comparison for translation accuracy checks
- User authentication and multi-user support
- Re-translation suggestions powered by LLM
- Batch analysis across entire volumes
- Export reports as PDF
- Webhook notifications when analysis completes
