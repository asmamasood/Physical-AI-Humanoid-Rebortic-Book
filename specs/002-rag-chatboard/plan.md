# Implementation Plan: RAG Chatboard

**Branch**: `002-rag-chatboard` | **Date**: 2025-12-17 | **Spec**: [spec.md](file:///d:/digital-book/specs/002-rag-chatboard/spec.md)  
**Input**: Feature specification from `specs/002-rag-chatboard/spec.md`

## Summary

Build a production-ready RAG Chatboard for the Physical AI & Humanoid Robotics Docusaurus book. The system ingests Markdown chapters, chunks and embeds them via Cohere, stores vectors in Qdrant Cloud, and serves queries through a FastAPI backend that synthesizes answers via Gemini with citations. Includes a selective-chat mode that answers strictly from user-highlighted text without Qdrant lookup.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript/React (frontend)  
**Primary Dependencies**: FastAPI, Cohere SDK, Qdrant Client, Google Generative AI, Docusaurus 3.x  
**Storage**: Qdrant Cloud (vectors), Neon Serverless Postgres (optional metadata/history)  
**Testing**: pytest (backend), Playwright (E2E)  
**Target Platform**: Cloud Run / Vercel (backend), GitHub Pages (frontend)  
**Project Type**: Web application (backend + frontend plugin)  
**Performance Goals**: <5s p95 response time, 100 concurrent sessions  
**Constraints**: All API keys server-side only, rate limiting required  
**Scale/Scope**: ~20 chapters, 4 modules, estimated 200-500 chunks

## Constitution Check

- [x] **I. Content Integrity**: RAG answers derived only from book content with citations
- [x] **II. Rigorous Sourcing**: Citations in `module:chapter:chunk_id` format with clickable links
- [x] **III. Accessible Academic Style**: Chat UI supports Q&A about academic content
- [x] **IV. Bilingual Delivery**: Plugin compatible with Docusaurus i18n (en/ur locales)
- [x] **V. Docusaurus Implementation**: Plugin architecture for Docusaurus v3, GitHub Pages deployment
- [x] **VI. Modular Structure**: Ingestion respects 4-module structure in metadata

---

## Project Structure

### Documentation (this feature)

```text
specs/002-rag-chatboard/
├── spec.md              # Feature specification
├── plan.md              # This file
└── tasks.md             # Task breakdown (next step)
```

### Source Code (repository root)

```text
# Backend (FastAPI)
backend/
├── main.py                     # FastAPI app entry point
├── config.py                   # Environment configuration
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Cloud Run deployment
├── routers/
│   ├── chat.py                 # /chat, /selective-chat endpoints
│   ├── ingest.py               # /ingest endpoint (admin)
│   └── meta.py                 # /meta, /feedback endpoints
├── services/
│   ├── qdrant_client.py        # Qdrant wrapper
│   ├── cohere_embedder.py      # Cohere embedding service
│   ├── gemini_agent.py         # Gemini LLM wrapper
│   └── neon_db.py              # Optional: Neon Postgres
├── middleware/
│   ├── auth.py                 # Admin auth for ingest
│   └── rate_limiter.py         # Rate limiting
├── utils/
│   └── logger.py               # Structured logging
└── tests/
    ├── unit/
    └── integration/

# Ingestion Scripts
scripts/
├── collect_chapters.py         # Enumerate .md files, extract frontmatter
├── chunker.py                  # Deterministic chunking (200-800 tokens)
├── embed_upsert.py             # Cohere embed → Qdrant upsert
└── run_ingestion.py            # Orchestration script

# Frontend (Docusaurus Plugin)
frontend/
└── plugin-rag/
    ├── package.json
    ├── index.js                # Plugin entry point
    └── src/
        ├── ChatBoard.tsx       # Main chat component
        ├── HighlightListener.tsx
        ├── api/
        │   └── chat.ts         # API client
        ├── theme/
        │   └── ChatBoard.css
        └── utils/
            └── highlight.ts

# CI/CD
.github/workflows/
├── ingest.yml                  # Ingestion on docs changes
└── deploy-backend.yml          # Backend deployment
```

---

## Phase 0 — Preparation

### Objectives
- Collect and validate all required secrets
- Decide deployment target for FastAPI
- Set up development environment

### Secrets Required

| Secret | Source | Usage |
|--------|--------|-------|
| `COHERE_API_KEY` | [cohere.com](https://dashboard.cohere.com/api-keys) | Embeddings |
| `QDRANT_URL` | [cloud.qdrant.io](https://cloud.qdrant.io) | Vector database endpoint |
| `QDRANT_API_KEY` | Qdrant Cloud dashboard | Vector database auth |
| `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com/app/apikey) | LLM |
| `NEON_DB_URL` | [neon.tech](https://console.neon.tech) (optional) | Metadata/history |
| `ADMIN_SECRET` | Generate with `openssl rand -hex 32` | Ingest endpoint auth |

### Deployment Decision

> [!IMPORTANT]
> **Recommended: Cloud Run** for FastAPI deployment
> - Native Docker support
> - Auto-scaling
> - Easy secrets management via Secret Manager
> - Pay-per-request pricing

Alternative: Vercel Serverless Functions (if team prefers JS ecosystem)

### Deliverables
- [ ] All secrets collected and documented in `.env.example`
- [ ] Qdrant Cloud collection `book_v1` created
- [ ] Cloud Run project configured (or Vercel project)
- [ ] Local development environment validated

---

## Phase 1 — Data Pipeline

### 1.1 Chapter Collection

**File**: `scripts/collect_chapters.py`

```python
# Pseudocode
def collect_chapters(docs_root: Path) -> List[Chapter]:
    """
    Recursively enumerate .md files from docs_root.
    Extract frontmatter (title, sidebar_position, module).
    Return list of Chapter objects with content.
    """
    chapters = []
    for md_file in docs_root.rglob("*.md"):
        frontmatter, content = parse_markdown(md_file)
        module = extract_module_from_path(md_file)  # e.g., "module-1"
        chapters.append(Chapter(
            path=md_file,
            module=module,
            title=frontmatter.get("title", md_file.stem),
            content=content,
            source_url=generate_url(md_file)
        ))
    return chapters
```

### 1.2 Chunking

**File**: `scripts/chunker.py`

```python
# Pseudocode
def chunk_chapter(chapter: Chapter, min_tokens=200, max_tokens=800) -> List[Chunk]:
    """
    Deterministic chunking with overlap.
    Generate stable chunk_id: hash(module + chapter + content[:100])
    Track start_pos, end_pos, token_count.
    """
    chunks = []
    text = clean_markdown(chapter.content)
    sentences = split_into_sentences(text)
    
    current_chunk = []
    current_tokens = 0
    start_pos = 0
    
    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)
        if current_tokens + sentence_tokens > max_tokens and current_tokens >= min_tokens:
            # Finalize chunk
            chunk_text = " ".join(current_chunk)
            chunk_id = generate_chunk_id(chapter.module, chapter.title, chunk_text)
            chunks.append(Chunk(
                chunk_id=chunk_id,
                module=chapter.module,
                chapter=chapter.title,
                content=chunk_text,
                source_url=chapter.source_url,
                start_pos=start_pos,
                end_pos=start_pos + len(chunk_text),
                token_count=current_tokens
            ))
            # Overlap: keep last 2 sentences
            current_chunk = current_chunk[-2:]
            current_tokens = sum(count_tokens(s) for s in current_chunk)
            start_pos = start_pos + len(chunk_text) - len(" ".join(current_chunk))
        
        current_chunk.append(sentence)
        current_tokens += sentence_tokens
    
    # Don't forget final chunk
    if current_chunk:
        # ... finalize remaining
    
    return chunks
```

### 1.3 Embedding & Upserting

**File**: `scripts/embed_upsert.py`

```python
# Pseudocode
import cohere
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

def embed_and_upsert(chunks: List[Chunk], collection_name="book_v1"):
    """
    Embed chunks via Cohere, upsert to Qdrant.
    """
    co = cohere.Client(os.environ["COHERE_API_KEY"])
    qdrant = QdrantClient(
        url=os.environ["QDRANT_URL"],
        api_key=os.environ["QDRANT_API_KEY"]
    )
    
    # Ensure collection exists
    if collection_name not in [c.name for c in qdrant.get_collections().collections]:
        qdrant.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
        )
    
    # Batch embed
    texts = [c.content for c in chunks]
    embeddings = co.embed(texts=texts, model="embed-english-v3.0", input_type="search_document").embeddings
    
    # Upsert points
    points = [
        PointStruct(
            id=c.chunk_id,
            vector=embeddings[i],
            payload={
                "module": c.module,
                "chapter": c.chapter,
                "content": c.content,
                "source_url": c.source_url,
                "start_pos": c.start_pos,
                "end_pos": c.end_pos,
                "token_count": c.token_count
            }
        )
        for i, c in enumerate(chunks)
    ]
    qdrant.upsert(collection_name=collection_name, points=points)
    
    return len(points)
```

### 1.4 Unit Tests

**File**: `scripts/tests/test_ingestion.py`

```python
def test_chunk_sizes():
    """Verify all chunks are 200-800 tokens."""
    
def test_chunk_id_determinism():
    """Same content produces same chunk_id."""
    
def test_qdrant_upsert():
    """Verify vectors exist in Qdrant after upsert."""
```

### Deliverables
- [ ] `scripts/collect_chapters.py` implemented and tested
- [ ] `scripts/chunker.py` implemented with deterministic IDs
- [ ] `scripts/embed_upsert.py` successfully upserting to `book_v1`
- [ ] Unit tests passing
- [ ] Sample ingestion run documented

---

## Phase 2 — Backend

### 2.1 FastAPI Application Structure

**File**: `backend/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import chat, ingest, meta
from middleware.rate_limiter import RateLimitMiddleware

app = FastAPI(title="RAG Chatboard API", version="1.0.0")

# CORS for Docusaurus frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://asmamasood.github.io", "http://localhost:3000"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Rate limiting
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)

# Routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(ingest.router, prefix="/api", tags=["ingest"])
app.include_router(meta.router, prefix="/api", tags=["meta"])

@app.get("/health")
async def health():
    return {"status": "ok"}
```

### 2.2 Chat Endpoints

**File**: `backend/routers/chat.py`

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.qdrant_client import search_chunks
from services.gemini_agent import generate_answer
from services.cohere_embedder import embed_query

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    session_id: str | None = None
    top_k: int = 5

class SelectiveChatRequest(BaseModel):
    query: str
    selection_text: str
    selection_meta: dict | None = None
    session_id: str | None = None

class ChatResponse(BaseModel):
    answer: str
    citations: list[dict]
    session_id: str | None

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """RAG-based chat with Qdrant retrieval."""
    # 1. Embed query
    query_embedding = await embed_query(request.query)
    
    # 2. Search Qdrant
    chunks = await search_chunks(query_embedding, top_k=request.top_k)
    
    if not chunks:
        return ChatResponse(
            answer="I couldn't find relevant information in the book.",
            citations=[],
            session_id=request.session_id
        )
    
    # 3. Generate answer with Gemini
    answer, citations = await generate_answer(request.query, chunks)
    
    return ChatResponse(
        answer=answer,
        citations=citations,
        session_id=request.session_id
    )

@router.post("/selective-chat", response_model=ChatResponse)
async def selective_chat(request: SelectiveChatRequest):
    """
    Answer based ONLY on selection_text.
    MUST NOT query Qdrant.
    """
    # NO Qdrant lookup - this is critical for security/compliance
    
    answer = await generate_selective_answer(
        query=request.query,
        selection_text=request.selection_text
    )
    
    if not answer or answer == "NOT_FOUND":
        return ChatResponse(
            answer="Answer not found in selected text.",
            citations=[],
            session_id=request.session_id
        )
    
    return ChatResponse(
        answer=answer,
        citations=[{
            "type": "selection",
            "source": "user_selection",
            "url": request.selection_meta.get("url") if request.selection_meta else None
        }],
        session_id=request.session_id
    )
```

