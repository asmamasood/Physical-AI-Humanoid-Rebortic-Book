# RAG Chatbot Upgrade Architecture 🏗️

## System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                           FRONTEND (Docusaurus + React)                     │
│                                                                             │
│  ┌───────────────┐      ┌───────────────┐      ┌───────────────┐          │
│  │ FloatingWidget│      │   ChatKit UI  │      │  Profile Page │          │
│  │               │      │               │      │               │          │
│  │ • Chat Input  │      │ • Thread List │      │ • User Info   │          │
│  │ • Send Button │      │ • Messages    │      │ • Points/Level│          │
│  │ • Text Select │      │ • Citations   │      │ • Preferences │          │
│  └───────┬───────┘      └───────┬───────┘      └───────┬───────┘          │
│          │                      │                      │                   │
└──────────┼──────────────────────┼──────────────────────┼───────────────────┘
           │                      │                      │
           │ POST /chat           │ GET /chat-history    │ GET /profile
           │                      │                      │
┌──────────▼──────────────────────▼──────────────────────▼───────────────────┐
│                                                                             │
│                       FASTAPI BACKEND (Python)                              │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         /chat Endpoint                               │   │
│  │                                                                      │   │
│  │  1. Validate Request (ChatRequest model)                            │   │
│  │  2. Generate Session ID (if not provided)                           │   │
│  │  3. Embed Query (Local/Cohere)                                      │   │
│  │  4. Search Qdrant (with filters)                                    │   │
│  │  5. Fetch User Context (Profile, History, Points)                   │   │
│  │  6. Call GeminiAgent.generate_rag_answer()  ◄─── UPGRADE HERE      │   │
│  │  7. Save to Database (Neon)                                         │   │
│  │  8. Return Response                                                 │   │
│  └────────────────────────────┬────────────────────────────────────────┘   │
│                               │                                             │
│  ┌────────────────────────────▼────────────────────────────────────────┐   │
│  │                    GeminiAgent (gemini_agent.py)                     │   │
│  │                                                                      │   │
│  │  ┌────────────────────────────────────────────────────────────┐    │   │
│  │  │ Step 1: Intent Detection (_detect_intent)  🆕 ENHANCED     │    │   │
│  │  │                                                             │    │   │
│  │  │  Input: query, selected_text                               │    │   │
│  │  │  Output: "SELECTED" | "SUMMARY" | "QUIZ" | "QA"           │    │   │
│  │  │                                                             │    │   │
│  │  │  Priority Flow:                                            │    │   │
│  │  │  1. If selected_text exists → SELECTED                     │    │   │
│  │  │  2. If "summarize" keywords → SUMMARY                      │    │   │
│  │  │  3. If "quiz" keywords → QUIZ                              │    │   │
│  │  │  4. Default → QA                                           │    │   │
│  │  └─────────────────────────┬──────────────────────────────────┘    │   │
│  │                            │                                        │   │
│  │  ┌─────────────────────────▼─────────────────────────────────┐    │   │
│  │  │ Step 2: Context Formatting                                 │    │   │
│  │  │                                                             │    │   │
│  │  │  • Assemble chunks from Qdrant                             │    │   │
│  │  │  • Format user profile                                     │    │   │
│  │  │  • Format gamification status                              │    │   │
│  │  │  • Format conversation history                             │    │   │
│  │  │  • Escape special characters                               │    │   │
│  │  └─────────────────────────┬──────────────────────────────────┘    │   │
│  │                            │                                        │   │
│  │  ┌─────────────────────────▼─────────────────────────────────┐    │   │
│  │  │ Step 3: System Prompt Selection  🆕 ENHANCED               │    │   │
│  │  │                                                             │    │   │
│  │  │  Based on intent:                                          │    │   │
│  │  │  • SELECTED → SYSTEM_PROMPT_SELECTIVE                      │    │   │
│  │  │  • SUMMARY → SYSTEM_PROMPT_SUMMARY (enhanced)              │    │   │
│  │  │  • QUIZ → SYSTEM_PROMPT_QUIZ (enhanced)                    │    │   │
│  │  │  • QA → SYSTEM_PROMPT_RAG (enhanced)                       │    │   │
│  │  └─────────────────────────┬──────────────────────────────────┘    │   │
│  │                            │                                        │   │
│  │  ┌─────────────────────────▼─────────────────────────────────┐    │   │
│  │  │ Step 4: Gemini API Call                                    │    │   │
│  │  │                                                             │    │   │
│  │  │  • Send prompt to Gemini                                   │    │   │
│  │  │  • Receive generated response                              │    │   │
│  │  │  • Handle errors/rate limits                               │    │   │
│  │  └─────────────────────────┬──────────────────────────────────┘    │   │
│  │                            │                                        │   │
│  │  ┌─────────────────────────▼─────────────────────────────────┐    │   │
│  │  │ Step 5: Post-Processing  🆕 ENHANCED                       │    │   │
│  │  │                                                             │    │   │
│  │  │  • Add context-aware greetings (_add_greetings)            │    │   │
│  │  │  • Extract citations (_extract_citations)                  │    │   │
│  │  │  • Format response                                         │    │   │
│  │  └─────────────────────────┬──────────────────────────────────┘    │   │
│  │                            │                                        │   │
│  │                            ▼                                        │   │
│  │                    Return (answer, citations)                       │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
           │                      │                      │
           ▼                      ▼                      ▼
