# RAG Chatboard for Physical AI & Humanoid Robotics Book

A production-ready Retrieval-Augmented Generation (RAG) system for the Docusaurus textbook.

![Chatboard UI](https://via.placeholder.com/800x450.png?text=RAG+Chatboard+Preview)

## Features

- **Context-Aware Chat**: Ask questions about the book content.
- **Selective Query**: Highlight any text in the book to ask specific questions about it.
- **Source Citations**: Every answer includes links to the specific chapters used.
- **Admin Ingestion**: Automated pipeline to ingest book content into Qdrant vector database.
- **Secure Architecture**: API keys are stored securely on the backend; no exposure to client.

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Qdrant Cloud Account
- Cohere API Key
- Gemini API Key

### 1. Setup Environment

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

### 2. Install Dependencies

```bash
# Install ingestion scripts dependencies
pip install -r scripts/requirements.txt

# Install backend dependencies
pip install -r backend/requirements.txt
```

### 3. Ingest Content

Index the book content into Qdrant:

```bash
python -m scripts.run_ingestion
```

### 4. Run Backend Server

Start the FastAPI backend:

```bash
uvicorn backend.app.main:app --reload
```

Server runs at: `http://localhost:8000`
Docs available at: `http://localhost:8000/docs`

### 5. Run Frontend (Docusaurus)

```bash
cd physical-ai-robotics-book
npm start
```

The chat button will appear in the bottom right corner.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | General RAG chat question |
| POST | `/api/selective-chat` | Chat about selected text (no retrieval) |
| POST | `/api/ingest` | Trigger content ingestion (Admin only) |
| GET | `/api/meta` | Get collection metadata |

## Architecture

- **Frontend**: Docusaurus Plugin + React ChatBoard component
- **Backend**: FastAPI (Python)
- **Vector DB**: Qdrant Cloud
- **Embeddings**: Cohere `embed-english-v3.0`
- **LLM**: Google Gemini `gemini-1.5-flash`

## Project Structure

```
.
├── backend/               # FastAPI Application
│   ├── app/               # App code
│   │   ├── middleware/    # Auth & Rate limiting
│   │   ├── routers/       # API endpoints
│   │   └── services...    # Clients (Cohere, Qdrant, Gemini)
├── frontend/
│   └── plugin-rag/        # Docusaurus Plugin
├── scripts/               # Ingestion pipeline
└── physical-ai-robotics-book/ # Main Docusaurus site
```

## Security

See [SECURITY.md](SECURITY.md) for details on key management and security practices.