### 2.3 Gemini Agent Wrapper

**File**: `backend/services/gemini_agent.py`

```python
import google.generativeai as genai
from config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

SYSTEM_PROMPT_RAG = """You are a helpful assistant for the Physical AI & Humanoid Robotics textbook.
Answer the user's question based ONLY on the provided context chunks.
For each piece of information you use, cite the source in format [module:chapter:chunk_id].
If the answer is not in the context, say "I couldn't find this information in the book."

Context:
{context}

Question: {query}

Answer with citations:"""

SYSTEM_PROMPT_SELECTIVE = """You are a helpful assistant.
Answer the user's question based STRICTLY on the following selected text.
Do NOT use any external knowledge.
If the answer cannot be found in the selected text, respond with exactly: NOT_FOUND

Selected Text:
{selection_text}

Question: {query}

Answer:"""

async def generate_answer(query: str, chunks: list) -> tuple[str, list]:
    """Generate RAG answer with citations."""
    context = "\n\n".join([
        f"[{c['module']}:{c['chapter']}:{c['chunk_id']}]\n{c['content']}"
        for c in chunks
    ])
    
    prompt = SYSTEM_PROMPT_RAG.format(context=context, query=query)
    response = await model.generate_content_async(prompt)
    
    # Extract citations from response
    citations = extract_citations(response.text, chunks)
    
    return response.text, citations

async def generate_selective_answer(query: str, selection_text: str) -> str:
    """Generate answer strictly from selection."""
    prompt = SYSTEM_PROMPT_SELECTIVE.format(selection_text=selection_text, query=query)
    response = await model.generate_content_async(prompt)
    return response.text.strip()
```

