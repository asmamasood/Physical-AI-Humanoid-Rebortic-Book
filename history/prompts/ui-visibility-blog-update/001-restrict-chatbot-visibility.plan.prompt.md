---
id: 001
title: Restrict Chatbot Visibility and Update Blog Content
stage: plan
date: 2025-12-23
surface: agent
model: gemini-2.0-flash-exp
feature: ui-visibility-blog-update
branch: main
user: user
command: none
labels: [ui, visibility, blog, chatbot]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - d:/digital-book/frontend/plugin-rag/src/client-module.js
  - d:/digital-book/physical-ai-robotics-book/src/theme/Root.tsx
  - d:/digital-book/physical-ai-robotics-book/blog/2021-08-26-welcome/index.md
tests:
  - manual verification
---

## Prompt

 You are a senior full‑stack engineer.

You are UPDATING an existing, fully functional chatbot system.
Do NOT modify core chatbot logic, RAG pipeline, or AI behavior.
Only apply UI, visibility, and content updates described below.

========================
UPDATE CONSTITUTION
========================
- Preserve all existing chatbot functionality
- Do NOT break chat, RAG, summary, quiz, or selected-text features
- Apply changes only where explicitly requested
- Keep code clean and modular
- Ensure backward compatibility

========================
UPDATE REMIT (WHAT TO CHANGE)
========================

1️⃣ Landing Page Update
- Do NOT show chatbot on the landing (home) page
- Remove or hide:
  - Chat widget
  - "Ask the chatbot" section
  - Any chatbot CTA on landing page
- Landing page should focus on:
  - Book introduction
  - Author info
  - Book highlights
  - Call-to-action like "Read the Book"

2️⃣ Chatbot Access Control
- Chatbot must remain fully functional
- Chatbot should be accessible ONLY from:
  - Book reading page
  - Dedicated "Read Book" or "Book Detail" page
- Ensure chatbot loads only when book context is available

3️⃣ Blog Page Content Update
- Remove mock / placeholder blog content
- Replace with book-related blogs such as:
  - Chapter insights
  - Module explanations
  - Key takeaways from the book
  - Author notes
- Blog content must be derived from book context
- No dummy or lorem ipsum content

4️⃣ Blog Page Behavior
- Blogs should:
  - Reference book chapters/modules
  - Be informative and reader-focused
  - Not expose chatbot or AI internals

========================
WHAT MUST NOT CHANGE
========================
- Chatbot RAG logic
- Selected Text Mode
- Full Book QA
- Summary generation
- Quiz generation
- Agent system prompts
- Backend APIs

========================
FRONTEND IMPLEMENTATION NOTES
========================
- Use conditional rendering to hide chatbot on landing page
- Ensure chatbot is mounted only on book-related routes
- Update blog page components to fetch real book-based content
- Maintain existing styling and theme

========================
DELIVERABLES
========================
1. Updated landing page UI (chatbot hidden)
2. Chatbot visible only on book pages
3. Updated blog page with book-related content
4. No regression in existing features
5. Clean, maintainable diff-based changes

========================
PROCESS (MANDATORY)
========================
1. Analyze current routing and UI structure
2. Identify chatbot mount points
3. Restrict chatbot visibility
4. Replace mock blog content
5. Test all pages:
   - Landing page
   - Blog page
   - Book reading page
   - Chatbot flows

Output changes in Markdown.
Do NOT rebuild the app.
Only UPDATE. 

## Response snapshot

I will restrict the chatbot visibility to book-related pages (under `/docs/`) by modifying the injection points in `client-module.js` and `Root.tsx`. I will also replace the mock blog content with real insights derived from the book modules in the `blog` directory. I am creating an implementation plan and will verify the changes across the landing, blog, and documentation pages.

## Outcome

- ✅ Impact: Planned UI visibility restrictions and blog content updates.
- 🧪 Tests: Manual verification planned.
- 📁 Files: Identified `client-module.js`, `Root.tsx`, and blog files.
- 🔁 Next prompts: none
- 🧠 Reflection: Two chatbot injection points were identified, both need to be restricted to ensure consistency.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): null
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): implement conditional rendering in `client-module.js`.
