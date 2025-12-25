---
id: 003-implement-auth-plan
title: Implement Auth and Personalization Plan
stage: plan
date: 2025-12-20
surface: agent
model: gemini-2.0-flash-exp
feature: auth-personalization
branch: main
user: user
command: /sp.plan
labels: [plan, auth, personalization, better-auth, architecture]
links:
  spec: d:/digital-book/specs/auth-personalization/spec.md
  tasks: d:/digital-book/specs/auth-personalization/tasks.md
files_yaml:
 - d:/digital-book/specs/auth-personalization/plan.md
tests_yaml: []
prompt_text: |
  /sp.plan

  Phase 1 — Authentication Setup
  - Integrate Better Auth for Signup & Signin.
  - Protect access to book chapters and chatbot.
  - Use client-side JS to check session; redirect unauthenticated users.

  Phase 2 — User Background Collection
  - During Signup, collect software (skill level, tools) and hardware (device type, system) info.
  - Store data in Better Auth metadata or a small backend (FastAPI/Supabase).

  Phase 3 — Personalization Logic
  - Fetch user background on chapter load.
  - Adjust chapter content dynamically based on skill/hardware.
  - Apply same logic to chatbot responses if available.

  Phase 4 — Chapter-Level Personalization (Bonus)
  - Add “Personalize This Chapter” button at chapter start (MDX React component).
  - On click, re-fetch user profile and adjust content dynamically.
  - Support modes: Beginner / Practical / Advanced.

  Phase 5 — Validation & Testing
  - Test auth flow, data collection, and personalization.
  - Ensure only authenticated users see chapters.
  - Verify button correctly updates content per user profile.
response_text: |
  Created architectural plan documenting the 5-phase approach for Auth & Personalization.
  The plan details the implementation of Better Auth, User Background schema, Personalization Engine, and Client-side Auth Guards.
  Since the implementation is complete, the items reflect the existing working system.
---
