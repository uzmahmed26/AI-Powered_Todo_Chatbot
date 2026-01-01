# Implementation Tasks: Advanced Features - Intelligence, Deployment, Multi-language & Voice

**Feature**: 006-bonus-features
**Branch**: `006-bonus-features`
**Created**: 2025-12-31

## Overview

This document provides concrete implementation tasks for bonus features:
- **User Story 1 (P3)**: Multi-language Support (English + Urdu)
- **User Story 2 (P4)**: Voice Commands (Web Speech API)
- **User Story 3 (P5)**: Reusable Agent Skills (Decorator pattern)
- **User Story 4 (P5)**: Cloud Deployment Blueprints (IaC generation)

## Task Organization

- **Phase 1**: Setup (dependencies, environment)
- **Phase 2**: Foundational (database, shared utilities)
- **Phase 3**: User Story 1 - Multi-language Support (P3) ⭐ **RECOMMENDED MVP**
- **Phase 4**: User Story 2 - Voice Commands (P4)
- **Phase 5**: User Story 3 - Agent Skills (P5)
- **Phase 6**: User Story 4 - Cloud Blueprints (P5)
- **Phase 7**: Polish & Integration

**Test Approach**: Tests included for P3 multi-language feature (user-facing). Tests optional for P4-P5 features per constitution (TDD optional for P3+ bonus features).

---

## Phase 1: Setup & Dependencies

**Goal**: Install dependencies and configure project environment

### Frontend Setup

- [X] T001 [P] Install i18next dependencies in frontend/package.json (i18next, react-i18next, i18next-browser-languagedetector)
- [X] T002 [P] Verify Web Speech API browser support check in frontend/src/utils/browserCompat.ts
- [X] T003 [P] Create TypeScript type definitions in frontend/src/types/translation.types.ts

### Backend Setup

- [X] T004 [P] Install Jinja2 for blueprint templates in backend/requirements.txt
- [X] T005 [P] Verify Pydantic version compatibility for skills type hints in backend/requirements.txt

### Environment Configuration

- [X] T006 Create environment variables for supported languages in .env.example (SUPPORTED_LANGUAGES=en,ur)
- [X] T007 Create environment variables for blueprint config in .env.example (BLUEPRINT_OUTPUT_DIR, BLUEPRINT_EXPIRY_HOURS)

---

## Phase 2: Foundational Tasks

**Goal**: Database migration and shared infrastructure (blocks all user stories)

### Database Migration

- [X] T008 Create migration SQL script migrations/006_add_language_voice_columns.sql (ALTER TABLE messages ADD COLUMN detected_language VARCHAR(5) DEFAULT 'en', ADD COLUMN voice_input BOOLEAN DEFAULT FALSE)
- [ ] T009 Run database migration and verify columns added successfully (REQUIRES DATABASE ACCESS - User action needed)
- [X] T010 Create index on detected_language column for analytics queries (Included in T008 migration script)

### Shared Backend Utilities

- [X] T011 [P] Create skills registry module backend/src/skills/__init__.py
- [X] T012 [P] Implement @skill decorator in backend/src/skills/registry.py with SKILL_REGISTRY dict

---

## Phase 3: User Story 1 - Multi-language Support (P3) ⭐ **MVP SCOPE**

**Story Goal**: Users interact with chatbot in English or Urdu with automatic language detection and localized responses

**Independent Test**: Send Urdu message "میں دودھ خریدنا چاہتا ہوں", verify language detected as Urdu, task created, response in Urdu

**Success Criteria**:
- ✅ Language detection 95%+ accuracy for clear inputs
- ✅ Urdu speakers complete task workflows 85%+ success rate
- ✅ Language switching seamless without conversation reset

### US1: Tests (TDD - Red Phase)

- [X] T013 [P] [US1] Write test for detectLanguage('Hello world') → 'en' in frontend/tests/utils/languageDetection.test.ts
- [X] T014 [P] [US1] Write test for detectLanguage('مرحبا') → 'ur' in frontend/tests/utils/languageDetection.test.ts
- [X] T015 [P] [US1] Write test for detectLanguage('Hello مرحبا مرحبا') → 'ur' (dominant language) in frontend/tests/utils/languageDetection.test.ts
- [X] T016 [P] [US1] Write test for getEffectiveLanguage with auto-detection enabled in frontend/tests/utils/languageDetection.test.ts
- [X] T017 [P] [US1] Write test for language preference persistence in localStorage in frontend/tests/utils/languageDetection.test.ts

