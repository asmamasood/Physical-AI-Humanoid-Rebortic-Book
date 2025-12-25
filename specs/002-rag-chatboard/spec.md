# Feature Specification: RAG Chatboard

**Feature Branch**: `002-rag-chatboard`  
**Created**: 2025-12-11  
**Updated**: 2025-12-17  
**Status**: Ready for Implementation  
**Input**: User description: "Build & embed a production-ready Retrieval-Augmented Generation (RAG) Chatboard into an existing Docusaurus book (deployed on GitHub Pages). The chatboard must answer user questions from the book, support 'highlight → ask' mode (answer strictly from selected text), and be secure (no secrets client-side)."

## Technology Stack

| Component | Technology | Environment Variable |
|-----------|------------|---------------------|
| Embeddings | Cohere | `COHERE_API_KEY` |
| Vector DB | Qdrant Cloud | `QDRANT_URL`, `QDRANT_API_KEY` |
| LLM | Gemini API | `GEMINI_API_KEY` |
| Backend | FastAPI (Python, async) | - |
| Metadata DB (Optional) | Neon Serverless Postgres | `NEON_DB_URL` |
| Frontend | Docusaurus plugin + React | - |
| CI/CD | GitHub Actions → Cloud Run / Vercel | - |

## User Scenarios & Testing *(mandatory)*

### User Story 1 - General Q&A from Book Content (Priority: P1)

Users want to ask general questions about the book's content and receive accurate answers, backed by evidence with precise citations.

**Why this priority**: This is the core RAG functionality, delivering the primary value proposition of making book content accessible through natural language queries.

**Independent Test**: Can be fully tested by posing various questions related to the book's topics and verifying that relevant, cited answers are returned with proper source attribution (module:chapter:chunk_id format).

**Acceptance Scenarios**:

1. **Given** a user is viewing any page in the Docusaurus book, **When** they type a general question into the chat interface, **Then** the chatboard responds with an accurate answer derived from the book's content, including inline citations in `module:chapter:chunk_id` format.
2. **Given** the chatboard receives a question, **When** the relevant information is scattered across multiple book sections, **Then** the chatboard synthesizes the information into a coherent answer with multiple citations referencing each source.
3. **Given** a user asks a question unrelated to the book content, **When** Qdrant retrieval returns no relevant chunks (low similarity scores), **Then** the chatboard responds with "I couldn't find an answer in the book."

---

### User Story 2 - Highlight-to-Ask Specifics (Priority: P1)

Users want to quickly get answers to questions about specific sections of the book by highlighting text and asking a question directly related to that selection, ensuring the answer is constrained STRICTLY to the highlighted context.

**Why this priority**: This provides a powerful, contextual interaction mode, enhancing the user's ability to deep-dive into specific content. Critical for precision and trust.

**Independent Test**: Can be tested by highlighting specific sentences or paragraphs and asking questions whose answers are contained strictly within the highlighted text. Verify the response is limited to that context and does NOT reference external sources.

**Acceptance Scenarios**:

1. **Given** a user has highlighted a specific paragraph in the Docusaurus book, **When** they invoke the "Ask Chatboard" feature with a question, **Then** the chatboard provides an answer strictly based on the highlighted text, without consulting Qdrant or any external content.
2. **Given** a user asks a question whose answer is NOT present in the highlighted selection, **When** the `/selective-chat` endpoint processes the request, **Then** the system returns: "Answer not found in selected text."
3. **Given** any request to `/selective-chat`, **When** the backend processes it, **Then** the backend MUST NOT query Qdrant under any circumstances.

---

### User Story 3 - Content Ingestion Pipeline (Priority: P1)

Content administrators need to ingest, chunk, embed, and index the book's Markdown content into Qdrant with proper metadata for accurate retrieval.

**Why this priority**: Without ingested content, the RAG system cannot function. This is the foundation for all retrieval functionality.

**Independent Test**: Can be tested by running the ingestion script against the docs directory and verifying vectors are created in Qdrant with correct metadata.

**Acceptance Scenarios**:

