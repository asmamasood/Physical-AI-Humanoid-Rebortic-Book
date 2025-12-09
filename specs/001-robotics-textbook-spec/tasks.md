# Tasks: Robotics Textbook Generation

**Input**: Design documents from `/specs/001-robotics-textbook-spec/`
**Prerequisites**: plan.md, spec.md, data-model.md, research.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel
- **[Story]**: Which user story this task belongs to
- Include exact file paths in descriptions

## Path Conventions

- Paths are relative to the repository root.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the directory structure for the book content.

- [X] T001 [P] Create module directories in `physical-ai-robotics-book/docs/` (module-1, module-2, module-3, module-4)
- [X] T002 [P] Create corresponding chapter/subchapter directories inside each module directory.
- [X] T003 [P] Create parallel directory structure for Urdu content in `physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Set up the testing framework.

- [ ] T004 Initialize Playwright in `physical-ai-robotics-book/` and create a basic test scaffolding in `physical-ai-robotics-book/tests/`.

---

## Phase 3: User Story 1 - Module 1 (Priority: P1) 🎯 MVP

**Goal**: Generate all content for Module 1 and test its rendering.
**Independent Test**: The Docusaurus site renders Module 1 correctly in both English and Urdu.

### Implementation for User Story 1

- [ ] T005 [US1] Generate English content for Module 1, Chapter 1 in `physical-ai-robotics-book/docs/module-1/chapter-1.md`.
- [ ] T006 [P] [US1] Generate Urdu content for Module 1, Chapter 1 in `physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/module-1/chapter-1.md`.
- [ ] T007 [US1] Generate English content for Module 1, Chapter 2 in `physical-ai-robotics-book/docs/module-1/chapter-2.md`.
- [ ] T008 [P] [US1] Generate Urdu content for Module 1, Chapter 2 in `physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/module-1/chapter-2.md`.
- [ ] T009 [US1] Write Playwright test in `physical-ai-robotics-book/tests/module-1.spec.ts` to verify Module 1 content renders correctly in both languages.

---

## Phase 4: User Story 2 - Module 2 (Priority: P2)

**Goal**: Generate all content for Module 2 and test its rendering.
**Independent Test**: The Docusaurus site renders Module 2 correctly.

### Implementation for User Story 2

- [ ] T010 [US2] Generate English content for Module 2, Chapter 1 in `physical-ai-robotics-book/docs/module-2/chapter-1.md`.
- [ ] T011 [P] [US2] Generate Urdu content for Module 2, Chapter 1 in `physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/module-2/chapter-1.md`.
- [ ] T012 [US2] Generate English content for Module 2, Chapter 2 in `physical-ai-robotics-book/docs/module-2/chapter-2.md`.
- [ ] T013 [P] [US2] Generate Urdu content for Module 2, Chapter 2 in `physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/module-2/chapter-2.md`.
- [ ] T014 [US2] Write Playwright test in `physical-ai-robotics-book/tests/module-2.spec.ts` to verify Module 2 content renders correctly.

---

## Phase 5: User Story 3 - Module 3 (Priority: P3)

**Goal**: Generate all content for Module 3 and test its rendering.
**Independent Test**: The Docusaurus site renders Module 3 correctly.

### Implementation for User Story 3

- [ ] T015 [US3] Generate English content for Module 3, Chapter 1 in `physical-ai-robotics-book/docs/module-3/chapter-1.md`.
- [ ] T016 [P] [US3] Generate Urdu content for Module 3, Chapter 1 in `physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/module-3/chapter-1.md`.
- [ ] T017 [US3] Generate English content for Module 3, Chapter 2 in `physical-ai-robotics-book/docs/module-3/chapter-2.md`.
- [ ] T018 [P] [US3] Generate Urdu content for Module 3, Chapter 2 in `physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/module-3/chapter-2.md`.
- [ ] T019 [US3] Write Playwright test in `physical-ai-robotics-book/tests/module-3.spec.ts` to verify Module 3 content renders correctly.

---

## Phase 6: User Story 4 - Module 4 (Priority: P4)

**Goal**: Generate all content for Module 4 and test its rendering.
**Independent Test**: The Docusaurus site renders Module 4 correctly.

### Implementation for User Story 4

- [ ] T020 [US4] Generate English content for Module 4, Chapter 1 in `physical-ai-robotics-book/docs/module-4/chapter-1.md`.
- [ ] T021 [P] [US4] Generate Urdu content for Module 4, Chapter 1 in `physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/module-4/chapter-1.md`.
- [ ] T022 [US4] Generate English content for Module 4, Chapter 2 in `physical-ai-robotics-book/docs/module-4/chapter-2.md`.
- [ ] T023 [P] [US4] Generate Urdu content for Module 4, Chapter 2 in `physical-ai-robotics-book/i18n/ur/docusaurus-plugin-content-docs/current/module-4/chapter-2.md`.
- [ ] T024 [US4] Write Playwright test in `physical-ai-robotics-book/tests/module-4.spec.ts` to verify Module 4 content renders correctly.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final review and validation.

- [ ] T025 [P] Review all English content for grammar, clarity, and technical accuracy.
- [ ] T026 [P] Review all Urdu content for grammar and clarity.
- [ ] T027 Run all Playwright tests (`npm run test` in `physical-ai-robotics-book/`) and fix any issues.
- [ ] T028 Finalize sidebars and navigation in `physical-ai-robotics-book/sidebars.ts` and `physical-ai-robotics-book/docusaurus.config.ts`.
- [ ] T029 Perform a final build (`npm run build`) to ensure no errors.

## Dependencies & Execution Order

- **Phase 1 & 2**: Can be done in parallel. Must be completed before Phase 3.
- **User Stories (Phase 3-6)**: Can be implemented in parallel after Phase 2 is complete.
- **Polish (Phase 7)**: Depends on all user story phases being complete.

## Implementation Strategy

### Incremental Delivery
1.  Complete Setup & Foundational phases.
2.  Implement User Story 1 (Module 1). Validate it independently.
3.  Implement User Stories 2, 3, and 4. Each can be validated independently.
4.  Complete Polish phase for final release.
