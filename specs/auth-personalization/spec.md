# Specification: Auth & Personalization

## 1. Goal Description
Implement a secure, personalized interactive book experience where:
- Access to content (book chapters) and AI tools (chatbot) is restricted to authenticated users.
- Content is dynamically adapted to the user's technical background (Software/Hardware skills).
- Authentication is handled by **Better Auth** (self-hosted).

## 2. Authentication Flow

### Architecture
- **Auth Service**: Node.js/Express server (Port 3001) running `better-auth`.
- **Database**: Neon Postgres (Shared connection).
- **Frontend**: Docusaurus (Port 3000) using `better-auth/react` client.
- **Backend**: FastAPI (Port 8000) for personalization and history.

### Access Control
- **Global Guard**: Implemented in `src/theme/Root.tsx`.
- **Public Routes**: `/` (Landing), `/login`, `/signup`, `/blog`.
- **Protected Routes**: `/docs/*` (Book Content), `/chat` (if exists), Widget.
- **Behavior**: Unauthenticated access to protected routes redirects to `/login`.

## 3. Data Schema

### Core Identity (Better Auth Standard)
Stored in Postgres tables managed by Better Auth:
- `user`: id, email, name, image, emailVerified, createdAt, updatedAt.
- `session`: id, userId, token, expiresAt, ipAddress, userAgent.
- `account`: id, userId, accountId, providerId, etc. (for OAuth).
- `verification`: id, identifier, value, expiresAt (for email verification).

### User Profile (Custom)
Table: `user_background`
| Column | Type | Description |
|--------|------|-------------|
| `user_id` | TEXT (PK) | Foreign Key to `user.id`. |
| `software_role` | TEXT | e.g. "Frontend", "Backend", "Fullstack". |
| `software_level` | TEXT | "Beginner", "Intermediate", "Advanced". |
| `hardware_type` | TEXT | "Low-end PC", "High-end PC", "Mobile". |
| `gpu_available` | BOOLEAN | Whether user has local GPU access. |
| `updated_at` | TIMESTAMP | Last update time. |

## 4. Personalization Logic

### Trigger
- **UI**: "Personalize This Chapter" button (`<PersonalizeButton />`) injected into MDX chapters.
- **Action**: User clicks button -> sends `chapter_content` + `user_id` to Backend.

### Processing (Backend)
1. **Endpoint**: `POST /api/personalize`
2. **Context Retrieval**: Fetch user profile from `user_background` using `user_id`.
3. **Prompt Engineering**:
   - Construct prompt: "Rewrite this text for a [Level] [Role] user with [Hardware]..."
   - Append original text.
4. **LLM Call**: Send to Gemini Flash.
5. **Response**: Return adapted Markdown.

### Caching
- **Key**: `user_id` + `chapter_id` (or content hash).
- **TTL**: 1 hour (in-memory or Redis).
- Prevents re-generating content for the same user repeatedly.

## 5. Integration Outline

### Frontend (Docusaurus)
- **`auth-client.ts`**: Configured `createAuthClient` pointing to `http://localhost:3001/api/auth`.
- **`signup.tsx`**: Multi-step form.
  - Step 1: `authClient.signUp.email` (Create Identity).
  - Step 2: `fetch('http://localhost:8000/api/profile')` (Save Background).
- **`login.tsx`**: `authClient.signIn.email`. Redirects to `/docs/intro`.
- **`Root.tsx`**: Wraps app. Checks `useSession()`. Redirects if null.
- **`PersonalizeButton.tsx`**: Client component. Calls backend `personalize` API.

### Backend (Python/FastAPI)
- **`routers/profile.py`**: CRUD for `user_background` table.
- **`routers/personalize.py`**: Handles LLM adaptation logic.
- **`db_neon.py`**: Database connector using `asyncpg` (separate from Auth Service connection).

### Auth Service (Node.js)
- **`auth.js`**: Better Auth configuration.
- **`index.js`**: Express server mounting auth routes.