┌──────────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   Qdrant Cloud       │  │  Neon Postgres   │  │  Gemini API      │
│                      │  │                  │  │                  │
│ • Vector Search      │  │ • User Profiles  │  │ • LLM Generation │
│ • Chunk Storage      │  │ • Chat History   │  │ • Smart Prompts  │
│ • Filtering          │  │ • Gamification   │  │ • Citations      │
└──────────────────────┘  └──────────────────┘  └──────────────────┘
```

---

## Intent Detection Flow (Enhanced) 🧠

```
User Query
    │
    ▼
┌───────────────────────────────────────────────┐
│   Parse Query & Check Selected Text           │
└───────────────┬───────────────────────────────┘
                │
                ▼
        ┌───────────────┐
        │ selected_text │
        │   exists?     │
        └───┬───────┬───┘
            │       │
        YES │       │ NO
            │       │
            ▼       ▼
    ┌───────────┐  ┌────────────────────────────┐
    │ SELECTED  │  │ Check Query Keywords        │
    │   MODE    │  └────────┬───────────────────┘
    └───────────┘           │
                            ▼
                    ┌─────────────────┐
                    │ "summarize"     │
                    │ "gist"          │
                    │ "overview"?     │
                    └───┬─────────┬───┘
                        │         │
                    YES │         │ NO
                        │         │
                        ▼         ▼
                ┌───────────┐  ┌────────────────────────┐
                │ SUMMARY   │  │ Check Quiz Keywords     │
                │   MODE    │  └────────┬───────────────┘
                └───────────┘           │
                                        ▼
                                ┌─────────────────┐
                                │ "quiz"          │
                                │ "test me"       │
                                │ "questions"?    │
                                └───┬─────────┬───┘
                                    │         │
                                YES │         │ NO
                                    │         │
                                    ▼         ▼
                            ┌───────────┐  ┌───────────┐
                            │   QUIZ    │  │    QA     │
                            │   MODE    │  │   MODE    │
                            └───────────┘  └───────────┘
```

---

## System Prompt Selection Matrix 📝

| Intent | System Prompt | Key Features | Use Case |
|--------|---------------|--------------|----------|
| **SELECTED** | `SYSTEM_PROMPT_SELECTIVE` | • Strict context mode<br>• Only uses selected text<br>• No Qdrant retrieval | User highlights text and asks question |
| **SUMMARY** | `SYSTEM_PROMPT_SUMMARY` 🆕 | • Structured format<br>• Emojis (📖✨)<br>• Bullet points<br>• Key takeaways | "Summarize chapter 3" |
| **QUIZ** | `SYSTEM_PROMPT_QUIZ` 🆕 | • MCQ + Short answer<br>• Book-grounded<br>• Answer explanations<br>• Emojis (🎯📝) | "Create quiz for module 1" |
| **QA** | `SYSTEM_PROMPT_RAG` 🆕 | • Full RAG pipeline<br>• Citations<br>• Profile-aware<br>• Conversational | "What is Physical AI?" |

---

## Data Flow: Example Request 🔄

### Example: Summary Request

```
Step 1: User Input
┌────────────────────────────────────────────┐
│ Query: "Summarize module 1 chapter 1"      │
│ User ID: "user123"                         │
│ Session ID: "abc-xyz"                      │
└────────────────────────────────────────────┘
              │
              ▼
Step 2: Backend Processing
┌────────────────────────────────────────────┐
│ • Validate request                         │
│ • Embed query → [0.123, 0.456, ...]        │
└────────────────────────────────────────────┘
              │
              ▼
Step 3: Qdrant Search
┌────────────────────────────────────────────┐
│ • Query vector: [0.123, 0.456, ...]        │
│ • Filter: module="module-1"                │
│ • Top K: 10                                │
│ • Results: 10 chunks (scored)              │
└────────────────────────────────────────────┘
              │
              ▼
Step 4: User Context Fetch (Parallel)
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Chat History    │  │ User Profile    │  │ Points/Level    │
│ (last 5 msgs)   │  │ (preferences)   │  │ (gamification)  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
              │
              ▼
