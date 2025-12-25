---
id: 003
title: Fix Chatbot Visibility on SPA Navigation
stage: refactor
date: 2025-12-23
surface: agent
model: gemini-2.0-flash-exp
feature: ui-visibility-blog-update
branch: main
user: user
command: none
labels: [bugfix, spa, docusaurus, chatbot]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - d:/digital-book/frontend/plugin-rag/src/client-module.js
tests:
  - manual route navigation verification
---

## Prompt

(Context: User reported chatbot missing after sign-in)

## Response snapshot

Identified that `client-module.js` only ran visibility checks on initial page load, causing the chatbot to remain hidden when navigating to `/docs/` via client-side routing (redirects or links).
Implemented `onRouteUpdate` in `client-module.js` to re-evaluate visibility and mount/unmount the chatbot on every route change.
Verified that the chatbot now appears immediately when navigating to book pages.

## Outcome

- ✅ Impact: Chatbot visibility is now robust across SPA navigation and redirects.
- 🧪 Tests: Confirmed Home -> Docs navigation triggers mount.
- 📁 Files: `client-module.js`
- 🔁 Next prompts: none
- 🧠 Reflection: Docusaurus plugins require lifecycle hooks like `onRouteUpdate` to handle SPA behavior correctly.

## Evaluation notes (flywheel)

- Failure modes observed: Initial implementation missed SPA navigation case.
- Graders run and results (PASS/FAIL): null
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): none