### US1: Language Detection (Green Phase)

- [X] T018 [US1] Implement detectLanguage function using Unicode character ranges in frontend/src/utils/languageDetection.ts (Arabic U+0600-U+06FF for Urdu, Latin for English)
- [X] T019 [US1] Implement getLanguagePreference function to read from localStorage in frontend/src/utils/languageDetection.ts
- [X] T020 [US1] Implement saveLanguagePreference function to write to localStorage in frontend/src/utils/languageDetection.ts
- [X] T021 [US1] Implement getEffectiveLanguage function (auto-detect or use preference) in frontend/src/utils/languageDetection.ts
- [X] T022 [US1] Verify all detectLanguage tests pass (T013-T017)

### US1: i18next Configuration

- [X] T023 [US1] Create English translation file frontend/src/locales/en.json with chat UI strings (placeholder, voiceButton, send, taskCreated, taskDeleted, errors)
- [X] T024 [US1] Create Urdu translation file frontend/src/locales/ur.json with translated strings (پیغام لکھیں, صوتی ان پٹ, بھیجیں, etc.)
- [X] T025 [US1] Create LanguageContext with i18next initialization in frontend/src/contexts/LanguageContext.tsx
- [X] T026 [US1] Wrap App component with LanguageContext provider in frontend/src/App.tsx

### US1: Language Toggle UI

- [X] T027 [P] [US1] Create LanguageToggle component with en/ur switch in frontend/src/components/LanguageToggle.tsx
- [X] T028 [P] [US1] Style LanguageToggle component with RTL support in frontend/src/components/LanguageToggle.css
- [X] T029 [US1] Integrate LanguageToggle into chat header in frontend/src/pages/SmartTodoApp.tsx

### US1: Backend Language Support

- [X] T030 [US1] Update message creation API to accept detected_language parameter in backend/src/api/models.py
- [X] T031 [US1] Store detected_language in messages table on message creation in backend/src/api/services/message_service.py
- [X] T032 [US1] Update GPT-4 system prompt to respond in detected language in backend/src/agent/agent.py

### US1: E2E Integration Test

- [ ] T033 [US1] Write E2E test: user sends English message, receives English response in frontend/tests/e2e/multi-language.spec.ts
- [ ] T034 [US1] Write E2E test: user sends Urdu message, receives Urdu response in frontend/tests/e2e/multi-language.spec.ts
- [ ] T035 [US1] Write E2E test: user switches language mid-conversation, system adapts in frontend/tests/e2e/multi-language.spec.ts
- [ ] T036 [US1] Verify all User Story 1 acceptance scenarios pass

---

## Phase 4: User Story 2 - Voice Commands (P4)

**Story Goal**: Users issue voice commands hands-free with Web Speech API transcription

**Independent Test**: Click microphone, speak "Add buy groceries", verify transcription displayed, task created

**Success Criteria**:
- ✅ Speech-to-text 90%+ accuracy in quiet environments
- ✅ Voice processing <5 seconds (recording + transcription + agent)
- ✅ 80%+ success rate on first attempt

### US2: Voice Input Hook

- [ ] T037 [P] [US2] Create useVoiceInput hook with SpeechRecognition initialization in frontend/src/hooks/useVoiceInput.ts
- [ ] T038 [P] [US2] Implement startRecording function with language auto-detection in frontend/src/hooks/useVoiceInput.ts
- [ ] T039 [P] [US2] Implement stopRecording function with final transcript capture in frontend/src/hooks/useVoiceInput.ts
- [ ] T040 [P] [US2] Implement cancelRecording function with cleanup in frontend/src/hooks/useVoiceInput.ts
- [ ] T041 [P] [US2] Add interim results handler for real-time transcription display in frontend/src/hooks/useVoiceInput.ts
- [ ] T042 [P] [US2] Add error handling for permission denied, no speech, timeout in frontend/src/hooks/useVoiceInput.ts

### US2: Voice Input UI

- [ ] T043 [P] [US2] Create VoiceInputButton component with microphone icon in frontend/src/components/VoiceInputButton.tsx
- [ ] T044 [P] [US2] Style VoiceInputButton with recording state (idle, recording, error) in frontend/src/components/VoiceInputButton.css
- [ ] T045 [US2] Integrate VoiceInputButton into chat input area in frontend/src/pages/SmartTodoApp.tsx
- [ ] T046 [US2] Add transcription preview area with edit capability in frontend/src/pages/SmartTodoApp.tsx
- [ ] T047 [US2] Add confirm/cancel buttons for transcript in frontend/src/pages/SmartTodoApp.tsx

