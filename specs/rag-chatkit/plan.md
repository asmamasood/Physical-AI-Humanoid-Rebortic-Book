# Plan: ChatKit RAG Integration

## 1. Scope and Dependencies
- **In Scope:**
  - Persistent Chat History (Postgres).
  - Modern "ChatKit" UI Components.
  - Streaming Support (Backend ready).
  - Multi-thread support (Sidebar).
- **Out of Scope:**
  - Multimedia attachments (files/images).
  - Group chat.
- **Dependencies:**
  - `better-auth`: For `user_id` linkage.
  - `asyncpg`: For non-blocking DB writes.
  - `react-markdown`: For rendering bot responses.

## 2. Key Decisions
- **Schema Design:** 
  - using `UUID` for IDs to prevent enumeration.
  - `user_id` is a string (matching Better Auth).
  - Storing `role` as simple string ("user"/"assistant").
- **API Strategy:**
  - `POST /api/chat/message`: Unified endpoint. Handles:
    1. Saving User Message.
    2. RAG Retrieval.
    3. LLM Generation.
    4. Saving Bot Message.
    5. Returning Bot Message.
  - *Trade-off*: Slightly higher latency than streaming immediately, but ensures data consistency.
- **UI Architecture:**
  - **Headless Hook (`useChatKit`)**: Manages logic.
  - **Dumb Components**: Presentational only.
  - Allows easy swapping of themes or layout (Floating vs Full Page).

## 3. Interfaces

### Database (`db_neon.py`)
```sql
CREATE TABLE chat_threads (
    id UUID PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE chat_messages (
    id UUID PRIMARY KEY,
    thread_id UUID REFERENCES chat_threads(id) ON DELETE CASCADE,
    role TEXT CHECK (role IN ('user', 'assistant')),
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Frontend (`useChatKit`)
```typescript
interface UseChatKit {
  messages: Message[];
  loading: boolean;
  sendMessage: (text: string) => Promise<void>;
  threadId: string | null;
  history: Thread[];
  createThread: () => void;
  loadThread: (id: string) => void;
}
```

## 4. Phase Breakdown

### Phase 1: Backend Infrastructure (Current)
- Implement Schema in `db_neon.py`.
- Create CRUD routers in `routers/chat_history.py`.

### Phase 2: Frontend Components
- Build `src/components/ChatKit/*`.
- Style with CSS Modules.

### Phase 3: Integration
- Wire `useChatKit` to Backend APIs.
- Replace `FloatingChat` internals.

## 5. Verification
- Use `curl` or Swagger to verify history persistence.
- Verify UI updates optimistically.
