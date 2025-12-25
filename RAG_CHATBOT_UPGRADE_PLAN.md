# RAG Chatbot Upgrade Plan 📘

## Executive Summary

This document outlines the **UPGRADE STRATEGY** for the existing RAG chatbot system. We will **NOT rebuild** the system, but extend it modularly with new capabilities while preserving all existing functionality.

---

## Current System Architecture ✅

### Existing Capabilities
- ✅ Basic chat with RAG retrieval from Qdrant
- ✅ System prompts with personalization
- ✅ Session handling via Neon Postgres
- ✅ ChatKit / OpenAI Agents integration
- ✅ Frontend chat UI (FloatingWidget)
- ✅ Selected text support (via `/selective-chat` endpoint)
- ✅ User profiles & gamification
- ✅ Chat history & thread management
- ✅ Translation support (Urdu)
- ✅ Subagent personas

### Tech Stack
- **Backend**: FastAPI (Python 3.11+)
- **Vector DB**: Qdrant Cloud
- **Embeddings**: Local (sentence-transformers) or Cohere
- **LLM**: Google Gemini (Flash)
- **Database**: Neon Serverless Postgres
- **Frontend**: Docusaurus + React

### Key Files
- `backend/app/routers/chat.py` - Chat endpoints
- `backend/app/gemini_agent.py` - LLM agent with prompts
- `backend/app/models.py` - Pydantic schemas
- `backend/app/qdrant_client.py` - Vector search
- `backend/app/config.py` - Configuration

---

## Upgrade Constitution 🎯

### Core Principles
1. **Preserve Existing Behavior**: All current endpoints and features continue to work
2. **Add Without Breaking**: Extend functionality modularly
3. **Grounding in Context**: Never hallucinate book content
4. **Friendly & Engaging**: Use greetings and appropriate emojis 😊📘
5. **Security First**: All secrets in environment variables

---

## New Capabilities to Add 🚀

### 1️⃣ **Selected Text Mode (STRICT)** ✅
**Status**: Already implemented via `/selective-chat` endpoint
- When `selected_text` is provided, answer ONLY from that text
- If answer not found, return clear message
- No Qdrant retrieval used

**Extension Point**: Already working in `gemini_agent.py:257-278`

---

### 2️⃣ **Enhanced Full Book Question Answering**
**Status**: Needs enhancement

**Current**: Basic RAG with module/chapter filtering
**Upgrade**: Improve intent detection and context assembly

**Changes Required**:
```python
# In gemini_agent.py
# Enhance _detect_intent() method to better understand:
# - Cross-module questions
# - Conceptual queries
# - Definition requests
```

**Extension Point**: `gemini_agent.py:225-233` (_detect_intent method)

---

### 3️⃣ **Chapter / Module Summary Generation** 🆕
**Status**: Partially implemented, needs refinement

**Current**: Basic SUMMARY intent detection exists
**Upgrade**: Improve summary quality and structure

**Changes Required**:
1. Enhance `SYSTEM_PROMPT_SUMMARY` in `gemini_agent.py:77-88`
2. Add better context aggregation for summaries
3. Ensure emojis and structured format

**Implementation Strategy**:
```python
# Detect summary requests in _detect_intent():
if any(word in q for word in ["summarize", "summary", "gist", "brief", "overview"]):
    return "SUMMARY"

# Use enhanced summary prompt:
SYSTEM_PROMPT_SUMMARY = """You are a master educator 📖✨.

Generate a comprehensive, structured summary of the provided book content.

RULES:
1. Ground your summary STRICTLY in the provided CONTEXT
2. Use this structure:
   - 🎯 Key Topics (bullet points)
   - 📚 Core Concepts (numbered list)
   - 💡 Important Takeaways (highlights)
3. Maintain a friendly, encouraging tone
4. Use emojis to make engaging
5. If content is insufficient, state clearly

CONTEXT:
{context}

USER REQUEST: {query}

(Provide a warm, structured summary):"""
```

**Extension Point**: `gemini_agent.py:77-88, 183-202`

---

### 4️⃣ **Quiz Generation** 🆕
**Status**: Partially implemented, needs refinement

**Current**: Basic QUIZ intent detection exists
**Upgrade**: Improve quiz quality, variety, and feedback

**Changes Required**:
1. Enhance `SYSTEM_PROMPT_QUIZ` in `gemini_agent.py:90-102`
2. Add quiz formatting guidelines
3. Include answer explanations

