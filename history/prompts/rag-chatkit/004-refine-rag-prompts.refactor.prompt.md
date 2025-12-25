---
id: 569947dc-c3c9-4674-8b63-12822530c00d
title: Refine RAG Prompts for Summary and Definitions
stage: refactor
date: 2025-12-20
surface: agent
model: gemini-2.0-flash-exp
feature: rag-chatbot
branch: main
user: user
command: task_boundary
labels:
  - rag
  - prompt-engineering
  - summarization
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - d:\digital-book\backend\app\gemini_agent.py
tests_yaml:
  - verification via manual chat
prompt_text: |
  rag hatbot gives summary ,define any line when user ask and explain every thing which is found in book when user ask give ans the user question
response_text: |
  Refining the Gemini agent system prompts to explicitly handle requests for summaries, definitions, and detailed explanations based on the retrieved book content.
---
User is requesting better capabilities for the RAG chatbot to handling summaries, definitions, and detailed explanations of book content.
Plan:
1. Modify `backend/app/gemini_agent.py` to update the system prompt.
2. Ensure the prompt instructs the model to be a "helpful tutor" that can define terms and summarize sections using the provided context.