1. **Given** Markdown files exist in `physical-ai-robotics-book/docs/`, **When** the ingestion pipeline runs, **Then** each file is parsed, cleaned, chunked (200-800 tokens), embedded via Cohere, and upserted to Qdrant with metadata `{module, chapter, chunk_id, source_url, start_pos, end_pos, token_count}`.
2. **Given** a document is updated, **When** the ingestion runs via GitHub Actions on docs changes, **Then** only the changed document's chunks are re-indexed (incremental update).
3. **Given** the ingestion endpoint `/api/ingest`, **When** called without admin authentication, **Then** the request is rejected with 401 Unauthorized.

---

### User Story 4 - Chat UI and UX Integration (Priority: P2)

Users need an intuitive and seamlessly integrated chat interface and a clear highlight-to-query mechanism directly within the Docusaurus book.

**Why this priority**: A well-integrated and user-friendly interface is crucial for adoption and positive user experience.

**Independent Test**: Can be tested by navigating the Docusaurus site and interacting with the chat UI and highlighting features, verifying their visual and functional integration.

**Acceptance Scenarios**:

1. **Given** a user is browsing the Docusaurus book, **When** they click the chat button in the navbar, **Then** a chat window appears as a floating panel consistent with the site's theme.
2. **Given** a user highlights text on any documentation page, **When** the selection is complete, **Then** an "Ask Chatboard" button appears positioned near the selection.
3. **Given** a user clicks "Ask Chatboard" on highlighted text, **When** the response is received, **Then** the chat window opens automatically to display the response.

---

### User Story 5 - Observability & History (Priority: P3)

Administrators want to track ingestion runs and optionally store conversation history for analytics and debugging.

**Why this priority**: Important for production operations but not blocking core functionality.

**Independent Test**: Can be tested by running ingestion and verifying logs are captured; by having a conversation and verifying it's stored in Neon.

**Acceptance Scenarios**:

1. **Given** an ingestion run completes, **When** logs are checked, **Then** detailed logs show: files processed, chunks created, vectors upserted, errors encountered.
2. **Given** Neon DB is configured (`NEON_DB_URL` set), **When** a chat conversation occurs, **Then** the conversation is persisted with timestamp, user_id (optional), query, response, and citations.

---

### Edge Cases

- **Empty Qdrant Results**: If no chunks score above the similarity threshold, return "I couldn't find relevant information in the book."
- **Extremely Long Selections**: If highlighted text exceeds Gemini's context window, truncate and inform the user.
- **API Unavailability**: If Gemini/Cohere/Qdrant APIs are unavailable, return a user-friendly error with retry suggestion.
- **Rate Limiting**: If request rate exceeds limits, return 429 with retry-after header.
- **Malformed Input**: If user input contains injection attempts, sanitize and log the attempt.
- **Concurrent Ingestion**: If ingestion is already running, queue or reject new ingestion requests.

## Requirements *(mandatory)*

### Functional Requirements

#### Ingestion Pipeline

- **FR-001 (Content Extraction)**: System MUST read `.md` files from `physical-ai-robotics-book/docs/` directory recursively.
- **FR-002 (Content Cleaning)**: System MUST remove Markdown formatting, extract plain text while preserving semantic structure.
- **FR-003 (Chunking)**: System MUST chunk content into 200-800 token segments with configurable overlap.
- **FR-004 (Embedding)**: System MUST generate embeddings using Cohere Embed API for each chunk.
- **FR-005 (Vector Storage)**: System MUST upsert vectors to Qdrant Cloud with metadata: `{module, chapter, chunk_id, source_url, start_pos, end_pos, token_count}`.
- **FR-006 (Incremental Updates)**: System SHOULD support incremental ingestion (only changed files).

#### Retrieval

- **FR-007 (Semantic Search)**: System MUST perform semantic search on Qdrant with configurable `top_k` parameter.
- **FR-008 (Metadata Return)**: Retrieval MUST return chunk metadata and similarity scores alongside content.

#### Chat Endpoints

