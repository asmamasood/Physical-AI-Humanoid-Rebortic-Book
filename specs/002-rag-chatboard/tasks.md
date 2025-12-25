# Tasks: RAG Chatboard

**Input**: Design documents from `specs/002-rag-chatboard/` (spec.md, plan.md)  
**Prerequisites**: plan.md ✅, spec.md ✅  
**Branch**: `002-rag-chatboard`  
**Estimate**: ~7 days (single developer)

## Format: `[ID] [P?] [Story] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1=General Q&A, US2=Selective Chat, US3=Ingestion, US4=UI/UX, US5=Observability)
- Include exact file paths in descriptions

---

## Phase 0: Preparation

**Purpose**: Environment setup, secrets collection, external service configuration

### Secrets & Configuration

- [ ] T001 Create `.env.example` with all required environment variables at project root
  - `COHERE_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`, `GEMINI_API_KEY`, `NEON_DB_URL`, `ADMIN_SECRET`
  - Notes: Include comments explaining where to obtain each key
- [ ] T002 [P] Create Qdrant Cloud collection `book_v1` with vector size 1024 (Cohere embed-english-v3.0)
  - Manual step via Qdrant Cloud dashboard
- [ ] T003 [P] Create Google Cloud project and enable Cloud Run API (if using Cloud Run)
  - Document project ID in `.env.example`
- [ ] T004 [P] Set up GitHub repository secrets for CI/CD
  - `COHERE_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`, `GEMINI_API_KEY`, `GCP_SA_KEY`, `GCP_PROJECT_ID`

**Checkpoint**: Environment ready for development

---

## Phase 1: Scripts (Data Pipeline)

**Purpose**: Content ingestion from Markdown → Qdrant vectors

### Chapter Collection

- [ ] T005 [P] [US3] Create `scripts/__init__.py` (empty package init)
- [ ] T006 [US3] Create `scripts/collect_chapters.py`
  - Function `collect_chapters(docs_root: Path) -> List[Chapter]`
  - Recursively enumerate `.md` files from `physical-ai-robotics-book/docs/`
  - Parse YAML frontmatter (title, sidebar_position)
  - Extract module from path (e.g., `module-1/chapter-1.md` → module="module-1")
  - Generate `source_url` pointing to GitHub Pages location
  - Return list of `Chapter(path, module, title, content, source_url)`
  - Dependencies: PyYAML, pathlib

### Chunking

- [ ] T007 [US3] Create `scripts/chunker.py`
  - Function `chunk_chapter(chapter: Chapter, min_tokens=200, max_tokens=800) -> List[Chunk]`
  - Clean Markdown formatting (remove `#`, `**`, links, code blocks)
  - Split into sentences using NLTK or regex
  - Aggregate sentences into chunks of 200-800 tokens
  - Implement 2-sentence overlap between chunks
  - Generate deterministic `chunk_id`: `hashlib.sha256(f"{module}:{chapter}:{content[:100]}").hexdigest()[:16]`
  - Track `start_pos`, `end_pos`, `token_count` per chunk
  - Return list of `Chunk(chunk_id, module, chapter, content, source_url, start_pos, end_pos, token_count)`
  - Dependencies: tiktoken (for token counting)

### Embedding & Upsert

- [ ] T008 [US3] Create `scripts/embed_upsert.py`
  - Function `embed_and_upsert(chunks: List[Chunk], collection_name="book_v1") -> int`
  - Initialize Cohere client with `COHERE_API_KEY`
  - Initialize Qdrant client with `QDRANT_URL`, `QDRANT_API_KEY`
  - Check if collection exists, create if not (size=1024, distance=COSINE)
  - Batch embed texts using `co.embed(model="embed-english-v3.0", input_type="search_document")`
  - Create `PointStruct` with vector and payload metadata
  - Upsert to Qdrant in batches of 100
  - Return count of vectors upserted
  - Dependencies: cohere, qdrant-client

### Orchestration

