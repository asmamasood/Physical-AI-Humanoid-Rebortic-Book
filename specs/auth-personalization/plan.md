# Plan: Auth & Personalization Architecture

## 1. Scope and Dependencies
- **In Scope:**
  - Full-stack Authentication (Frontend & Backend).
  - User Profile Collection (Software/Hardware skills).
  - AI-driven Content Personalization.
  - Global Route Protection.
- **Out of Scope:**
  - Third-party OAuth providers (Email/Password only for now).
  - Payment processing.
- **Dependencies:**
  - **Better Auth:** Authentication framework.
  - **Neon Postgres:** Database persistence.
  - **Google Gemini:** LLM for text rewriting.
  - **Docusaurus:** Frontend framework.

## 2. Key Decisions and Rationale
- **Auth Provider:** Selected **Better Auth** (Self-hosted) over NextAuth/Clerk.
  - *Rationale:* Maximum control, no vendor lock-in, easy integration with Node.js backend.
- **Profile Storage:** Separate `user_background` table in Postgres (FastAPI managed).
  - *Rationale:* Decouples auth identity (Better Auth) from application specific business data (Profile). Allows easier schema evolution for AI personalization context.
- **Personalization Trigger:** **On-Demand (Button Click)** vs Automatic.
  - *Rationale:* "Personalize This Chapter" button gives users control and saves token costs (only personalizing what users actually read).

## 3. Interfaces and API Contracts
- **Auth Service (Port 3001)**
  - `POST /api/auth/sign-up/email`: Register user.
  - `POST /api/auth/sign-in/email`: Login user.
  - `GET /api/auth/session`: Validate session.
- **Backend Service (Port 8000)**
  - `POST /api/profile`: Create/Update user background.
    - Input: `{ user_id, software_role, software_level, hardware_type, gpu_available }`
  - `GET /api/profile/{user_id}`: Retrieve profile.
  - `POST /api/personalize`: Rewrite content.
    - Input: `{ content, user_id }`
    - Output: `{ personalized_content }`

## 4. Phase Breakdown

### Phase 1: Authentication Setup ✅
- **Objective:** Secure the application.
- **Implementation:**
  - Deployed Node.js Auth Service.
  - Implemented Client-side Auth Guard (`src/theme/Root.tsx`) to intercept all navigation.
  - Configured `docusaurus.config.ts` to expose Auth Links.

### Phase 2: User Background Collection ✅
- **Objective:** Gather context for AI.
- **Implementation:**
  - Enhanced `SignupPage` with a multi-step wizard.
  - Created persistent `user_background` schema in Postgres.
  - Wired Frontend to backend API to store data during registration.

### Phase 3: Personalization Logic ✅
- **Objective:** Adapt content to user.
- **Implementation:**
  - Developed RAG-lite pipeline using Gemini.
  - Backend fetches User Profile + Original Content -> Generates tailored version.
  - Prompt Engineering: "Rewrite for [Role] with [Hardware]...".

### Phase 4: Chapter-Level Personalization ✅
- **Objective:** Granular control.
- **Implementation:**
  - Created `<PersonalizeButton />` MDX component.
  - Placed at the top of chapter files.
  - Handles loading states and errors seamlessly.

### Phase 5: Validation & Testing ✅
- **Status:** Verified.
  - **Auth:** Redirects work. Session persists. "Sign It/Out" toggles correctly.
  - **Data:** Profile data confirmed in DB (`check_db.py`).
  - **AI:** Button generates personalized text successfully.

## 5. Risk Analysis
- **Risk:** Token Costs (Gemini).
  - *Mitigation:* On-demand button limits usage. Future: Add caching/rate-limiting.
- **Risk:** "Flash of Unauthenticated Content".
  - *Mitigation:* Implemented Loading State in `Root.tsx` to block rendering while session is pending.

## 6. Evaluation
- **Definition of Done:** 
  - User can Signup -> Login -> See Book -> Personalize Chapter.
  - Unauthenticated user sees Login.
  - All data persists in Neon DB.