**Implementation Strategy**:
```python
# Detect quiz requests in _detect_intent():
if any(word in q for word in ["quiz", "test me", "questions", "assessment", "exam"]):
    return "QUIZ"

# Use enhanced quiz prompt:
SYSTEM_PROMPT_QUIZ = """You are a friendly examiner 🎯📝.

Generate a moderate-difficulty quiz based STRICTLY on the provided book content.

QUIZ FORMAT:
Generate 3-5 questions in this format:

**Question 1** (Multiple Choice)
[Question text]
A) Option 1
B) Option 2
C) Option 3
D) Option 4

**Answer**: [Correct answer with brief explanation]

RULES:
1. Create variety: Mix multiple-choice and short-answer
2. Use ONLY the provided context - no external knowledge
3. Moderate difficulty (not too easy, not expert-level)
4. Include brief explanations for answers
5. Be encouraging: "Let's test your understanding! 🎯"
6. If insufficient content, state politely

CONTEXT:
{context}

USER REQUEST: {query}

(Generate an engaging, educational quiz):"""
```

**Extension Point**: `gemini_agent.py:90-102, 187-192`

---

### 5️⃣ **Conversational Behavior Enhancement** 🆕
**Status**: Partially implemented, needs consistency

**Current**: Some greetings added via `_add_greetings()` method
**Upgrade**: Make conversational tone more consistent and natural

**Changes Required**:
```python
# In gemini_agent.py:235-239
def _add_greetings(self, text: str) -> str:
    """Add contextual greetings based on response type."""
    # Check if greeting already exists
    first_line = text[:50].lower()

    if any(word in first_line for word in ["hello", "hi ", "hey", "greetings"]):
        return text

    # Detect response type and add appropriate greeting
    if "summary" in text[:100].lower():
        return f"Hello! 😊 Here's a summary for you:\n\n{text}"
    elif "quiz" in text[:100].lower() or "question" in text[:100].lower():
        return f"Hi there! 🎯 Let's test your knowledge:\n\n{text}"
    elif "I couldn't find" in text or "not found" in text.lower():
        return f"Hello! 😊 {text}"
    else:
        return f"Hello! 😊 {text}"
```

**Extension Point**: `gemini_agent.py:235-239`

---

## Intent Detection Logic 🧠

### Enhanced Detection Strategy

Update `_detect_intent()` method in `gemini_agent.py:225-233`:

```python
def _detect_intent(self, query: str, selected_text: Optional[str]) -> str:
    """
    Detect user intent from query and context.

    Returns: "SELECTED" | "SUMMARY" | "QUIZ" | "QA"
    """
    q = query.lower()

    # Priority 1: Selected Text Mode (if text provided)
    if selected_text and len(selected_text) > 10:
        return "SELECTED"

    # Priority 2: Summary Request
    summary_keywords = [
        "summarize", "summary", "gist", "brief",
        "overview", "recap", "in short", "tldr"
    ]
    if any(word in q for word in summary_keywords):
        return "SUMMARY"

    # Priority 3: Quiz/Test Request
    quiz_keywords = [
        "quiz", "test me", "questions", "assessment",
        "exam", "evaluate", "check my knowledge"
    ]
    if any(word in q for word in quiz_keywords):
        return "QUIZ"

    # Priority 4: Explanation/Definition Request (QA with emphasis)
    explain_keywords = [
        "explain", "define", "what is", "what are",
        "how does", "why does", "describe"
    ]
    if any(word in q for word in explain_keywords):
        return "QA"  # Standard QA mode with explanation focus

    # Default: Standard QA Mode
    return "QA"
```

**Extension Point**: `gemini_agent.py:225-233`

---

## API Extensions 🔌

### Current Endpoints
- ✅ `POST /chat` - RAG-based chat
- ✅ `POST /selective-chat` - Selected text only

### No New Endpoints Required!
All new capabilities (summary, quiz) will be handled through **intent detection** in the existing `/chat` endpoint.

### Request Schema (Already Supports Extensions)
```python
class ChatRequest(BaseModel):
    query: str                          # User's question
    selected_text: Optional[str]        # For selective mode
    module_id: Optional[str]            # Filter by module
    chapter_id: Optional[str]           # Filter by chapter
    book_id: Optional[str]              # Future: multi-book support
    session_id: Optional[str]           # Session tracking
    user_id: Optional[str]              # User identification
    agent_id: Optional[int]             # Custom subagent
    top_k: int = 5                      # Number of chunks
```

**No changes needed** - existing schema already supports all requirements!

---

## System Prompts Update 📝

### Updated Main RAG Prompt

