---
id: 005
title: Generate Complete RAG Chatboard Task Breakdown
stage: tasks
date: 2025-12-17
surface: agent
model: gemini-2.5
feature: 002-rag-chatboard
branch: 002-rag-chatboard
user: asmamasood
command: /sp.tasks
labels: ["rag", "chatboard", "tasks", "implementation", "full-stack"]
links:
  spec: file:///d:/digital-book/specs/002-rag-chatboard/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-rag-chatboard/tasks.md
tests:
  - null
---

## Prompt

/sp.task

Generate a complete RAG Chatboard feature using this structure:

1. Scripts
   - scripts/collect_chapters.py
   - scripts/chunker.py
   - scripts/embed_upsert.py

2. Backend
   - backend/app/main.py (FastAPI)
   - backend/app/qdrant_client.py
   - backend/app/cohere_client.py
   - backend/app/gemini_agent.py (agent/prompt builder)
   - backend/app/models.py (pydantic defs)
   - backend/app/db_neon.py (optional)

3. Endpoints
   - POST /ingest {repo_path_or_url} (ADMIN_SECRET)
   - POST /chat {query, session_id, top_k}
   - POST /selective-chat {query, session_id, selection_text, selection_meta?}
   - GET  /meta
   - POST /feedback

4. Frontend
   - plugin-rag/index.tsx (Docusaurus plugin)
   - frontend/src/components/ChatBoard.tsx
   - frontend/src/styles/chatboard.css

5. CI / Ops
   - .github/workflows/ingest.yml
   - Dockerfile (optional) for FastAPI
   - deploy guide for Cloud Run / Vercel

6. Tests
   - tests/test_ingest.py
   - tests/test_retrieval.py
   - tests/test_selective_chat.py

7. Docs
   - README.md (setup, env vars, run commands)
   - SECURITY.md (how keys are stored / rotated)

8. Example usage files
   - example_doc.md
   - example_curl_commands.txt

## Response snapshot

Created comprehensive tasks.md (`specs/002-rag-chatboard/tasks.md`) with **60 tasks** across **8 phases**:

**Phase 0 - Preparation (4 tasks)**:
- T001-T004: Environment setup, secrets collection, Qdrant/GCP configuration

**Phase 1 - Scripts (6 tasks)**:
- T005-T010: collect_chapters.py, chunker.py, embed_upsert.py, run_ingestion.py

**Phase 2 - Backend Foundation (11 tasks)**:
- T011-T021: Project structure, config, models, services (Cohere, Qdrant, Gemini, Neon), middleware

**Phase 3 - Backend Endpoints (6 tasks)**:
- T022-T028: main.py, /chat, /selective-chat, /ingest, /meta, /feedback

**Phase 4 - Frontend (10 tasks)**:
- T029-T038: plugin-rag, ChatBoard.tsx, highlight listener, styles, docusaurus.config.ts

**Phase 5 - CI/CD (4 tasks)**:
- T039-T042: ingest.yml, deploy-backend.yml, Dockerfile, DEPLOY.md

**Phase 6 - Tests (6 tasks)**:
- T043-T048: test_ingest.py, test_retrieval.py, test_selective_chat.py, conftest.py

**Phase 7 - Documentation (4 tasks)**:
- T049-T052: README.md, SECURITY.md, example_doc.md, example_curl_commands.txt

**Phase 8 - Polish (8 tasks)**:
- T053-T060: Integration testing, performance validation, cleanup

**Schedule**: 7 days for single developer with detailed day-by-day breakdown

## Outcome

- ✅ Impact: Complete implementable task list ready for development team
- 🧪 Tests: 6 test tasks included (T043-T048)
- 📁 Files: specs/002-rag-chatboard/tasks.md (created)
- 🔁 Next prompts: Begin implementation with Phase 0 (T001-T004)
- 🧠 Reflection: Tasks include critical marker for T045 (selective chat must not call Qdrant)

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (planning phase)
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Begin Phase 0 implementation, validate environment setup
