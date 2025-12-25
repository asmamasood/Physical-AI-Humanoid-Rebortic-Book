---
id: 004
title: Create RAG Chatboard Implementation Plan
stage: plan
date: 2025-12-17
surface: agent
model: gemini-2.5
feature: 002-rag-chatboard
branch: 002-rag-chatboard
user: asmamasood
command: /sp.plan
labels: ["rag", "chatboard", "implementation-plan", "fastapi", "docusaurus", "cloud-run"]
links:
  spec: file:///d:/digital-book/specs/002-rag-chatboard/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-rag-chatboard/plan.md
tests:
  - null
---

## Prompt

/sp.plan Phase 0 — Prep - Collect required secrets and repo link - Decide deployment target for FastAPI (Vercel/Cloud Run) Phase 1 — Data Pipeline  - scripts/collect_chapters.py: enumerate .md files, extract frontmatter - scripts/chunker.py: deterministic chunking (200–800 tokens), chunk_id generation - scripts/embed_upsert.py: use Cohere embeddings, upsert to Qdrant collection "book_v1" - Unit test: ingest sample .md and verify vectors in Qdrant Phase 2 — Backend  - FastAPI app with async endpoints: - POST /ingest (ADMIN_SECRET) - POST /chat {query, session_id, top_k} - POST /selective-chat {query, session_id, selection_text, selection_meta?} - GET /meta - POST /feedback - Implement qdrant_client.py wrapper, neon_db.py (optional), rate-limiter, auth middleware - Agent wrapper agents_wrapper.py to call Gemini with carefully constructed system prompts - Unit tests for retrieval + selective-chat behavior Phase 3 — Frontend / Docusaurus - plugin-rag that injects ChatBoard component site-wide - ChatBoard.tsx with: - message list, input, send - highlight listener + floating "Ask about selection" button - calls to /chat and /selective-chat - display citations with links to chapter anchors - Add plugin config + instructions to docusaurus.config.js Phase 4 — CI & Deploy  - GitHub Action workflow ingest.yml: run ingest on docs changes or manual trigger - Deploy FastAPI (Cloud Run/Vercel) with env vars - Document secrets provisioning for Qdrant, Cohere, Gemini, Neon Phase 5 — QA & Handoff  - E2E tests: ingest → query → selective-chat tests - Provide README: setup, run, sample curl commands, testing notes Total estimate: minimal MVP ~1 week of focused work (single dev). (For planning only; deliverable is the Spec-Kit.)

## Response snapshot

Created comprehensive 6-phase implementation plan (`specs/002-rag-chatboard/plan.md`) containing:

**Phase 0 - Preparation**:
- Secrets table: COHERE_API_KEY, QDRANT_URL, QDRANT_API_KEY, GEMINI_API_KEY, NEON_DB_URL, ADMIN_SECRET
- Recommended Cloud Run for FastAPI deployment

**Phase 1 - Data Pipeline**:
- `scripts/collect_chapters.py`: Enumerate .md files, extract frontmatter
- `scripts/chunker.py`: Deterministic chunking (200-800 tokens) with stable chunk_id
- `scripts/embed_upsert.py`: Cohere embeddings → Qdrant upsert with metadata

**Phase 2 - Backend**:
- FastAPI app structure with routers, services, middleware
- `/chat` endpoint with RAG retrieval and citations
- `/selective-chat` endpoint with strict selection-only context
- Gemini agent wrapper with specialized system prompts
- Rate limiting and admin authentication

**Phase 3 - Frontend**:
- `plugin-rag/` Docusaurus plugin structure
- `ChatBoard.tsx` with message list, input, highlight listener
- API client for backend communication
- CSS styling matching Docusaurus theme

**Phase 4 - CI/CD**:
- `ingest.yml` GitHub Actions workflow for docs changes
- `deploy-backend.yml` for Cloud Run deployment
- Dockerfile configuration

**Phase 5 - QA**:
- E2E tests for full ingestion → query → selective-chat flow
- README documentation with setup and curl examples

**Timeline**: 7 days for single developer

## Outcome

- ✅ Impact: Comprehensive implementation plan ready for execution
- 🧪 Tests: Plan includes test requirements for each phase
- 📁 Files: specs/002-rag-chatboard/plan.md (created)
- 🔁 Next prompts: /sp.tasks to generate detailed task breakdown
- 🧠 Reflection: Plan includes detailed pseudocode and file structures to accelerate implementation

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (planning phase)
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Generate tasks with /sp.tasks, then begin Phase 0 execution