### US2: Voice Language Selection

- [ ] T048 [US2] Implement getVoiceRecognitionLanguage function (uses last detected conversation language) in frontend/src/hooks/useVoiceInput.ts
- [ ] T049 [US2] Set SpeechRecognition.lang to 'ur-PK' or 'en-US' based on conversation context in frontend/src/hooks/useVoiceInput.ts
- [ ] T050 [US2] Add fallback to browser locale if no conversation history in frontend/src/hooks/useVoiceInput.ts

### US2: Backend Integration

- [ ] T051 [US2] Update message creation API to accept voice_input boolean parameter in backend/src/api/routes/messages.py
- [ ] T052 [US2] Store voice_input=true flag in messages table for voice-originated messages in backend/src/api/routes/messages.py
- [ ] T053 [US2] Add logging for voice input sessions (session_id, language, confidence, errors) in backend/src/services/logging_service.py

### US2: E2E Integration Test (Optional)

- [ ] T054 [US2] Write E2E test: click mic, speak English command, verify transcript, submit in frontend/tests/e2e/voice-input.spec.ts (OPTIONAL)
- [ ] T055 [US2] Write E2E test: voice input with Urdu speech, verify ur-PK recognized in frontend/tests/e2e/voice-input.spec.ts (OPTIONAL)
- [ ] T056 [US2] Verify User Story 2 acceptance scenarios pass

---

## Phase 5: User Story 3 - Reusable Agent Skills (P5)

**Story Goal**: Development team creates reusable skills for common task patterns

**Independent Test**: Create date_parsing skill, invoke from multiple places, verify DRY principle

**Success Criteria**:
- ✅ Development time reduced 30%+ when using skills vs reimplementing
- ✅ Code duplication reduced 40%+ across agents
- ✅ Skill reuse rate 60%+ (skills used by multiple agents)

### US3: Skill Implementations

- [ ] T057 [P] [US3] Implement date_parsing skill with @skill decorator in backend/src/skills/date_parsing.py (parses "tomorrow", "next Friday", "in 3 days")
- [ ] T058 [P] [US3] Implement task_filtering skill in backend/src/skills/task_filtering.py (filters by status, date, priority)
- [ ] T059 [P] [US3] Implement input_validation skill in backend/src/skills/input_validation.py (validates title length, due_date future, priority enum)
- [ ] T060 [P] [US3] Implement error_translation skill in backend/src/skills/error_translation.py (translates technical errors to en/ur user messages)

### US3: Skill Testing (Optional)

- [ ] T061 [P] [US3] Write unit test for date_parsing("tomorrow") in backend/tests/skills/test_date_parsing.py (OPTIONAL)
- [ ] T062 [P] [US3] Write unit test for task_filtering with status filter in backend/tests/skills/test_task_filtering.py (OPTIONAL)
- [ ] T063 [P] [US3] Write unit test for input_validation with invalid title in backend/tests/skills/test_input_validation.py (OPTIONAL)
- [ ] T064 [P] [US3] Write unit test for error_translation to Urdu in backend/tests/skills/test_error_translation.py (OPTIONAL)

### US3: Skill Integration

- [ ] T065 [US3] Integrate date_parsing skill into task creation endpoint in backend/src/api/routes/tasks.py
- [ ] T066 [US3] Integrate task_filtering skill into task list endpoint in backend/src/api/routes/tasks.py
- [ ] T067 [US3] Integrate input_validation skill into task creation validation in backend/src/api/routes/tasks.py
- [ ] T068 [US3] Integrate error_translation skill into API error handlers in backend/src/api/app.py
- [ ] T069 [US3] Verify all skills registered in SKILL_REGISTRY at module import

---

## Phase 6: User Story 4 - Cloud Deployment Blueprints (P5)

**Story Goal**: Operations team generates IaC for AWS/GCP/Azure from declarative specs

**Independent Test**: Invoke AWS blueprint skill with params, verify generated Terraform files with secrets manager refs

**Success Criteria**:
- ✅ Blueprints deploy successfully 95%+ without manual modification
- ✅ Deployment time reduced 50%+ vs manual setup
- ✅ Security audit findings reduced 70%+ using blueprint configs