Step 5: Intent Detection
┌────────────────────────────────────────────┐
│ _detect_intent("Summarize module 1", None) │
│ → Keyword match: "summarize"               │
│ → Result: SUMMARY                          │
└────────────────────────────────────────────┘
              │
              ▼
Step 6: Context Assembly
┌────────────────────────────────────────────┐
│ CONTEXT:                                   │
│ [module-1:intro:chunk1]                    │
│ Physical AI combines robotics with AI...   │
│                                            │
│ [module-1:intro:chunk2]                    │
│ Humanoid robots mimic human form...        │
│ ...                                        │
└────────────────────────────────────────────┘
              │
              ▼
Step 7: Prompt Construction
┌────────────────────────────────────────────┐
│ SYSTEM_PROMPT_SUMMARY                      │
│ + CONTEXT (10 chunks)                      │
│ + USER QUERY                               │
│ → "Generate structured summary..."         │
└────────────────────────────────────────────┘
              │
              ▼
Step 8: Gemini API Call
┌────────────────────────────────────────────┐
│ model.generate_content(prompt)             │
│ → Raw response from Gemini                 │
└────────────────────────────────────────────┘
              │
              ▼
Step 9: Post-Processing
┌────────────────────────────────────────────┐
│ • Add greeting: "Hello! 📖"                │
│ • Extract citations: [module:chapter:id]   │
│ • Format response                          │
└────────────────────────────────────────────┘
              │
              ▼
Step 10: Save to Database
┌────────────────────────────────────────────┐
│ • Save to chat_messages table              │
│ • Update conversation history              │
│ • Award gamification points                │
└────────────────────────────────────────────┘
              │
              ▼
Step 11: Response
┌────────────────────────────────────────────┐
│ {                                          │
│   "answer": "Hello! 📖 Here's a summary...",│
│   "citations": [                           │
│     {"module": "module-1", ...}            │
│   ],                                       │
│   "session_id": "abc-xyz"                  │
│ }                                          │
└────────────────────────────────────────────┘
```

---

## Code Modification Map 🗺️

### File: `backend/app/gemini_agent.py`

```python
# ========================================
# SECTION 1: System Prompts (Lines 30-102)
# ========================================

# 🆕 ENHANCED
SYSTEM_PROMPT_RAG = """
You are a warm, human-like AI tutor...
[Enhanced with dynamic schema guidance]
"""

# 🆕 ENHANCED
SYSTEM_PROMPT_SUMMARY = """
You are a master educator 📖✨...
[Enhanced with structured format]
"""

# 🆕 ENHANCED
SYSTEM_PROMPT_QUIZ = """
You are a friendly examiner 🎯📝...
[Enhanced with question variety]
"""

# ✅ EXISTING (No changes)
SYSTEM_PROMPT_SELECTIVE = """
You are a warm tutor helping with selected text...
"""

# ========================================
# SECTION 2: Intent Detection (Lines 225-233)
# ========================================

# 🆕 ENHANCED
def _detect_intent(self, query: str, selected_text: Optional[str]) -> str:
    """
    Enhanced intent detection with priority ordering
    and comprehensive keyword matching.
    """
    q = query.lower()

    # Priority 1: Selected Text
    if selected_text and len(selected_text) > 10:
        return "SELECTED"

    # Priority 2: Summary
    summary_keywords = ["summarize", "summary", "gist", "brief",
                        "overview", "recap", "tldr"]
    if any(word in q for word in summary_keywords):
        return "SUMMARY"

    # Priority 3: Quiz
    quiz_keywords = ["quiz", "test me", "questions", "assessment",
                     "exam", "evaluate"]
    if any(word in q for word in quiz_keywords):
        return "QUIZ"

    # Default: QA
    return "QA"

# ========================================
# SECTION 3: Greeting Logic (Lines 235-239)
# ========================================

# 🆕 ENHANCED
def _add_greetings(self, text: str) -> str:
    """
    Add context-aware greetings based on response type.
    """
    first_line = text[:50].lower()

    # Skip if greeting already exists
    if any(word in first_line for word in ["hello", "hi ", "hey"]):
        return text

    # Context-aware greetings
    if "summary" in text[:100].lower():
        return f"Hello! 📖 Here's a summary for you:\n\n{text}"
    elif "quiz" in text[:100].lower() or "question" in text[:100].lower():
        return f"Hi there! 🎯 Let's test your knowledge:\n\n{text}"
    elif "couldn't find" in text.lower():
        return f"Hello! 😊 {text}"
    else:
        return f"Hello! 😊 {text}"
