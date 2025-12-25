# Specification: ChatKit RAG Integration

## 1. Goal Description
Upgrade the existing ephemeral RAG Chatbot into a **reusable, persistent "ChatKit" system**.
- **UI**: Adopt a "ChatKit" component architecture (modular, themeable, reusable).
- **Functionality**: Enable **History Saving** so users can continue past conversations.
- **RAG**: Maintain deep integration with the book's RAG backend.

## 2. Architecture: "ChatKit" Pattern

### Frontend Components (`src/components/ChatKit/`)
A modular UI library replacing the monolithic `FloatingChat`:
- `<ChatProvider>`: Context for state (messages, loading, error).
- `<ChatContainer>`: The main wrapper (floating or embedded).
- `<MessageList>`: Scrollable area rendering `<MessageBubble>`.
- `<MessageInput>`: Text area with "Send" and "Stop" controls.
- `<ChatHistorySidebar>`: List of past threads (collapsible).

### State Management (`useChatKit`)
A custom hook handling:
- `sendMessage(text)`: Optimistic updates + Backend API call.
- `loadHistory(threadId)`: Fetch past messages.
- `createNewThread()`: Reset state for new topic.
- `streamResponse`: Handle streaming tokens (optional).

## 3. Data Schema (History)

### Backend (FastAPI + Postgres)
New tables in `db_neon.py` to persist conversations:

**Table: `chat_threads`**
| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID (PK) | Unique Thread ID. |
| `user_id` | TEXT | Owner (linked to Auth). |
| `title` | TEXT | Auto-generated summary. |
| `created_at` | TIMESTAMP | Sort key. |

**Table: `chat_messages`**
| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID (PK) | Unique Message ID. |
| `thread_id` | UUID (FK) | Parent Thread. |
| `role` | TEXT | "user" or "assistant". |
| `content` | TEXT | Markdown text. |
| `timestamp` | TIMESTAMP | Order key. |

## 4. API Endpoints (Backend)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/chat/history` | List threads for current user. |
| `GET` | `/api/chat/history/{id}` | Get messages for a thread. |
| `POST` | `/api/chat/message` | Send message. Saves to DB automatically. Support RAG context. |
| `DELETE` | `/api/chat/history/{id}` | Delete a thread. |

## 5. Integration Plan

1. **Refactor Backend**: 
   - Update `routers/chat.py` to write to DB (`chat_messages`) instead of just returning ephemeral responses.
2. **Build ChatKit**:
   - Create `src/components/ChatKit` structure.
   - Implement `useChatKit` hook using `auth-client` for user ID.
3. **Replace Widget**:
   - Update `FloatingChat` to use `<ChatKit />` internally.
4. **UI Polish**:
   - Add "History" icon to floating widget header.
   - Show list of previous chats.

## 6. Access Control
- Strictly enforced by `user_id` from Better Auth.
- Users can only access their own history.
