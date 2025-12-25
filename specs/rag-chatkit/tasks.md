# Tasks: ChatKit RAG Integration

## Phase 1: Backend History Infrastructure
- [x] **Database Schema** <!-- id: 1 -->
  - [x] Update `db_neon.py` with `chat_threads` and `chat_messages` tables.
  - [x] Create Pydantic models for Thread/Message in `models.py`.
- [x] **API Endpoints** <!-- id: 2 -->
  - [x] Implement `GET /api/chat/history` (List threads).
  - [x] Implement `GET /api/chat/history/{id}` (Get stored messages).
  - [x] Update `POST /api/chat` to save User/Assistant messages to DB.
  - [x] Implement `DELETE /api/chat/history/{id}`.

## Phase 2: Frontend ChatKit Library
- [x] **Core Components** (`src/components/ChatKit/`) <!-- id: 3 -->
  - [x] `<ChatProvider>` (Context for messages, loading, threads).
  - [x] `<MessageList>` (Scrollable area, auto-scroll).
  - [x] `<MessageBubble>` (Markdown rendering, user/bot styles).
  - [x] `<MessageInput>` (Textarea, Send button, Stop button).
- [x] **Container & Sidebar** <!-- id: 4 -->
  - [x] `<ChatContainer>` (Layout wrapper).
  - [x] `<HistorySidebar>` (List of past threads, New Chat button).

## Phase 3: Integration
- [x] **Hook Implementation** <!-- id: 5 -->
  - [x] Implement `useChatKit` hook (API calls, state management).
- [x] **Floating Widget Upgrade** <!-- id: 6 -->
  - [x] Replace `FloatingChat` internal logic with `<ChatKit />`.
  - [x] Ensure Auth integration (`session.user.id`).

## Phase 4: Verification
- [x] **Manual Testing** <!-- id: 7 -->
  - [x] Verify messages persist after refresh.
  - [x] Verify can switch between threads.
  - [x] Verify RAG answers are still accurate.