- **FR-009 (General Chat - `/chat`)**: System MUST accept user queries, perform retrieval, pass retrieved chunks to Gemini, and return synthesized responses with citations.
- **FR-010 (Citation Format)**: Citations MUST be formatted as `module:chapter:chunk_id` with clickable source links.
- **FR-011 (Selective Chat - `/selective-chat`)**: System MUST accept `selection_text` and optional `selection_meta`, pass ONLY selection_text to Gemini, and MUST NOT query Qdrant.
- **FR-012 (Strict Context Enforcement)**: If answer is not found in `selection_text`, system MUST return: "Answer not found in selected text."

#### Frontend

- **FR-013 (Docusaurus Plugin)**: System MUST provide a Docusaurus plugin that injects the chat UI.
- **FR-014 (Chat Window)**: Chat UI MUST provide input field, message history, loading states, and error feedback.
- **FR-015 (Highlight Detection)**: System MUST detect text selection on documentation pages.
- **FR-016 (Context Menu)**: System MUST display "Ask Chatboard" button on text selection.

### Non-Functional Requirements

#### Security

- **NFR-001 (Server-Side Keys)**: All API keys (`COHERE_API_KEY`, `QDRANT_API_KEY`, `GEMINI_API_KEY`, `NEON_DB_URL`) MUST be stored and managed exclusively server-side, NEVER exposed in client-side code or network requests.
- **NFR-002 (Backend Proxy)**: All LLM and database calls MUST be proxied through the backend—no direct client-to-API communication.
- **NFR-003 (Admin Authentication)**: Ingestion endpoints MUST require admin authentication.
- **NFR-004 (Rate Limiting)**: Chat endpoints MUST implement rate limiting to prevent abuse.
- **NFR-005 (Input Sanitization)**: All user input MUST be sanitized before processing.

#### Performance

- **NFR-006 (Response Time)**: Chat responses SHOULD complete within 5 seconds for 95th percentile.
- **NFR-007 (Concurrent Users)**: System SHOULD support 100 concurrent chat sessions.

#### Deployment

- **NFR-008 (Serverless Backend)**: Backend MUST be deployable to Cloud Run or Vercel serverless.
- **NFR-009 (CI/CD)**: GitHub Actions MUST trigger ingestion on docs directory changes.
- **NFR-010 (Static Frontend)**: Frontend MUST work when Docusaurus is deployed to GitHub Pages.

#### Observability

- **NFR-011 (Logging)**: Ingestion pipeline MUST log detailed operation metrics.
- **NFR-012 (Conversation History)**: System MAY persist conversation history in Neon Postgres when configured.

### Key Entities

- **Chunk**: A segment of book content (200-800 tokens) with metadata linking to source location.
- **Vector**: Embedding representation of a chunk stored in Qdrant.
- **Metadata**: `{module, chapter, chunk_id, source_url, start_pos, end_pos, token_count}`.
- **Chat Message**: User query or assistant response in a conversation.
- **Citation**: Reference to source chunk in format `module:chapter:chunk_id` with URL.
- **Selection**: User-highlighted text with optional metadata (URL, element ID).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001 (End-to-End RAG)**: Within 5 seconds of a user query, the system MUST successfully retrieve relevant chunks, generate a Gemini response, and return citations—validated by automated integration tests.
- **SC-002 (Selection Mode Enforcement)**: 100% of `/selective-chat` requests MUST be processed without any Qdrant queries—validated by backend access logging.
- **SC-003 (Citation Accuracy)**: 95% of returned citations MUST link to chunks containing information used in the answer—validated by manual review of sample responses.
- **SC-004 (UI Integration)**: The Docusaurus plugin MUST load on all pages without console errors and with <10% impact on page load time.
- **SC-005 (Security Compliance)**: Zero API keys MUST be detectable in client-side code, network requests, or browser console—validated by security audit.
- **SC-006 (Ingestion Pipeline)**: All `.md` files in docs directory MUST be successfully chunked and indexed—validated by comparing file count to Qdrant vector count.
- **SC-007 (Deployment Success)**: System MUST successfully deploy and function on GitHub Pages (frontend) + Cloud Run/Vercel (backend).