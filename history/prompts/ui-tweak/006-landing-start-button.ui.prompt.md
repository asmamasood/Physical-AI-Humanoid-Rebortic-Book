---
id: 006
title: Update Start Button Redirect
stage: ui-tweak
date: 2025-12-24
surface: agent
model: gemini-2.0-flash-exp
feature: landing-page
branch: main
user: user
command: none
labels: [ux, frontend, landing-page]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - d:/digital-book/physical-ai-robotics-book/src/pages/index.tsx
tests:
  - manual verification of button link
---

## Prompt

(Context: User reported "when user click on start btton signin ui show")

## Response snapshot

User requested that the "Start Button" on the landing page lead to the Sign In UI.
Updated `src/pages/index.tsx`:
- Changed button label from "Sign In to Read" to "Get Started".
- Confirmed logic `to={session ? "/docs/intro" : "/login"}` ensures unauthenticated users are directed to `/login`.

## Outcome

- ✅ Impact: Clearer CTA ("Get Started") that behaves as requested.
- 🧪 Tests: n/a (simple prop change).
- 📁 Files: `index.tsx`.
- 🔁 Next prompts: none
