# Tasks: Auth, Personalization, and Urdu Translation

## Phase 1: Backend Infrastructure
- [x] **Auth Guard** <!-- id: 1 -->
  - [x] Protect `/docs` routes in `Root.tsx`.
- [x] **Profile Storage** <!-- id: 2 -->
  - [x] Create `user_backgrounds` table in Neon.
  - [x] Implement API to save/fetch background.
- [x] **Translation API** <!-- id: 3 -->
  - [x] Create `POST /api/translate` endpoint in FastAPI.
  - [x] Implement translation logic in `GeminiAgent`.

## Phase 2: Frontend Components
- [x] **PersonalizeButton** <!-- id: 4 -->
  - [x] Create component to trigger personalization.
  - [x] Integration with `PersonalizationProvider` (or direct API call).
- [x] **TranslateButton** <!-- id: 5 -->
  - [x] Create UI for Urdu/English toggle.
  - [x] Implement API call to `POST /api/translate`.
- [x] **Content Wrapper Extension** <!-- id: 6 -->
  - [x] Logic to swap English content with Urdu content in the DOM.
  - [x] Handle loading states for translation.

## Phase 3: UI Integration & Polishing
- [x] **Docusaurus Swizzling** <!-- id: 7 -->
  - [x] Inject `TranslateButton` next to `PersonalizeButton` in `DocItem/Content`.
- [x] **Persistence** <!-- id: 8 -->
  - [x] Save language preference in user profile/DB.
  - [x] Apply translation automatically if preferred.

## Phase 4: Verification
- [x] Test Urdu translation accuracy.
- [x] Test personalization depth (Beginner vs Advanced).
- [x] Verify auth protection on all book pages.