- [ ] T009 [US3] Create `scripts/run_ingestion.py`
  - Main orchestration script
  - Load environment from `.env`
  - Call `collect_chapters()` → `chunk_chapter()` for each → `embed_and_upsert()`
  - Print progress: files processed, chunks created, vectors upserted
  - Handle errors gracefully with detailed logging
  - Exit with appropriate status code
  - Dependencies: python-dotenv

### Requirements

- [ ] T010 [P] [US3] Create `scripts/requirements.txt`
  - cohere>=5.0.0
  - qdrant-client>=1.7.0
  - tiktoken>=0.5.0
  - PyYAML>=6.0
  - python-dotenv>=1.0.0

**Checkpoint**: Ingestion pipeline can run `python scripts/run_ingestion.py` successfully

---

## Phase 2: Backend Foundation

**Purpose**: FastAPI application structure, services, and middleware

### Project Structure

- [ ] T011 [P] Create `backend/app/__init__.py` (empty package init)
- [ ] T012 [P] Create `backend/requirements.txt`
  - fastapi>=0.109.0
  - uvicorn[standard]>=0.27.0
  - pydantic>=2.5.0
  - cohere>=5.0.0
  - qdrant-client>=1.7.0
  - google-generativeai>=0.3.0
  - python-dotenv>=1.0.0
  - asyncpg>=0.29.0 (for Neon)
  - httpx>=0.26.0

### Configuration

- [ ] T013 Create `backend/app/config.py`
  - Pydantic `Settings` class with all environment variables
  - `COHERE_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`, `GEMINI_API_KEY`
  - `NEON_DB_URL` (optional)
  - `ADMIN_SECRET`
  - `CORS_ORIGINS` (default: `["https://asmamasood.github.io", "http://localhost:3000"]`)
  - `RATE_LIMIT_PER_MINUTE` (default: 60)
  - Validate all required keys on startup

### Models (Pydantic)

- [ ] T014 Create `backend/app/models.py`
  - `ChatRequest(query: str, session_id: Optional[str], top_k: int = 5)`
  - `SelectiveChatRequest(query: str, selection_text: str, selection_meta: Optional[dict], session_id: Optional[str])`
  - `ChatResponse(answer: str, citations: List[Citation], session_id: Optional[str])`
  - `Citation(module: str, chapter: str, chunk_id: str, source_url: str, score: Optional[float])`
  - `IngestRequest(repo_path_or_url: Optional[str])`
  - `IngestResponse(status: str, files_processed: int, chunks_created: int, vectors_upserted: int)`
  - `FeedbackRequest(session_id: str, message_id: str, rating: int, comment: Optional[str])`
  - `MetaResponse(version: str, collection: str, vector_count: int, last_ingested: Optional[datetime])`

### Services

- [ ] T015 [P] Create `backend/app/cohere_client.py`
  - `CohereEmbedder` class
  - Async method `embed_query(text: str) -> List[float]`
  - Use `model="embed-english-v3.0"`, `input_type="search_query"`
  - Handle rate limits and errors gracefully

- [ ] T016 [P] Create `backend/app/qdrant_client.py`
  - `QdrantService` class
  - Async method `search_chunks(query_embedding: List[float], top_k: int = 5) -> List[dict]`
  - Return chunks with metadata and scores
  - Method `get_collection_info() -> dict` for `/meta` endpoint
  - Handle connection errors

- [ ] T017 [P] Create `backend/app/gemini_agent.py`
  - `GeminiAgent` class
  - Configure with `GEMINI_API_KEY`
  - System prompts:
    - `SYSTEM_PROMPT_RAG`: Answer from context with citations in `[module:chapter:chunk_id]` format
    - `SYSTEM_PROMPT_SELECTIVE`: Answer ONLY from selection_text, return "NOT_FOUND" if not present
  - Async method `generate_rag_answer(query: str, chunks: List[dict]) -> Tuple[str, List[Citation]]`
  - Async method `generate_selective_answer(query: str, selection_text: str) -> str`
  - Parse citations from response text