### 2.4 Middleware

**File**: `backend/middleware/auth.py`

```python
from fastapi import Request, HTTPException
from config import settings

async def verify_admin(request: Request):
    """Verify admin secret for protected endpoints."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header != f"Bearer {settings.ADMIN_SECRET}":
        raise HTTPException(status_code=401, detail="Unauthorized")
```

**File**: `backend/middleware/rate_limiter.py`

```python
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.rpm = requests_per_minute
        self.requests = defaultdict(list)
    
    async def dispatch(self, request, call_next):
        client_ip = request.client.host
        now = time.time()
        
        # Clean old requests
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] 
            if now - t < 60
        ]
        
        if len(self.requests[client_ip]) >= self.rpm:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
                headers={"Retry-After": "60"}
            )
        
        self.requests[client_ip].append(now)
        return await call_next(request)
```

### 2.5 Ingest Endpoint

**File**: `backend/routers/ingest.py`

```python
from fastapi import APIRouter, Depends
from middleware.auth import verify_admin

router = APIRouter()

@router.post("/ingest", dependencies=[Depends(verify_admin)])
async def trigger_ingestion():
    """
    Trigger full ingestion pipeline.
    Protected by ADMIN_SECRET.
    """
    from scripts.run_ingestion import run_full_ingestion
    
    result = await run_full_ingestion()
    return {
        "status": "completed",
        "files_processed": result.files,
        "chunks_created": result.chunks,
        "vectors_upserted": result.vectors
    }
```

### Deliverables
- [ ] `backend/main.py` with CORS, rate limiting, routers
- [ ] `backend/routers/chat.py` with `/chat` and `/selective-chat`
- [ ] `backend/services/gemini_agent.py` with system prompts
- [ ] `backend/middleware/auth.py` and `rate_limiter.py`
- [ ] Unit tests for retrieval and selective-chat behavior
- [ ] Local testing with `uvicorn backend.main:app --reload`

---

## Phase 3 — Frontend / Docusaurus Plugin

### 3.1 Plugin Structure

**File**: `frontend/plugin-rag/index.js`

```javascript
const path = require('path');

module.exports = function pluginRag(context, options) {
  return {
    name: 'docusaurus-plugin-rag-chatboard',
    
    getThemePath() {
      return path.resolve(__dirname, './src/theme');
    },
    
    getClientModules() {
      return [path.resolve(__dirname, './src/client-module')];
    },
    
    injectHtmlTags() {
      return {
        headTags: [
          {
            tagName: 'link',
            attributes: {
              rel: 'stylesheet',
              href: '/css/chatboard.css',
            },
          },
        ],
      };
    },
  };
};
```

### 3.2 ChatBoard Component

**File**: `frontend/plugin-rag/src/ChatBoard.tsx`