### US4: Blueprint Templates

- [ ] T070 [P] [US4] Create AWS Lambda Terraform template in backend/src/blueprints/templates/aws_lambda.tf.j2 (Lambda + IAM + secrets manager data source)
- [ ] T071 [P] [US4] Create AWS RDS Terraform template in backend/src/blueprints/templates/aws_rds.tf.j2 (RDS + VPC + security groups)
- [ ] T072 [P] [US4] Create GCP Cloud Functions template in backend/src/blueprints/templates/gcp_function.tf.j2 (Cloud Functions + IAM + Secret Manager)
- [ ] T073 [P] [US4] Create GCP Cloud SQL template in backend/src/blueprints/templates/gcp_sql.tf.j2 (Cloud SQL + VPC)
- [ ] T074 [P] [US4] Create Azure Functions ARM template in backend/src/blueprints/templates/azure_function.json.j2 (Function App + Key Vault)
- [ ] T075 [P] [US4] Create Azure Database ARM template in backend/src/blueprints/templates/azure_db.json.j2 (Azure Database + VNet)

### US4: Blueprint Generator

- [ ] T076 [P] [US4] Implement generate_aws_blueprint skill in backend/src/skills/blueprints.py with Jinja2 rendering
- [ ] T077 [P] [US4] Implement generate_gcp_blueprint skill in backend/src/skills/blueprints.py with Jinja2 rendering
- [ ] T078 [P] [US4] Implement generate_azure_blueprint skill in backend/src/skills/blueprints.py with Jinja2 rendering
- [ ] T079 [P] [US4] Implement validate_blueprint skill for parameter validation in backend/src/skills/blueprints.py (region valid, instance types, scaling min<max)

### US4: Blueprint API

- [ ] T080 [US4] Create POST /api/blueprints/generate endpoint in backend/src/api/routes/blueprints.py
- [ ] T081 [US4] Add request validation using Pydantic models in backend/src/api/routes/blueprints.py
- [ ] T082 [US4] Add secrets setup instructions generation (Markdown with pre-create commands) in backend/src/blueprints/generator.py
- [ ] T083 [US4] Add deployment instructions generation (Markdown with terraform init/apply steps) in backend/src/blueprints/generator.py

### US4: Testing (Optional)

- [ ] T084 [P] [US4] Write test for AWS blueprint generation with secrets references in backend/tests/blueprints/test_aws_generator.py (OPTIONAL)
- [ ] T085 [P] [US4] Write test for GCP blueprint generation in backend/tests/blueprints/test_gcp_generator.py (OPTIONAL)
- [ ] T086 [P] [US4] Write test for Azure blueprint generation in backend/tests/blueprints/test_azure_generator.py (OPTIONAL)
- [ ] T087 [US4] Verify User Story 4 acceptance scenarios pass

---

## Phase 7: Polish & Integration

**Goal**: Cross-cutting improvements and final integration

### Documentation

- [ ] T088 [P] Update README.md with multi-language and voice setup instructions
- [ ] T089 [P] Create API documentation for blueprint generation endpoint
- [ ] T090 [P] Add inline code comments for language detection algorithm
- [ ] T091 [P] Add inline code comments for voice input lifecycle

### Error Handling & Logging

- [ ] T092 [P] Add structured logging for language detection events in frontend/src/utils/languageDetection.ts
- [ ] T093 [P] Add structured logging for voice input sessions in frontend/src/hooks/useVoiceInput.ts
- [ ] T094 [P] Add structured logging for skill invocations in backend/src/skills/registry.py
- [ ] T095 [P] Add structured logging for blueprint generation in backend/src/skills/blueprints.py

### Performance Optimization

- [ ] T096 Verify language detection <50ms performance target (client-side benchmark)
- [ ] T097 Verify voice transcription <3s p95 performance target (E2E test)
- [ ] T098 Verify blueprint generation <10s p95 performance target (backend benchmark)
- [ ] T099 Verify skill invocation <10ms overhead (unit test)

### Browser Compatibility

- [ ] T100 Test multi-language on Chrome 90+, Edge 90+, Safari 14+
- [ ] T101 Test voice input on Chrome 90+, Edge 90+ (Web Speech API support)
- [ ] T102 Add graceful degradation message for unsupported browsers (Firefox voice)
- [ ] T103 Verify RTL text rendering for Urdu in all supported browsers

### Final Integration