- [ ] T018 Create `backend/app/db_neon.py` (optional)
  - `NeonDB` class for conversation history
  - Async pool with asyncpg
  - Method `save_conversation(session_id, query, response, citations)`
  - Method `save_feedback(session_id, message_id, rating, comment)`
  - Method `get_ingestion_metadata() -> dict`
  - Skip gracefully if `NEON_DB_URL` not configured

### Middleware

- [ ] T019 [P] Create `backend/app/middleware/__init__.py`
- [ ] T020 [P] Create `backend/app/middleware/auth.py`
  - `verify_admin(request: Request)` dependency
  - Check `Authorization: Bearer {ADMIN_SECRET}` header
  - Raise HTTPException 401 if invalid

- [ ] T021 [P] Create `backend/app/middleware/rate_limiter.py`
  - `RateLimitMiddleware` Starlette middleware
  - Track requests per IP per minute
  - Return 429 with `Retry-After` header when exceeded

**Checkpoint**: All backend services created and can be imported

---

## Phase 3: Backend Endpoints

**Purpose**: FastAPI routes for all API functionality

### Main Application

- [ ] T022 Create `backend/app/main.py`
  - Initialize FastAPI app with title, version
  - Add CORS middleware with allowed origins from config
  - Add RateLimitMiddleware
  - Include all routers with `/api` prefix
  - Health check endpoint `GET /health`
  - Startup event to validate configuration
  - Dependencies: T013, T019, T020, T021

### Chat Endpoints (US1, US2)

- [ ] T023 Create `backend/app/routers/__init__.py`
- [ ] T024 [US1] Create `backend/app/routers/chat.py`
  - `POST /chat` endpoint
    1. Embed query via CohereEmbedder
    2. Search Qdrant for top_k chunks
    3. If no chunks: return "I couldn't find relevant information in the book."
    4. Pass chunks to GeminiAgent.generate_rag_answer()
    5. Return ChatResponse with answer and citations
    6. Optionally save to Neon if configured
  - Dependencies: T015, T016, T017

- [ ] T025 [US2] Add `/selective-chat` endpoint to `backend/app/routers/chat.py`
  - `POST /selective-chat` endpoint
    1. Extract selection_text from request
    2. **CRITICAL**: Do NOT call Qdrant - this enforces selection-only mode
    3. Call GeminiAgent.generate_selective_answer()
    4. If response is "NOT_FOUND": return "Answer not found in selected text."
    5. Return ChatResponse with answer and selection citation
  - Add logging to verify no Qdrant calls
  - Dependencies: T017

### Ingest Endpoint (US3)

- [ ] T026 [US3] Create `backend/app/routers/ingest.py`
  - `POST /ingest` endpoint with `Depends(verify_admin)`
  - Trigger ingestion pipeline
  - Return IngestResponse with stats
  - Dependencies: T020, scripts/run_ingestion.py

### Meta & Feedback Endpoints (US5)

- [ ] T027 [US5] Create `backend/app/routers/meta.py`
  - `GET /meta` endpoint
    - Return API version, collection name, vector count, last ingestion timestamp
  - `POST /feedback` endpoint
    - Accept FeedbackRequest
    - Save to Neon if configured
    - Return success status
  - Dependencies: T016, T018

### Router Registration

- [ ] T028 Register all routers in `backend/app/main.py`
  - `app.include_router(chat.router, prefix="/api", tags=["chat"])`
  - `app.include_router(ingest.router, prefix="/api", tags=["ingest"])`
  - `app.include_router(meta.router, prefix="/api", tags=["meta"])`

**Checkpoint**: Backend runs with `uvicorn backend.app.main:app --reload` and all endpoints accessible

---

## Phase 4: Frontend / Docusaurus Plugin

**Purpose**: Chat UI integrated into Docusaurus book

### Plugin Structure

- [ ] T029 [P] Create `frontend/plugin-rag/package.json`
  - name: "docusaurus-plugin-rag-chatboard"
  - main: "./index.js"
  - No external dependencies (uses Docusaurus React)

- [ ] T030 Create `frontend/plugin-rag/index.js`
  - Export plugin function
  - `getThemePath()` → return theme components directory
  - `getClientModules()` → return client module path
  - `injectHtmlTags()` → inject CSS link

