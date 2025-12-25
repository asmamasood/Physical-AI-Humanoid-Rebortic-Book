# Tasks: Auth & Personalization

## Phase 1: Authentication Infrastructure
- [x] **Setup Auth Service** <!-- id: 1 -->
  - [x] Initialize Node.js/Express service on port 3001
  - [x] Configure Better Auth with Neon Postgres (pg driver)
  - [x] Define User, Session, Account, Verification tables
  - [x] Configure CORS for port 3000 (Frontend)
- [x] **Frontend Integration** <!-- id: 2 -->
  - [x] Install `better-auth/react` client
  - [x] Configure `src/lib/auth-client.ts`
  - [x] Create `LoginPage` (`src/pages/login.tsx`)
  - [x] Create Global Auth Guard (`src/theme/Root.tsx`)

## Phase 2: User Profile & Signup
- [x] **Backend Schema** <!-- id: 3 -->
  - [x] Create `user_background` table in Neon DB
  - [x] Create Pydantic models for User Background
  - [x] Implement GET/POST `/api/profile` endpoints
- [x] **Signup Flow** <!-- id: 4 -->
  - [x] Create `SignupPage` (`src/pages/signup.tsx`)
  - [x] Implement Multi-step form (Identity -> Background)
  - [x] Save Identity to Auth Service
  - [x] Save Background to Backend Service

## Phase 3: Content Personalization
- [x] **Personalization Engine** <!-- id: 5 -->
  - [x] Implement `/api/personalize` endpoint
  - [x] Integrate Gemini LLM for text rewriting
  - [x] Fetch user background context for prompts
- [x] **UI Integration** <!-- id: 6 -->
  - [x] Create `<PersonalizeButton />` component
  - [x] Inject button into MDX chapters
  - [x] Display personalized content on success

## Phase 4: Verification & Polish
- [x] **Access Control** <!-- id: 7 -->
  - [x] Verify `/docs/*` redirects to Login
  - [x] Verify `/chat` (widget) only appears for authenticated users
  - [x] Verify Landing Page (`/`) is public
- [x] **UI UX** <!-- id: 8 -->
  - [x] "First you sign in then reading book" message
  - [x] Navbar: Sign In/Sign Out toggles correctly
