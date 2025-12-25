---
id: 002
title: Implement Chatbot Visibility and Blog Updates
stage: implement
date: 2025-12-23
surface: agent
model: gemini-2.0-flash-exp
feature: ui-visibility-blog-update
branch: main
user: user
command: none
labels: [ui, visibility, blog, chatbot, implementation]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - d:/digital-book/frontend/plugin-rag/src/client-module.js
  - d:/digital-book/physical-ai-robotics-book/src/theme/Root.tsx
  - d:/digital-book/physical-ai-robotics-book/src/components/FloatingWidget/index.tsx
  - d:/digital-book/physical-ai-robotics-book/blog/authors.yml
  - d:/digital-book/physical-ai-robotics-book/blog/tags.yml
  - d:/digital-book/physical-ai-robotics-book/blog/2021-08-26-welcome/index.md
  - d:/digital-book/physical-ai-robotics-book/blog/2025-12-23-ros2-nodes/index.md
tests:
  - manual verification of routes
---

## Prompt

(Context: Continuation from Plan stage)
Proceed with implementation.

## Response snapshot

Implemented UI visibility restrictions for the RAG chatbot to ONLY appear on `/docs/` routes.
Updated `Root.tsx` to hide the conflicting `FloatingChat` on docs and blog pages.
Replaced mock blog content with book-relevant posts ("Bridging Digital and Physical Reality", "Nodes - The Nervous System of Robots").
Verified changes via manual route checking.

## Outcome

- ✅ Impact: Chatbot visibility is now correctly scoped to book content. Landing page is clean. Blog has relevant content and no overlapping widgets.
- 🧪 Tests: Confirmed visibility on landing (none), blog (none), and docs (chatbot present).
- 📁 Files: Modified frontend components and blog markdown files.
- 🔁 Next prompts: none
- 🧠 Reflection: The conflict between two different chatbot implementations (`plugin-rag` vs `FloatingChat`) was a key discovery that needed resolution.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): null
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): none