### API Client

- [ ] T031 [P] [US1] Create `frontend/src/api/chat.ts`
  - `API_BASE` constant from environment or default
  - `generalChat(query: string, topK?: number): Promise<ChatResponse>`
  - `selectiveChat(query: string, selectionText: string, selectionMeta?: object): Promise<ChatResponse>`
  - Error handling with user-friendly messages

### ChatBoard Component

- [ ] T032 [US4] Create `frontend/src/components/ChatBoard.tsx`
  - State: `isOpen`, `messages`, `input`, `isLoading`, `selectionText`
  - Message list with user/assistant styling
  - Input field with Enter key handling
  - Send button (disabled while loading)
  - Loading indicator ("Thinking...")
  - Citation links formatted as `module:chapter` with href to `source_url`
  - Clear history button
  - Close button
  - Import and use `generalChat` from api/chat.ts
  - Dependencies: T031

- [ ] T033 [US2] Add highlight listener to `frontend/src/components/ChatBoard.tsx`
  - `useEffect` hook listening to `mouseup` event
  - Get `window.getSelection().toString()`
  - If selection > 10 chars, show floating "Ask about selection" button
  - On click: call `selectiveChat()` with selection text and current URL
  - Auto-open chat window to show response
  - Clear selection after asking
  - Dependencies: T031

- [ ] T034 [P] [US4] Create `frontend/src/components/HighlightButton.tsx`
  - Floating button component for selection
  - Props: `position`, `onClick`, `visible`
  - Position near mouse cursor
  - Style: prominent button with "Ask about selection" text

### Styles

- [ ] T035 [P] [US4] Create `frontend/src/styles/chatboard.css`
  - `.chat-window`: fixed position, bottom-right, shadow, rounded corners
  - `.chat-header`: primary color, title, close button
  - `.chat-messages`: scrollable, max-height
  - `.message.user`: aligned right, primary-light background
  - `.message.assistant`: aligned left, surface background
  - `.chat-input`: flex row, input + button
  - `.toggle-button`: floating circle, fixed bottom-right
  - `.highlight-button`: floating, near selection
  - `.citations`: smaller text, links
  - `.loading`: pulse animation
  - Use CSS variables for Docusaurus theme compatibility

### Client Module

- [ ] T036 [US4] Create `frontend/plugin-rag/src/client-module.js`
  - Import React, createRoot
  - Import ChatBoard component
  - On window load: create root div, render ChatBoard
  - Dependencies: T032

### Plugin Registration

- [ ] T037 [US4] Update `physical-ai-robotics-book/docusaurus.config.ts`
  - Add plugin to `plugins` array:
    ```typescript
    plugins: [
      path.resolve(__dirname, '../frontend/plugin-rag'),
    ],
    ```
  - Ensure `customFields.chatEnabled: true`
  - Dependencies: T030

### Static Assets

- [ ] T038 [P] [US4] Copy `chatboard.css` to `physical-ai-robotics-book/static/css/chatboard.css`
  - Or configure plugin to serve CSS

**Checkpoint**: `npm run start` in physical-ai-robotics-book shows chat button, can open/close chat

---

## Phase 5: CI/CD & Deployment

**Purpose**: Automated workflows for ingestion and backend deployment

### GitHub Actions - Ingestion

- [ ] T039 [US3] Create `.github/workflows/ingest.yml`
  ```yaml
  name: Ingest Book Content
  on:
    push:
      paths: ['physical-ai-robotics-book/docs/**']
    workflow_dispatch:
  jobs:
    ingest:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with:
            python-version: '3.11'
        - run: pip install -r scripts/requirements.txt
        - run: python scripts/run_ingestion.py
          env:
            COHERE_API_KEY: ${{ secrets.COHERE_API_KEY }}
            QDRANT_URL: ${{ secrets.QDRANT_URL }}
            QDRANT_API_KEY: ${{ secrets.QDRANT_API_KEY }}
  ```

### GitHub Actions - Backend Deployment