```tsx
import React, { useState, useEffect, useRef } from 'react';
import { generalChat, selectiveChat } from './api/chat';
import styles from './theme/ChatBoard.module.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
}

interface Citation {
  module: string;
  chapter: string;
  chunk_id: string;
  source_url: string;
}

export default function ChatBoard() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectionText, setSelectionText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Handle text selection
  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection()?.toString().trim();
      if (selection && selection.length > 10) {
        setSelectionText(selection);
      } else {
        setSelectionText('');
      }
    };
    
    document.addEventListener('mouseup', handleSelection);
    return () => document.removeEventListener('mouseup', handleSelection);
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    
    try {
      const response = await generalChat(input);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.answer,
        citations: response.citations
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, something went wrong. Please try again.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAskSelection = async () => {
    if (!selectionText) return;
    
    setIsOpen(true);
    setIsLoading(true);
    
    const userMessage: Message = { 
      role: 'user', 
      content: `[About selection] ${selectionText.slice(0, 100)}...` 
    };
    setMessages(prev => [...prev, userMessage]);
    
    try {
      const response = await selectiveChat(
        'Explain this text',
        selectionText,
        { url: window.location.href }
      );
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.answer,
        citations: response.citations
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, something went wrong.'
      }]);
    } finally {
      setIsLoading(false);
      setSelectionText('');
    }
  };

  return (
    <>
      {/* Floating selection button */}
      {selectionText && (
        <button 
          className={styles.selectionButton}
          onClick={handleAskSelection}
        >
          Ask about selection
        </button>
      )}
      
      {/* Chat toggle button */}
      {!isOpen && (
        <button 
          className={styles.toggleButton}
          onClick={() => setIsOpen(true)}
        >
          💬
        </button>
      )}
      
      {/* Chat window */}
      {isOpen && (
        <div className={styles.chatWindow}>
          <div className={styles.header}>
            <span>RAG Chatboard</span>
            <button onClick={() => setIsOpen(false)}>✕</button>
          </div>
          
          <div className={styles.messages}>
            {messages.map((msg, i) => (
              <div key={i} className={styles[msg.role]}>
                <p>{msg.content}</p>
                {msg.citations && (
                  <div className={styles.citations}>
                    {msg.citations.map((c, j) => (
                      <a key={j} href={c.source_url}>
                        {c.module}:{c.chapter}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {isLoading && <div className={styles.loading}>Thinking...</div>}
            <div ref={messagesEndRef} />
          </div>
          
          <div className={styles.inputArea}>
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyPress={e => e.key === 'Enter' && handleSend()}
              placeholder="Ask about the book..."
              disabled={isLoading}
            />
            <button onClick={handleSend} disabled={isLoading}>Send</button>
          </div>
        </div>
      )}
    </>
  );
}
```

### 3.3 API Client

**File**: `frontend/plugin-rag/src/api/chat.ts`

```typescript
const API_BASE = process.env.NODE_ENV === 'production' 
  ? 'https://your-backend.run.app/api'  // Cloud Run URL
  : 'http://localhost:8000/api';

export async function generalChat(query: string, topK = 5) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, top_k: topK }),
  });
  
  if (!response.ok) throw new Error('Chat request failed');
  return response.json();
}

export async function selectiveChat(
  query: string, 
  selectionText: string,
  selectionMeta?: { url?: string }
) {
  const response = await fetch(`${API_BASE}/selective-chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, selection_text: selectionText, selection_meta: selectionMeta }),
  });
  
  if (!response.ok) throw new Error('Selective chat request failed');
  return response.json();
}
```

### 3.4 Docusaurus Configuration

**File**: `physical-ai-robotics-book/docusaurus.config.ts` (addition)

```typescript
// Add to plugins array
plugins: [
  [
    path.resolve(__dirname, '../frontend/plugin-rag'),
    {
      apiEndpoint: process.env.RAG_API_ENDPOINT || 'http://localhost:8000/api',
    },
  ],
],
```

### Deliverables
- [ ] `frontend/plugin-rag/` fully implemented
- [ ] `ChatBoard.tsx` with message list, input, citations
- [ ] Highlight listener with floating button
- [ ] API client for `/chat` and `/selective-chat`
- [ ] Plugin registered in `docusaurus.config.ts`
- [ ] CSS styling matching Docusaurus theme

---

## Phase 4 — CI/CD & Deployment

### 4.1 Ingestion Workflow

**File**: `.github/workflows/ingest.yml`

```yaml
name: Ingest Book Content

on:
  push:
    paths:
      - 'physical-ai-robotics-book/docs/**'
  workflow_dispatch:  # Manual trigger

jobs:
  ingest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r scripts/requirements.txt
      
      - name: Run ingestion
        env:
          COHERE_API_KEY: ${{ secrets.COHERE_API_KEY }}
          QDRANT_URL: ${{ secrets.QDRANT_URL }}
          QDRANT_API_KEY: ${{ secrets.QDRANT_API_KEY }}
        run: python scripts/run_ingestion.py
      
      - name: Report results
        run: echo "Ingestion completed successfully"