```python
SYSTEM_PROMPT_RAG = """You are a warm, human-like AI tutor for the "Physical AI & Humanoid Robotics" book.

{agent_persona}

CORE PHILOSOPHY:
- **Soft-Coded Intent**: Deeply understand the user's query intent. Adapt your response style:
  - Story request → Narrative summary
  - Technical question → Detailed scientific explanation
  - Simple definition → Clear, concise teaching
  - Conversational → Friendly, encouraging tone
- **Human Tone**: Speak like a person, not a machine. Use natural phrases:
  - "I found this interesting part..."
  - "Let me help you understand..."
  - "The book explains this really well..."
- **Context Strictness**: You ONLY know what's in the CONTEXT CHUNKS below
  - Never invent facts
  - Never use outside knowledge
  - If information is missing, say so clearly

{profile}
{gamification}

RULES:
1. **Dynamic Response Schema**: Analyze query intent and respond accordingly:
   - Summary → Structured overview with emojis 📖
   - Quiz → Interactive questions with answers 🎯
   - Explanation → Detailed breakdown with examples
   - Chat → Natural conversation with encouragement
2. **Language Adaptation**:
   - Detect user language preference
   - If user asks in Urdu or profile indicates Urdu → respond in Urdu
   - Otherwise → respond in English
3. **Gamification Awareness**:
   - If points/level provided, acknowledge naturally
   - Example: "Great progress at Level 5! 🎉"
   - Don't be robotic - keep it subtle and encouraging
4. **Citations**:
   - Always cite sources: [module:chapter:chunk_id]
   - Make citations natural part of text flow
5. **Uncertainty Handling**:
   - If content doesn't cover topic: "I couldn't find that specific detail in the book."
   - Suggest alternative questions or related topics

CONVERSATION HISTORY:
{history}

CONTEXT CHUNKS (Book Content):
{context}

USER QUERY: {query}

(Respond warmly and naturally, adapting to the user's intent):"""
```

---

## Implementation Roadmap 🗺️

### Phase 1: Enhance Existing Features ✅
**Status**: Mostly complete

1. ✅ Selected text mode (already working)
2. ✅ Basic intent detection (exists, needs refinement)
3. ✅ Profile & gamification integration (working)

### Phase 2: Refine Intent Detection 🔄
**Target Files**: `backend/app/gemini_agent.py`

**Tasks**:
1. Update `_detect_intent()` method (lines 225-233)
2. Add more keyword patterns
3. Test with various query types

**Estimated Changes**: ~30 lines

### Phase 3: Enhance System Prompts 📝
**Target Files**: `backend/app/gemini_agent.py`

**Tasks**:
1. Update `SYSTEM_PROMPT_RAG` (lines 30-57)
2. Update `SYSTEM_PROMPT_SUMMARY` (lines 77-88)
3. Update `SYSTEM_PROMPT_QUIZ` (lines 90-102)

**Estimated Changes**: ~100 lines

### Phase 4: Improve Greeting Logic 😊
**Target Files**: `backend/app/gemini_agent.py`

**Tasks**:
1. Update `_add_greetings()` method (lines 235-239)
2. Add context-aware greeting selection
3. Test with different response types

**Estimated Changes**: ~20 lines

### Phase 5: Testing & Validation ✅
**Test Cases**:
1. ✅ Selected text mode
2. ✅ Summary generation (module, chapter)
3. ✅ Quiz generation
4. ✅ Standard QA
5. ✅ Greeting consistency
6. ✅ Urdu translation
7. ✅ Profile personalization
8. ✅ Gamification awareness

---

## Backward Compatibility ✅

### Guaranteed Compatibility
- ✅ All existing API endpoints work unchanged
- ✅ Request/response schemas unchanged
- ✅ Frontend integration unchanged
- ✅ Database schemas unchanged
- ✅ Configuration unchanged

### No Breaking Changes
- Intent detection is **additive** (default to "QA" mode)
- System prompts enhanced but maintain same structure
- All new features are **opt-in** via user queries

---

## Testing Strategy 🧪

### Unit Tests
```python
# test_intent_detection.py
def test_detect_intent_summary():
    agent = GeminiAgent()
    assert agent._detect_intent("summarize chapter 1", None) == "SUMMARY"
    assert agent._detect_intent("give me a brief overview", None) == "SUMMARY"

def test_detect_intent_quiz():
    agent = GeminiAgent()
    assert agent._detect_intent("create a quiz for module 2", None) == "QUIZ"
    assert agent._detect_intent("test my knowledge", None) == "QUIZ"

def test_detect_intent_selected():
    agent = GeminiAgent()
    assert agent._detect_intent("what does this mean?", "sample text") == "SELECTED"
```

### Integration Tests
```python
# test_chat_modes.py
async def test_summary_mode():
    response = await client.post("/api/chat", json={
        "query": "summarize module 1",
        "top_k": 10
    })
    assert response.status_code == 200
    assert "📖" in response.json()["answer"]

async def test_quiz_mode():
    response = await client.post("/api/chat", json={
        "query": "generate quiz for chapter 2",
        "chapter_id": "chapter-2",
        "top_k": 10
    })
    assert response.status_code == 200
    assert "Question" in response.json()["answer"]
```

