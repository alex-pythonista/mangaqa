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
**Status:** `NOT STARTED`
**Started:** —
**Completed:** —

- [ ] 3.1 OpenRouter Integration
  - [ ] API client setup
  - [ ] Identify free embedding model
  - [ ] Embedding generation function
  - [ ] Rate limiting + retries
- [ ] 3.2 Embedding Pipeline
  - [ ] Trigger on chapter upload
  - [ ] Store in pgvector column
  - [ ] Similarity search query
  - [ ] End-to-end test

---

## Phase 4: QA Engine — The 4 Checkers
**Status:** `NOT STARTED`
**Started:** —
**Completed:** —

- [ ] 4.1 Untranslated Text Checker
  - [ ] Unicode range detection
  - [ ] Flag + severity assignment
  - [ ] Store results
- [ ] 4.2 Consistency Checker
  - [ ] Term extraction
  - [ ] Similarity search for near-duplicates
  - [ ] LLM confirmation
  - [ ] Store results
- [ ] 4.3 Character Voice Checker
  - [ ] Group lines by speaker
  - [ ] Compute centroid embeddings
  - [ ] Detect outliers
  - [ ] LLM voice validation
  - [ ] Store results
- [ ] 4.4 Tone Checker
  - [ ] Group by scene context
  - [ ] LLM tone analysis
  - [ ] Parse findings
  - [ ] Store results

---

## Phase 5: Job Queue & Analysis Orchestration
**Status:** `NOT STARTED`
**Started:** —
**Completed:** —

- [ ] 5.1 Job Queue
  - [ ] `POST /api/projects/{id}/analyze`
  - [ ] Job record creation
  - [ ] Background worker
  - [ ] Run all 4 checkers
  - [ ] Status transitions + timestamps
- [ ] 5.2 Job Status API
  - [ ] `GET /api/projects/{id}/jobs`
  - [ ] `GET /api/projects/{id}/jobs/{job_id}`
  - [ ] Frontend polling

---

## Phase 6: QA Report & Frontend
**Status:** `NOT STARTED`
**Started:** —
**Completed:** —

- [ ] 6.1 Report API
  - [ ] `GET /api/projects/{id}/report`
  - [ ] Filtering (checker, severity)
  - [ ] Response structure
- [ ] 6.2 Frontend — Report View
  - [ ] Summary cards
  - [ ] Filter controls
  - [ ] Issue list (expandable)
  - [ ] Chapter/page/panel references
- [ ] 6.3 Frontend — Job Status
  - [ ] Running state + progress
  - [ ] Auto-refresh on completion
  - [ ] Job history

---

## Phase 7: Testing & Polish
**Status:** `NOT STARTED`
**Started:** —
**Completed:** —

- [ ] 7.1 Synthetic Test Data
  - [ ] Create 2-3 fake manga series with errors
- [ ] 7.2 Backend Tests
  - [ ] Unit tests per checker
  - [ ] Integration tests (upload → analyze → report)
  - [ ] API endpoint tests
- [ ] 7.3 Frontend Polish
  - [ ] Responsive design
  - [ ] Loading + error states
  - [ ] Empty states
  - [ ] Toast notifications

---

## Phase 8: Deployment
**Status:** `NOT STARTED`
**Started:** —
**Completed:** —

- [ ] 8.1 Supabase
  - [ ] Verify production schema
  - [ ] Row Level Security
  - [ ] Connection pooling
- [ ] 8.2 Backend → Render
  - [ ] Dockerfile / render.yaml
  - [ ] Environment variables
  - [ ] Deploy + health check
  - [ ] Test endpoints
- [ ] 8.3 Frontend → Vercel
  - [ ] Vercel project setup
  - [ ] API base URL env var
  - [ ] Deploy + verify
  - [ ] Test full flow
- [ ] 8.4 Post-Deployment
  - [ ] End-to-end smoke test
  - [ ] CORS configuration
  - [ ] Rate limiting
  - [ ] Deployment notes in README

---

## Notes
- Supabase direct connection requires IPv6; using **Session Pooler** (pgbouncer) instead — requires `statement_cache_size=0` in asyncpg connect_args
- Alembic configured for async migrations with pgbouncer compatibility
- pgvector extension enabled via initial Alembic migration
