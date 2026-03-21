# MangaQA — Progress Tracker

> Update this file as you complete each phase. Check off subtasks as they're done.

---

## Phase 1: Project Setup & Infrastructure
**Status:** `COMPLETED`
**Started:** 2026-03-19
**Completed:** 2026-03-19

- [x] 1.1 Repository Setup
  - [x] Initialize git repo
  - [x] Create monorepo structure (`/frontend` + `/backend`)
  - [x] Add `.gitignore`
  - [x] Add `README.md`
- [x] 1.2 Backend Scaffold
  - [x] Python virtual environment
  - [x] Install core dependencies
  - [x] FastAPI app + health check
  - [x] Environment config (`.env`)
  - [x] Alembic setup
- [x] 1.3 Database Setup (Supabase)
  - [x] Create Supabase project
  - [x] Enable pgvector
  - [x] Design + create schema
  - [x] Run initial migration
- [x] 1.4 Frontend Scaffold
  - [x] Vite + React + TypeScript
  - [x] Install dependencies
  - [x] Routing skeleton
  - [x] API client utility

---

## Phase 2: Data Upload & Storage Pipeline
**Status:** `COMPLETED`
**Started:** 2026-03-20
**Completed:** 2026-03-20

- [x] 2.1 Upload API
  - [x] `POST /api/projects`
  - [x] `GET /api/projects`
  - [x] `GET /api/projects/{id}`
  - [x] `DELETE /api/projects/{id}`
  - [x] `POST /api/projects/{id}/chapters`
  - [x] `GET /api/projects/{id}/chapters`
- [x] 2.2 JSON Validation & Parsing
  - [x] Pydantic upload models
  - [x] Validation + error messages
  - [x] Store to DB
- [x] 2.3 Frontend — Upload Flow
  - [x] Dashboard page
  - [x] Create project form
  - [x] Project view with chapters
  - [x] JSON upload with preview
  - [x] Success/error feedback

---

## Phase 3: Embedding Generation
**Status:** `COMPLETED`
**Started:** 2026-03-21
**Completed:** 2026-03-21

- [x] 3.1 Embedding Integration
  - [x] HuggingFace Inference API client (replaced OpenRouter — no free embedding models)
  - [x] Model: BAAI/bge-small-en-v1.5 (384-dim, free tier)
  - [x] Embedding generation function with batch encoding + normalization
  - [x] Alembic migration: vector dimension 1536 → 384
- [x] 3.2 OpenRouter LLM Client
  - [x] Rate-limited client (sliding-window, 20 req/min)
  - [x] Retry logic with exponential backoff on 429
  - [x] JSON response parsing with markdown fence stripping
- [x] 3.3 Similarity Search
  - [x] pgvector cosine distance queries
  - [x] Find similar-but-different line pairs
  - [x] Speaker centroid computation + outlier detection
  - [x] End-to-end test

---

## Phase 4: QA Engine — The 4 Checkers
**Status:** `COMPLETED`
**Started:** 2026-03-21
**Completed:** 2026-03-21

- [x] 4.1 Untranslated Text Checker
  - [x] Unicode range detection (CJK, Hiragana, Katakana)
  - [x] Japanese ratio classification (critical ≥80%, warning <80%)
  - [x] Store results with context JSONB
- [x] 4.2 Consistency Checker
  - [x] pgvector similarity search for near-duplicate lines
  - [x] LLM batch validation (10 pairs per call)
  - [x] Store confirmed inconsistencies
- [x] 4.3 Character Voice Checker
  - [x] Group lines by speaker (min 5 lines)
  - [x] Compute centroid embeddings (numpy mean + normalize)
  - [x] Detect outliers via cosine distance
  - [x] LLM voice validation with typical examples
  - [x] Store results
- [x] 4.4 Tone Checker
  - [x] Group by page, merge adjacent short scenes
  - [x] LLM tone analysis per scene block
  - [x] Parse findings with severity classification
  - [x] Store results

---