```

### 4.2 Backend Deployment (Cloud Run)

**File**: `.github/workflows/deploy-backend.yml`

```yaml
name: Deploy Backend to Cloud Run

on:
  push:
    paths:
      - 'backend/**'
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2
      
      - name: Build and push Docker image
        run: |
          gcloud builds submit --tag gcr.io/${{ secrets.GCP_PROJECT_ID }}/rag-chatboard-api backend/
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy rag-chatboard-api \
            --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/rag-chatboard-api \
            --platform managed \
            --region us-central1 \
            --allow-unauthenticated \
            --set-env-vars "COHERE_API_KEY=${{ secrets.COHERE_API_KEY }}" \
            --set-secrets "GEMINI_API_KEY=gemini-api-key:latest,QDRANT_API_KEY=qdrant-api-key:latest"
```

### 4.3 Dockerfile

**File**: `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Deliverables
- [ ] `.github/workflows/ingest.yml` triggered on docs changes
- [ ] `.github/workflows/deploy-backend.yml` for Cloud Run
- [ ] `backend/Dockerfile` configured
- [ ] All secrets configured in GitHub repository settings
- [ ] Cloud Run service deployed and accessible
- [ ] Secrets documentation in `.env.example`

---

## Phase 5 — QA & Handoff

### 5.1 E2E Tests

**File**: `tests/e2e/test_rag_chatboard.py`

```python
import pytest
import requests

API_BASE = "https://your-backend.run.app/api"

def test_general_chat():
    """Test RAG query returns answer with citations."""
    response = requests.post(f"{API_BASE}/chat", json={
        "query": "What is physical AI?",
        "top_k": 5
    })
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data

def test_selective_chat():
    """Test selective chat answers only from selection."""
    response = requests.post(f"{API_BASE}/selective-chat", json={
        "query": "Summarize this",
        "selection_text": "Robots can sense their environment using various sensors."
    })
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    # Verify no Qdrant-based citations
    assert all(c.get("type") == "selection" for c in data.get("citations", []))

def test_selective_chat_not_found():
    """Test selective chat returns NOT_FOUND for unrelated query."""
    response = requests.post(f"{API_BASE}/selective-chat", json={
        "query": "What is quantum computing?",
        "selection_text": "Robots can sense their environment."
    })
    assert response.status_code == 200
    data = response.json()
    assert "not found" in data["answer"].lower()
```

### 5.2 Documentation

**File**: `README.md` (RAG Chatboard section)

```markdown
## RAG Chatboard

### Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in secrets
3. Install backend dependencies: `pip install -r backend/requirements.txt`
4. Install frontend dependencies: `cd physical-ai-robotics-book && npm install`

### Running Locally

```bash
# Backend
cd backend
uvicorn main:app --reload

# Frontend (separate terminal)
cd physical-ai-robotics-book
npm run start
```

### Sample API Calls

```bash
# General chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the main topics in this book?", "top_k": 5}'

# Selective chat
curl -X POST http://localhost:8000/api/selective-chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain this", "selection_text": "Humanoid robots..."}'

# Trigger ingestion (admin)
curl -X POST http://localhost:8000/api/ingest \
  -H "Authorization: Bearer YOUR_ADMIN_SECRET"
```

### Testing

```bash
# Backend tests
cd backend && pytest

# E2E tests
pytest tests/e2e/
```
```

### Deliverables
- [ ] E2E tests for ingestion → query → selective-chat
- [ ] README updated with setup, run, and testing instructions
- [ ] Sample curl commands documented
- [ ] All tests passing in CI

---

## Complexity Tracking

No constitution violations. Architecture follows standard patterns.

---

## Timeline Estimate

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 0 - Prep | 0.5 days | Secrets collected, environment ready |
| Phase 1 - Data Pipeline | 1.5 days | Ingestion scripts working, Qdrant populated |
| Phase 2 - Backend | 2 days | FastAPI endpoints functional |
| Phase 3 - Frontend | 1.5 days | Chat UI integrated in Docusaurus |
| Phase 4 - CI/CD | 1 day | Workflows deployed |
| Phase 5 - QA | 0.5 days | Tests passing, docs complete |

**Total**: ~7 days (1 week) for focused single-dev effort

---

## Next Steps

1. **Review this plan** and approve
2. Run `/sp.tasks` to generate detailed task checklist
3. Begin Phase 0: Collect secrets and set up environment
