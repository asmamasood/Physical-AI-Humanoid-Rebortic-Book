---
id: 003
title: Update RAG Chatboard Specification with Full Stack
stage: spec
date: 2025-12-17
surface: agent
model: gemini-2.5
feature: 002-rag-chatboard
branch: 002-rag-chatboard
user: asmamasood
command: /sp.specify
labels: ["rag", "chatboard", "specification", "cohere", "qdrant", "gemini", "fastapi"]
links:
  spec: file:///d:/digital-book/specs/002-rag-chatboard/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-rag-chatboard/spec.md
tests:
  - null
---

## Prompt

Goal:
Build & embed a production-ready Retrieval-Augmented Generation (RAG) Chatboard into an existing Docusaurus book (deployed on GitHub Pages). The chatboard must answer user questions from the book, support "highlight → ask" mode (answer strictly from selected text), and be secure (no secret keys exposed client-side).

Stack:
- Embeddings: Cohere (COHERE_API_KEY)
- Vector DB: Qdrant Cloud (QDRANT_URL, QDRANT_API_KEY)
- LLM: Gemini API (GEMINI_API_KEY)
- Backend: FastAPI (Python, async)
- Optional metadata DB: Neon Serverless Postgres (NEON_DB_URL)
- Frontend: Docusaurus plugin + React component
- CI/CD: GitHub Actions (ingest on docs changes), deploy FastAPI to Cloud Run / Vercel serverless

Core behaviours:
1. Ingest: read .md chapters → clean → chunk (200–800 tokens) → embed (Cohere) → upsert (Qdrant) with metadata {module, chapter, chunk_id, source_url, start_pos, end_pos, token_count}.
2. Retrieval: semantic search from Qdrant (top_k configurable). Returned chunks include metadata & score.
3. Chat:
   - /chat: uses retrieval → passes retrieved chunks to Gemini for synthesis. Agent must cite sources (module:chapter:chunk_id).
   - /selective-chat: receives selection_text (and optional selection_meta); must NOT query Qdrant nor use any external content — Gemini must answer *only* from selection_text. If answer not present, return: "Answer not found in selected text."
4. Security: keys only server-side, backend proxy for all LLM/DB calls, rate-limit & admin auth for ingest endpoints.
5. Observability: ingestion logs, optional conversation history stored in Neon.

Success criteria:
- End-to-end ingestion → retrieval → Gemini answer with citations.
- Selection-mode strictly enforced server-side.
- Docusaurus plugin injects Chat UI and highlight-to-query UX.

## Response snapshot

Created comprehensive updated specification in `specs/002-rag-chatboard/spec.md` with:
- 5 user stories (General Q&A P1, Highlight-to-Ask P1, Ingestion Pipeline P1, Chat UI P2, Observability P3)
- Complete technology stack table (Cohere, Qdrant Cloud, Gemini, FastAPI, Neon)
- 16 functional requirements (FR-001 to FR-016) covering ingestion, retrieval, chat endpoints, and frontend
- 12 non-functional requirements (NFR-001 to NFR-012) covering security, performance, deployment, and observability
- 7 measurable success criteria (SC-001 to SC-007)
- Key entities definition (Chunk, Vector, Metadata, Chat Message, Citation, Selection)
- Detailed edge cases for error handling

## Outcome

- ✅ Impact: Updated specification aligns with user's detailed technology stack and behavioral requirements
- 🧪 Tests: Specification includes testable acceptance scenarios for each user story
- 📁 Files: specs/002-rag-chatboard/spec.md (updated)
- 🔁 Next prompts: /sp.plan to create implementation plan, /sp.tasks to generate task breakdown
- 🧠 Reflection: Previous spec was generic; new spec includes specific technologies and strict behavioral requirements for selection-mode enforcement

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (specification phase)
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Proceed to planning phase with /sp.plan