- [ ] T040 [P] Create `.github/workflows/deploy-backend.yml`
  - Trigger on push to `backend/**` on main branch
  - Build Docker image
  - Push to Google Container Registry
  - Deploy to Cloud Run with environment variables
  - Alternative: Vercel serverless deployment

### Dockerfile

- [ ] T041 [P] Create `backend/Dockerfile`
  ```dockerfile
  FROM python:3.11-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY app/ app/
  EXPOSE 8080
  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
  ```

### Deployment Guide

- [ ] T042 [P] Create `docs/DEPLOY.md`
  - Prerequisites: GCP account, Qdrant Cloud, Cohere, Gemini API keys
  - Step 1: Create Qdrant collection
  - Step 2: Set up Cloud Run project
  - Step 3: Configure GitHub secrets
  - Step 4: Trigger first deployment
  - Step 5: Update frontend API_BASE with Cloud Run URL
  - Alternative: Vercel deployment steps

**Checkpoint**: Push to main triggers deployment, ingestion runs on docs changes

---

## Phase 6: Tests

**Purpose**: Verify functionality of all components

### Ingestion Tests

- [ ] T043 [US3] Create `tests/test_ingest.py`
  - `test_collect_chapters_finds_md_files()`
  - `test_chunker_produces_valid_sizes()` (200-800 tokens)
  - `test_chunk_id_is_deterministic()`
  - `test_embed_upsert_creates_vectors()` (mock Qdrant)
  - Fixtures: sample `.md` file, mock Cohere/Qdrant clients

### Retrieval Tests

- [ ] T044 [US1] Create `tests/test_retrieval.py`
  - `test_chat_endpoint_returns_citations()`
  - `test_chat_with_no_results_returns_message()`
  - `test_embedding_query_calls_cohere()`
  - `test_qdrant_search_returns_chunks()`
  - Use FastAPI TestClient

### Selective Chat Tests

- [ ] T045 [US2] Create `tests/test_selective_chat.py`
  - `test_selective_chat_does_not_call_qdrant()` ⚠️ CRITICAL
  - `test_selective_chat_answers_from_selection()`
  - `test_selective_chat_returns_not_found_for_unrelated_query()`
  - Mock QdrantService and verify it's never called

### Test Configuration

- [ ] T046 [P] Create `tests/__init__.py`
- [ ] T047 [P] Create `tests/conftest.py`
  - pytest fixtures for TestClient
  - Mock services
  - Sample data

- [ ] T048 [P] Add test dependencies to `backend/requirements.txt`
  - pytest>=7.4.0
  - pytest-asyncio>=0.23.0
  - httpx>=0.26.0

**Checkpoint**: `pytest tests/` passes all tests

---

## Phase 7: Documentation

**Purpose**: Setup guides, security documentation, usage examples

### README

- [ ] T049 Create `README.md` (update existing or create RAG section)
  - Project overview
  - Quick start (3 commands to run locally)
  - Environment variables table
  - API endpoints documentation
  - Screenshots of chat UI
  - Troubleshooting section

### Security Documentation

- [ ] T050 [P] Create `SECURITY.md`
  - Key storage: environment variables only, never in code
  - Key rotation: how to rotate each key
  - Rate limiting: configuration
  - Admin authentication: how ADMIN_SECRET works
  - CORS: allowed origins configuration
  - Qdrant security: API key authentication
  - Neon security: connection string handling
  - GitHub secrets: how secrets are managed

### Example Files

- [ ] T051 [P] Create `examples/example_doc.md`
  - Sample Markdown document for testing ingestion
  - Include frontmatter with title/sidebar_position
  - Multiple paragraphs for chunking

- [ ] T052 [P] Create `examples/example_curl_commands.txt`
  ```bash
  # Health check
  curl http://localhost:8000/health

  # General chat
  curl -X POST http://localhost:8000/api/chat \
    -H "Content-Type: application/json" \
    -d '{"query": "What is physical AI?", "top_k": 5}'

  # Selective chat
  curl -X POST http://localhost:8000/api/selective-chat \
    -H "Content-Type: application/json" \
    -d '{"query": "Explain this", "selection_text": "Humanoid robots are..."}'

  # Trigger ingestion (admin)
  curl -X POST http://localhost:8000/api/ingest \
    -H "Authorization: Bearer YOUR_ADMIN_SECRET"

  # Get metadata
  curl http://localhost:8000/api/meta

  # Submit feedback
  curl -X POST http://localhost:8000/api/feedback \
    -H "Content-Type: application/json" \
    -d '{"session_id": "abc123", "message_id": "msg1", "rating": 5}'
  ```

