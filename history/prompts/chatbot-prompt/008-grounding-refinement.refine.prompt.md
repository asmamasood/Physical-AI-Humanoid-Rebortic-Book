---
id: 008
title: Refine Chatbot Prompt for Book Grounding
stage: refinement
date: 2025-12-24
surface: agent
model: gemini-2.0-flash-exp
feature: chatbot-prompt
branch: main
user: user
command: none
labels: [prompt-engineering, backend, qa, gemini]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - d:/digital-book/backend/app/gemini_agent.py
  - d:/digital-book/backend/test_out_of_scope.py
tests:
  - backend/test_out_of_scope.py (Passed)
  - backend/test_features.py (Regression Passed)
---

## Prompt

(Context: User requested "add when user ask question chatbot give ans related to book in chatbot dont replace or delete any functionality")

## Response snapshot

User wanted strict "book-only" answers without breaking existing features (summary/quiz).
1.  **Modified `SYSTEM_PROMPT_RAG`**: Updated `gemini_agent.py` to include explicit "Context Strictness" rules (e.g., "You are a specialist on THIS BOOK ONLY").
2.  **Created `test_out_of_scope.py`**: Verified the chatbot refuses queries like "How do I bake a cake?".
3.  **Ran Regression**: Confirmed `test_features.py` (Summary/Quiz) still passes.

## Outcome

- ✅ Impact: Chatbot is now strictly grounded in the book content for QA, while preserving advanced features.
- 🧪 Tests: `test_out_of_scope.py` passes; `test_features.py` passes.
- 📁 Files: `gemini_agent.py`.
- 🔁 Next prompts: none
