---
id: 001-specify-auth
title: Specify Authentication and Personalization
stage: spec
date: 2025-12-20
surface: agent
model: gemini-2.0-flash-exp
feature: auth-personalization
branch: main
user: user
command: /sp.specify
labels: [auth, personalization, better-auth, schema]
links: null
files_yaml:
 - d:/digital-book/specs/auth-personalization/spec.md
tests_yaml: []
prompt_text: |
  /sp.specify

  Specify authentication and personalization for an interactive book.

  1. Use Better Auth for Signup and Signin.
  2. Only authenticated users can access chapters and chatbot.
  3. During Signup, collect:
     - Software background (skill level, tools)
     - Hardware background (device type, system level)
  4. Store background data with user profile.
  5. Personalize chapter content based on user background.
  6. Add a “Personalize This Chapter” button at the start of each chapter to dynamically adjust content (Beginner / Practical / Advanced).

  Deliver:
  - Auth flow
  - User schema
  - Personalization logic
  - Frontend + backend integration outline
response_text: |
  Created specification document defining the Better Auth integration, User Background schema, and Personalization flow.
  The system uses a dedicated Auth Service (Node.js) for identity and a Python Backend for personalization logic (RAG/LLM), with Docusaurus enforcing global access control.
---