## Phase 5: Job Queue & Analysis Orchestration
**Status:** `COMPLETED`
**Started:** 2026-03-21
**Completed:** 2026-03-21

- [x] 5.1 Job Queue
  - [x] `POST /api/projects/{id}/jobs/analyze` (202 Accepted)
  - [x] Job record creation with duplicate check
  - [x] FastAPI BackgroundTasks worker
  - [x] Sequential checker execution with per-checker commits
  - [x] Status transitions (pending → running → completed/failed)
  - [x] In-memory progress tracking
- [x] 5.2 Job Status API
  - [x] `GET /api/projects/{id}/jobs`
  - [x] `GET /api/projects/{id}/jobs/{job_id}` with live progress
  - [x] Frontend polling (10s interval)

---

## Phase 6: QA Report & Frontend
**Status:** `COMPLETED`
**Started:** 2026-03-21
**Completed:** 2026-03-21

- [x] 6.1 Report API
  - [x] `GET /api/projects/{id}/report` (latest completed job)
  - [x] Summary stats (by severity, by checker)
  - [x] Dialogue line context via selectinload
- [x] 6.2 Frontend — Report View
  - [x] Summary cards (total, critical, warning, info)
  - [x] Checker breakdown cards
  - [x] Filter dropdowns (checker type, severity) — client-side
  - [x] Expandable issue cards with dialogue context + suggestions
- [x] 6.3 Frontend — Job Status
  - [x] "Run Analysis" button with live progress display
  - [x] Job status badges (pending/running/completed/failed)
  - [x] Auto-navigate to report on completion
- [x] 6.4 Authentication
  - [x] JWT auth (python-jose + bcrypt)
  - [x] Login page + protected routes
  - [x] Axios interceptors (auto-attach token, redirect on 401)
  - [x] Logout button in nav
  - [x] User creation script (credentials from .env)

---

## Phase 7: Testing & Polish
**Status:** `SKIPPED`
**Reason:** MVP scope — skipped formal tests and UI polish for now

- [ ] 7.1 Synthetic Test Data — 2 sample chapters exist (`sample_chapter.json`, `sample_chapter_2.json`)
- [ ] 7.2 Backend Tests — skipped
- [ ] 7.3 Frontend Polish — skipped

---

## Phase 8: Deployment
**Status:** `COMPLETED`
**Started:** 2026-03-22
**Completed:** 2026-03-22

- [x] 8.1 Supabase
  - [x] Production schema verified (all migrations applied)
  - [x] Session Pooler (pgbouncer) connection configured
- [x] 8.2 Backend → Render
  - [x] `backend/Dockerfile` created
  - [x] `render.yaml` with all env vars
  - [x] `.dockerignore` for clean builds
  - [ ] Deploy + health check (manual step)
  - [ ] Test endpoints (manual step)
- [x] 8.3 Frontend → Vercel
  - [x] Root directory: `frontend`, framework: Vite, output: `dist`
  - [x] `VITE_API_BASE_URL` env var documented
  - [ ] Deploy + verify (manual step)
  - [ ] Test full flow (manual step)
- [x] 8.4 Post-Deployment
  - [x] CORS configuration via `CORS_ORIGINS` env var
  - [x] Deployment notes in README

---

## Notes
- Supabase direct connection requires IPv6; using **Session Pooler** (pgbouncer) instead — requires `statement_cache_size=0` in asyncpg connect_args
- Alembic configured for async migrations with pgbouncer compatibility
- pgvector extension enabled via initial Alembic migration
- OpenRouter has no free embedding models — using HuggingFace Inference API (BAAI/bge-small-en-v1.5) instead
- Avoided `sentence-transformers` local install (~500MB PyTorch) — would break Render free tier deployment
- Supabase has 8s default statement timeout on DDL — use `SET statement_timeout = '0'` in migrations or run DDL via SQL Editor
- OpenRouter free tier: 20 req/min, 200 req/day — ~28 LLM calls per chapter analysis (~84s)
- Job progress tracked in-memory (not DB) to avoid pgbouncer transaction/lock issues