```

---

## Database Schema (Unchanged) ✅

### Tables Used
```sql
-- User profiles
CREATE TABLE user_backgrounds (
    user_id TEXT PRIMARY KEY,
    software_role TEXT,
    software_level TEXT,
    hardware_type TEXT,
    gpu_available BOOLEAN,
    preferred_language TEXT DEFAULT 'en'
);

-- Gamification
CREATE TABLE gamification_status (
    user_id TEXT PRIMARY KEY,
    points_total INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Chat history (ChatKit format)
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY,
    thread_id UUID,
    user_id TEXT,
    role TEXT,
    content TEXT,
    created_at TIMESTAMP
);

-- Legacy conversation tracking
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    session_id TEXT,
    user_id TEXT,
    query TEXT,
    response TEXT,
    citations JSONB,
    created_at TIMESTAMP
);
```

**No schema changes required!** ✅

---

## API Contract (Unchanged) ✅

### Request Schema
```typescript
interface ChatRequest {
    query: string;              // User's question
    selected_text?: string;     // For selective mode
    module_id?: string;         // Filter by module
    chapter_id?: string;        // Filter by chapter
    book_id?: string;           // Future: multi-book
    session_id?: string;        // Session tracking
    user_id?: string;           // User identification
    agent_id?: number;          // Custom subagent
    top_k: number;              // Default: 5
}
```

### Response Schema
```typescript
interface ChatResponse {
    answer: string;             // Generated answer
    citations: Citation[];      // Source references
    session_id: string;         // Session ID
}

interface Citation {
    module: string;
    chapter: string;
    chunk_id: string;
    source_url: string;
    score?: number;
}
```

**No changes needed!** ✅

---

## Performance Considerations ⚡

### Current Performance
- Average response time: 2-3 seconds
- Qdrant search: ~200ms
- Embedding generation: ~100ms
- Gemini API call: 1-2 seconds
- Database operations: ~50ms

### Expected Impact (Minimal)
- Intent detection: +10ms (keyword matching)
- Enhanced prompts: No change (same Gemini call)
- Greeting addition: +5ms (string operation)

**Total overhead: ~15ms (negligible)** ✅

---

## Security Considerations 🔒

### Existing Security (Maintained)
- ✅ API keys in environment variables
- ✅ Rate limiting (60 req/min default)
- ✅ Input validation via Pydantic
- ✅ CORS protection
- ✅ SQL injection prevention (parameterized queries)

### No New Security Concerns
- Intent detection: Pure keyword matching (safe)
- System prompts: Static strings (safe)
- Greetings: String concatenation (safe)

**Security posture unchanged** ✅

---

## Monitoring & Observability 📊

### Logging Enhancements
```python
# Add to gemini_agent.py

logger.info(f"Intent detected: {intent} for query: {query[:50]}...")
logger.info(f"Using prompt: {prompt_type}")
logger.info(f"Generated answer with {len(citations)} citations")

# Error tracking
logger.error(f"Intent detection failed: {e}")
logger.warning(f"Empty chunks for query: {query}")
```

### Metrics to Track
- Intent distribution (QA vs SUMMARY vs QUIZ vs SELECTED)
- Response times by intent
- Citation counts by intent
- Error rates by intent
- User satisfaction by intent

---

## Testing Strategy 🧪

### Unit Tests
```python
# tests/test_intent_detection.py
def test_summary_intent():
    agent = GeminiAgent()
    assert agent._detect_intent("summarize chapter 1", None) == "SUMMARY"

def test_quiz_intent():
    agent = GeminiAgent()
    assert agent._detect_intent("create quiz", None) == "QUIZ"

def test_selected_intent():
    agent = GeminiAgent()
    assert agent._detect_intent("explain", "some text") == "SELECTED"
```

### Integration Tests
```python
# tests/test_chat_modes.py
@pytest.mark.asyncio
async def test_summary_endpoint():
    response = await client.post("/api/chat", json={
        "query": "summarize module 1",
        "top_k": 10
    })
    assert response.status_code == 200
    assert "📖" in response.json()["answer"]
```

---

## Rollback Plan 🔄

### Quick Rollback
```bash
# If issues occur
git revert <commit-hash>
git push origin main

# Redeploy
gcloud run deploy rag-backend --source .
```

### What Gets Rolled Back
- ✅ Code changes in gemini_agent.py
- ✅ System prompts revert to original
- ✅ Intent detection reverts to basic

### What Stays (No Impact)
- ✅ Database (no schema changes)
- ✅ Qdrant (no changes)
- ✅ Configuration (no changes)

---

## Conclusion 🎉

This upgrade is **low-risk, high-value** with:
- ✅ Minimal code changes (~150 lines)
- ✅ No breaking changes
- ✅ No database migrations
- ✅ No API contract changes
- ✅ Easy rollback path
- ✅ Significant UX improvement

**Ready to implement!** 🚀