- [ ] T104 Run full E2E test suite for all user stories
- [ ] T105 Verify all acceptance scenarios pass for US1 (multi-language)
- [ ] T106 Verify all acceptance scenarios pass for US2 (voice)
- [ ] T107 Create git commit with descriptive message and co-author attribution
- [ ] T108 Create pull request with summary of 4 bonus features implemented

---

## Dependencies & Execution Order

### Story Completion Order

```
Phase 1 (Setup) → Phase 2 (Foundational)
  ↓
Phase 3 (US1: Multi-language) ⭐ MVP - INDEPENDENT, can ship alone
  ↓
Phase 4 (US2: Voice) - DEPENDS ON US1 (uses language detection for voice language selection)
  ↓
Phase 5 (US3: Skills) - INDEPENDENT, can run in parallel with US4
  ↓
Phase 6 (US4: Blueprints) - INDEPENDENT (uses skills from US3, but can stub for testing)
  ↓
Phase 7 (Polish) - Runs after all stories complete
```

### Critical Path

1. **Phase 1** (Setup) → **Phase 2** (Foundational) - BLOCKING ALL STORIES
2. **Phase 3** (US1) - BLOCKS Phase 4 (US2 depends on language detection)
3. **Phase 5** (US3) + **Phase 6** (US4) - CAN RUN IN PARALLEL after Phase 2
4. **Phase 7** (Polish) - Runs last

### Parallel Execution Opportunities

**After Phase 2 completion, can parallelize**:

- **Team A**: Implement Phase 3 (US1: Multi-language) - 19 tasks
  - All [US1] tasks (T013-T036)

- **Team B**: Implement Phase 5 (US3: Agent Skills) - 13 tasks
  - All [US3] tasks (T057-T069) - Can start immediately, independent of US1

- **Team C**: Implement Phase 6 (US4: Cloud Blueprints) - 18 tasks
  - All [US4] tasks (T070-T087) - Can start immediately, uses US3 skills but can stub

**After Phase 3 completion**:
- **Team A** switches to Phase 4 (US2: Voice Commands) - 20 tasks
  - All [US2] tasks (T037-T056) - Requires US1 language detection

**Estimated Timeline**:
- **Sequential**: ~8-10 weeks (all phases one after another)
- **Parallel (3 teams)**: ~4-5 weeks (US1 + US3 + US4 parallel, then US2, then polish)

---

## MVP Recommendation

**Ship Phase 3 (User Story 1: Multi-language) as standalone MVP**

**Rationale**:
- User-facing feature with immediate value (Urdu speakers enabled)
- Independent from other stories (no dependencies on voice/skills/blueprints)
- Testable in isolation (E2E tests for language detection and switching)
- Low risk (client-side language detection, no infrastructure changes)
- High impact (accessibility improvement, international user base)

**Phase 3 Task Count**: 24 tasks (T013-T036)

**Estimated Effort**: 1-2 weeks for single developer following TDD

**Validation**: Run independent test "Send Urdu message, verify Urdu response" after T036

---

## Task Format Validation

✅ All 108 tasks follow required format:
- ✅ Checkbox: `- [ ]`
- ✅ Task ID: Sequential T001-T108
- ✅ [P] marker: Applied to parallelizable tasks (different files)
- ✅ [Story] label: Applied to user story tasks ([US1], [US2], [US3], [US4])
- ✅ File paths: Included for all implementation tasks
- ✅ Clear descriptions: Actionable with specific outcomes

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total Tasks | 108 |
| Setup Tasks (Phase 1) | 7 |
| Foundational Tasks (Phase 2) | 5 |
| US1 Tasks (P3 Multi-language) ⭐ | 24 |
| US2 Tasks (P4 Voice) | 20 |
| US3 Tasks (P5 Skills) | 13 |
| US4 Tasks (P5 Blueprints) | 18 |
| Polish Tasks (Phase 7) | 21 |
| Parallelizable Tasks [P] | 62 (57%) |
| Test Tasks | 17 (US1: 5 required, US2-US4: 12 optional) |

**Execution Modes**:
- **MVP Only (US1)**: 36 tasks (Phase 1+2+3) - 1-2 weeks
- **MVP + Voice (US1+US2)**: 56 tasks - 3-4 weeks
- **Full Feature Set (All)**: 108 tasks - 8-10 weeks sequential, 4-5 weeks parallel (3 teams)

**Next Command**: Start implementation with `/sp.implement` or begin with MVP scope (T001-T036)
