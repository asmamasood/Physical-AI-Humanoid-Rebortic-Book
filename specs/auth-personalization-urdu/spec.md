# Spec: Authenticated, Personalized, and Urdu Translation Features

## Goal
Enhance the digital book with user authentication, dynamic content personalization based on user background, and a toggleable Urdu translation feature.

## Requirements
- **Authentication**:
  - Integrate "Better Auth" for Sign-in and Sign-up.
  - Global guard: Redirect unauthenticated users to `/login`.
  - Protect all `/docs/*` routes and the Chatbot.
- **User Background**:
  - Signup must capture:
    - Software Background (e.g., Python, C++, No coding).
    - Hardware Background (e.g., Arduino, Raspberry Pi, No hardware experience).
  - Store this data in the backend (Postgres).
- **Personalization**:
  - "Personalize This Chapter" button on every doc page.
  - Dynamically rewrite content based on user's background (Beginner, Practical, or Advanced lens).
  - Use Gemini AI to perform the rewrite.
- **Urdu Translation**:
  - "Translate to Urdu" button on every doc page.
  - Toggle between English (Original) and Urdu.
  - Use Gemini AI to perform the translation dynamically.
  - Store language preference in local storage or user profile.

## Architecture
- **Frontend**: Docusaurus + React.
- **Backend**: FastAPI + Better Auth + Neon Postgres.
- **AI**: Google Gemini (via `GeminiAgent`).

## Schema (Existing & New)
- `user_backgrounds`: (user_id, software_bg, hardware_bg, updated_at)
- `user_preferences`: (user_id, language, updated_at) - *NEW*

## API Endpoints
- `POST /api/personalize`: Rewrites content based on profile.
- `POST /api/translate`: Translates content to Urdu.
- `GET/POST /api/profile/background`: Manage background data.
- `GET/POST /api/profile/preference`: Manage language/UI preferences.

## Implementation Plan
1. **Refine Auth & Profile**: (Mostly Done) Verify global guard and background storage.
2. **Personalization Button**: (Mostly Done) Ensure it uses the stored background correctly.
3. **Urdu Translation Feature**:
   - Create `TranslateButton` component.
   - Implement `POST /api/translate` in the backend.
   - Add state management in `DocItem` wrapper to swap content.
4. **UI Integration**: Swizzle `DocItem/Content` to inject both buttons.