**Checkpoint**: New developer can set up and run project using only README

---

## Phase 8: Polish & Integration

**Purpose**: Final integration, cleanup, and validation

- [ ] T053 [P] Run full ingestion on production docs and verify vector count
- [ ] T054 [P] Test chat UI in production build (`npm run build && npm run serve`)
- [ ] T055 End-to-end test: highlight text → ask → verify answer from selection only
- [ ] T056 [P] Verify no API keys exposed in browser network tab
- [ ] T057 [P] Performance test: measure response time for chat queries
- [ ] T058 Code cleanup: remove unused imports, add docstrings
- [ ] T059 [P] Create `.env.example` with all variables documented
- [ ] T060 Final review: run quickstart from README on fresh environment

**Checkpoint**: Production-ready RAG Chatboard

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 0 (Prep)
    ↓
Phase 1 (Scripts) ←─────────┐
    ↓                       │
Phase 2 (Backend Foundation)│
    ↓                       │
Phase 3 (Backend Endpoints)─┤
    ↓                       │
Phase 4 (Frontend) ─────────┤
    ↓                       │
Phase 5 (CI/CD) ────────────┘
    ↓
Phase 6 (Tests)
    ↓
Phase 7 (Docs)
    ↓
Phase 8 (Polish)
```

### Critical Path

1. **T001-T004**: Environment setup (blocks everything)
2. **T005-T010**: Scripts (blocks ingestion testing)
3. **T011-T021**: Backend services (blocks endpoints)
4. **T022-T028**: Backend endpoints (blocks frontend integration)
5. **T029-T038**: Frontend (blocks user testing)

### Parallel Opportunities

| Phase | Parallel Tasks |
|-------|----------------|
| Phase 0 | T002, T003, T004 |
| Phase 1 | T005 (with T006-T010) |
| Phase 2 | T015, T016, T017, T019, T020, T021 |
| Phase 4 | T029, T031, T034, T035 |
| Phase 5 | T040, T041, T042 |
| Phase 6 | T046, T047, T048 |
| Phase 7 | T050, T051, T052 |
| Phase 8 | T053, T054, T056, T057, T059 |

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 0: Prep
2. Complete Phase 1: Scripts (ingestion working)
3. Complete Phase 2: Backend Foundation
4. Complete T024 only from Phase 3 (`/chat` endpoint)
5. Minimal Phase 4: Basic ChatBoard without highlight
6. **VALIDATE**: Can ask questions and get answers with citations

### Incremental Delivery

1. **MVP**: General Q&A chat working → Deploy
2. **v1.1**: Add selective chat (US2) → Deploy
3. **v1.2**: Add full UI polish (US4) → Deploy
4. **v1.3**: Add observability (US5) → Deploy
5. **v1.4**: Complete CI/CD automation → Deploy

### Single Developer Schedule (7 days)

| Day | Tasks | Deliverable |
|-----|-------|-------------|
| 1 | T001-T010 | Ingestion pipeline working |
| 2 | T011-T018 | Backend services ready |
| 3 | T019-T028 | All endpoints functional |
| 4 | T029-T038 | Chat UI integrated |
| 5 | T039-T042 | CI/CD deployed |
| 6 | T043-T052 | Tests + docs complete |
| 7 | T053-T060 | Polish, review, ship |

---

## Notes

- [P] tasks = different files, can run in parallel
- [USx] label maps task to specific user story for traceability
- ⚠️ CRITICAL in T045: Selective chat MUST NOT call Qdrant
- Commit after each task or logical group
- Stop at any checkpoint to validate independently
- Test locally before pushing to trigger CI/CD