### Manual Test Cases
1. **Summary Test**: "Summarize module 1 chapter 1"
2. **Quiz Test**: "Create a quiz for robotics basics"
3. **Selected Text Test**: Highlight text, ask "explain this"
4. **Standard QA Test**: "What is Physical AI?"
5. **Greeting Test**: Check all responses start friendly
6. **Urdu Test**: "اردو میں جواب دیں - کیا ہے Physical AI؟"

---

## Configuration Updates 🔧

### Environment Variables (No Changes Required)
All necessary configuration already exists:
- ✅ `GEMINI_API_KEY` - LLM access
- ✅ `QDRANT_URL` & `QDRANT_API_KEY` - Vector DB
- ✅ `NEON_DB_URL` - Session storage
- ✅ `EMBEDDING_PROVIDER` - Local or Cohere

### Optional New Variables (Future)
```bash
# Future enhancements
MAX_QUIZ_QUESTIONS=5
SUMMARY_MAX_LENGTH=500
GREETING_STYLE=friendly  # options: friendly, professional, casual
```

---

## Deployment Checklist ✅

### Pre-Deployment
- [ ] Review all code changes
- [ ] Run unit tests
- [ ] Run integration tests
- [ ] Test with real book content
- [ ] Verify backward compatibility
- [ ] Check logging and error handling

### Deployment
- [ ] Update environment variables (if needed)
- [ ] Deploy backend to Cloud Run (or target platform)
- [ ] Verify health endpoint: `/health`
- [ ] Test all endpoints: `/chat`, `/selective-chat`
- [ ] Monitor logs for errors

### Post-Deployment
- [ ] Run smoke tests
- [ ] Verify intent detection working
- [ ] Check summary generation
- [ ] Check quiz generation
- [ ] Verify greetings appear
- [ ] Test with frontend UI

---

## Rollback Plan 🔄

### If Issues Occur
1. **Code Rollback**: Git revert to previous commit
2. **Database**: No schema changes, no rollback needed
3. **Configuration**: Revert environment variables
4. **Vector DB**: No changes to Qdrant, no action needed

### Rollback Command
```bash
# If using git tags
git revert <commit-hash>
git push origin main

# Redeploy
gcloud run deploy rag-backend --source .
```

---

## Success Metrics 📊

### Key Performance Indicators
1. **Intent Detection Accuracy**: >95% correct classification
2. **Summary Quality**: User satisfaction score >4/5
3. **Quiz Relevance**: Questions grounded in book content (100%)
4. **Response Time**: <3 seconds for standard queries
5. **Error Rate**: <1% API failures
6. **User Engagement**: Increased chat interactions

### Monitoring
- Track intent distribution (QA vs Summary vs Quiz)
- Monitor Gemini API usage and costs
- Log failed intent detections
- Collect user feedback via ratings

---

## Future Enhancements 🚀

### Post-Upgrade Features (Not in Current Scope)
1. **Multi-Book Support**: Handle multiple textbooks
2. **Advanced Filtering**: By difficulty level, topics, prerequisites
3. **Adaptive Learning**: Personalized content recommendations
4. **Voice Input**: Speech-to-text for queries
5. **Visual Diagrams**: Generate explanatory diagrams
6. **Progress Tracking**: Chapter completion tracking
7. **Collaborative Learning**: Share quizzes with peers

---

## Support & Maintenance 🛠️

### Documentation
- [ ] Update README.md with new features
- [ ] Add example queries to API docs
- [ ] Document intent detection keywords
- [ ] Create user guide for summary/quiz features

### Monitoring & Logs
```python
# Enhanced logging in gemini_agent.py
logger.info(f"Detected intent: {intent} for query: {query[:50]}...")
logger.info(f"Generated {len(citations)} citations")
logger.warning(f"Empty chunks returned for query: {query}")
```

---

## Conclusion 🎉

This upgrade plan extends the RAG chatbot with powerful new capabilities while maintaining **100% backward compatibility**. The modular design ensures:

✅ **No Breaking Changes**
✅ **Enhanced User Experience**
✅ **Maintained Code Quality**
✅ **Production-Ready**

All changes are localized to `gemini_agent.py` with minimal modifications (~150 lines total). The upgrade is **low-risk, high-value**, and fully aligned with the project's constitution.

---

**Ready to Implement!** 🚀

Next Steps:
1. Review this plan with stakeholders
2. Create feature branch: `feature/chatbot-upgrade`
3. Implement changes in phases
4. Test thoroughly
5. Deploy to staging
6. Deploy to production

**Estimated Timeline**: 2-3 development sessions
**Risk Level**: Low (no breaking changes)
**Impact**: High (significantly improved user experience)
