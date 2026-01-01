# Implementation Plan: Advanced Features - Intelligence, Deployment, Multi-language & Voice

**Branch**: `006-bonus-features` | **Date**: 2025-12-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-bonus-features/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement bonus features for the AI-powered todo chatbot to enhance functionality beyond core MVP:

1. **Multi-language Support (P3)**: Enable Urdu + English language detection and localized responses using Unicode character-set analysis for detection and GPT-4 for multilingual NLU processing
2. **Voice Commands (P4)**: Provide hands-free todo management via Web Speech API with automatic language selection based on conversation context
3. **Reusable Agent Skills (P5)**: Create decorator-based skill registry for common task management patterns (filtering, date parsing, error translation)
4. **Cloud Deployment Blueprints (P5)**: Generate infrastructure-as-code for AWS/GCP/Azure with secrets manager integration

**Technical Approach**: Frontend-focused enhancements with lightweight backend extensions. Language detection runs client-side (JavaScript Unicode analysis). Voice input uses browser-native Web Speech API. Skills implemented as Python decorator pattern. Blueprints as template generation skills.

## Technical Context

**Language/Version**:
- Frontend: TypeScript 5.x + React 18.x
- Backend: Python 3.11+

**Primary Dependencies**:
- Frontend: React, Web Speech API (browser native), i18next (internationalization)
- Backend: FastAPI, Pydantic (type validation), Jinja2 (blueprint templates)

**Storage**:
- PostgreSQL (existing todo database)
- Browser localStorage (language preference persistence)

**Testing**:
- Frontend: Jest + React Testing Library
- Backend: pytest
- E2E: Playwright for voice/language integration tests

**Target Platform**:
- Frontend: Modern browsers (Chrome 90+, Edge 90+, Safari 14+ for Web Speech API)
- Backend: Linux server (existing FastAPI deployment)

**Project Type**: Web application (existing frontend + backend architecture)

**Performance Goals**:
- Language detection: <50ms client-side (instant Unicode analysis)
- Voice transcription: <3s p95 (Web Speech API streaming)
- Blueprint generation: <10s p95
- Skill invocation overhead: <10ms

**Constraints**:
- Zero additional infrastructure costs (use browser-native APIs where possible)
- No breaking changes to existing todo operations
- Web Speech API browser compatibility: 95%+ user coverage
- Client-side language detection for offline capability

**Scale/Scope**:
- 2 languages (English, Urdu) with extensible architecture for future languages
- 4-6 initial agent skills (filtering, date parsing, validation, error translation)
- 3 cloud provider blueprints (AWS, GCP, Azure)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. MCP-First Stateless Architecture ✅ PASS
- **Status**: COMPLIANT
- **Analysis**: Features are additions to existing MCP-first architecture
  - Language detection is client-side (no server state)
  - Voice input is client-side (no server state)
  - Skills are stateless functions (inputs → outputs)
  - Blueprints generate static files (no runtime state)
  - Language preference stored in localStorage (client-side persistence)
- **Action**: None required

### II. Specification-First Development ✅ PASS
- **Status**: COMPLIANT
- **Analysis**: spec.md complete with:
  - User scenarios with Given-When-Then acceptance criteria
  - Measurable success criteria (95% language detection, 90% voice accuracy)
  - Edge cases documented with resolutions
  - Priorities defined (P3-P5)
  - Clear separation of business requirements and technical implementation
- **Action**: None required

### III. Test-Driven Development (TDD) ⚠️ CONDITIONAL PASS
- **Status**: OPTIONAL for P3+ bonus features per constitution
- **Analysis**: These are P3-P5 features where TDD is "highly recommended" but not mandatory
- **Recommended Approach**: Write tests for P3 multi-language (user-facing), optional for P5 skills/blueprints
- **Action**: Include test specifications in tasks.md; implement tests for P3 feature at minimum

### IV. Natural Language First ✅ PASS
- **Status**: COMPLIANT
- **Analysis**: Features enhance natural language capabilities:
  - Multi-language extends NLU to Urdu speakers
  - Voice input provides alternative natural language modality
  - Skills improve natural date parsing and error translation
  - No rigid syntax requirements introduced
- **Action**: None required

### V. Error Handling & User Safety ✅ PASS
- **Status**: COMPLIANT
- **Analysis**: Error scenarios documented:
  - Voice API failure → graceful fallback to text input
  - Low audio quality → retry prompt with user-friendly message
  - Language detection ambiguity → default to English, allow manual override
  - Speech transcription displayed for user verification before execution
- **Action**: Implement error handling per spec edge cases

### VI. Security & Privacy First ✅ PASS
- **Status**: COMPLIANT
- **Analysis**:
  - Blueprint secrets management: cloud-native secrets managers (AWS Secrets Manager, etc.), zero hardcoded credentials
  - Voice audio not persisted (processed client-side via Web Speech API)
  - Language preference stored locally (no server tracking)
  - User input validation maintained through existing MCP layer
  - No new authentication/authorization requirements
- **Action**: None required

### VII. Performance & Scalability ✅ PASS
- **Status**: COMPLIANT
- **Analysis**: Performance targets specified:
  - Language detection <50ms (client-side, no network latency)
  - Voice transcription <3s p95 (Web Speech API streaming)
  - Blueprint generation <10s p95
  - Skill overhead <10ms
  - Client-side processing reduces server load
  - Stateless skills enable horizontal scaling
- **Action**: None required

### VIII. Observability & Debugging ✅ PASS
- **Status**: COMPLIANT
- **Analysis**:
  - Language detection events logged (language switches, detection confidence)
  - Voice input sessions logged (transcription attempts, fallback triggers)
  - Skill invocations logged (skill name, version, execution time)
  - Blueprint generation logged (target platform, template used)
  - No sensitive data logged (voice audio not persisted, transcriptions logged without PII)
- **Action**: Add structured logging per existing patterns

### IX. AI Quality & Reliability ✅ PASS
- **Status**: COMPLIANT
- **Analysis**:
  - Multilingual NLU validated through acceptance tests
  - Voice transcription user-verified before agent processing
  - Language detection confidence threshold (95%+ accuracy requirement)
  - Graceful degradation (voice → text fallback, English default)
  - Skills tested independently before agent integration
- **Action**: Implement validation gates per spec

### X. Simplicity & Maintainability ✅ PASS
- **Status**: COMPLIANT
- **Analysis**:
  - Decorator pattern for skills (simple, Pythonic, no framework overhead)
  - Browser-native APIs for voice/language (zero infrastructure)
  - Client-side language detection (simple Unicode ranges, no ML models)
  - Templates for blueprints (straightforward Jinja2, no complex codegen)
  - Minimal dependencies (i18next for translations, existing stack otherwise)
- **Action**: None required

**GATE VERDICT: ✅ PASS** - All principles satisfied. Feature may proceed to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/006-bonus-features/
├── plan.md                              # This file (implementation plan)
├── spec.md                              # Feature specification (from /sp.specify)
├── research.md                          # Technology research & decisions
├── data-model.md                        # Entity schemas & relationships
├── quickstart.md                        # Developer quickstart guide
├── contracts/                           # API contracts
│   ├── language-detection.contract.ts   # Language detection types
│   ├── voice-input.contract.ts          # Web Speech API types
│   ├── agent-skills.contract.py         # Skills registry & decorator
│   └── blueprint-generation.contract.py # Blueprint generation API
└── tasks.md                             # Implementation tasks (from /sp.tasks - NOT YET CREATED)
```

### Source Code (repository root)

**Structure Decision**: Web application (Option 2) - Extends existing frontend + backend architecture

```text
frontend/                                # React + TypeScript
├── src/
│   ├── utils/
│   │   └── languageDetection.ts         # NEW: Unicode character-set analysis
│   ├── hooks/
│   │   └── useVoiceInput.ts             # NEW: Web Speech API hook
│   ├── components/
│   │   ├── LanguageToggle.tsx           # NEW: Manual language override UI
│   │   ├── LanguageToggle.css           # NEW: Styling
│   │   └── VoiceInputButton.tsx         # NEW: Microphone button component
│   ├── locales/
│   │   ├── en.json                      # NEW: English translations
│   │   └── ur.json                      # NEW: Urdu translations
│   ├── contexts/
│   │   └── LanguageContext.tsx          # NEW: i18next provider & context
│   └── types/
│       └── translation.types.ts         # NEW: i18next TypeScript types
└── tests/
    ├── utils/
    │   └── languageDetection.test.ts    # NEW: Language detection tests
    ├── hooks/
    │   └── useVoiceInput.test.ts        # NEW: Voice input tests
    └── e2e/
        ├── multi-language.spec.ts       # NEW: E2E language switching tests
        └── voice-input.spec.ts          # NEW: E2E voice input tests

backend/                                 # FastAPI + Python
├── src/
│   ├── skills/
│   │   ├── __init__.py                  # NEW: Skill module initialization
│   │   ├── registry.py                  # NEW: @skill decorator + SKILL_REGISTRY
│   │   ├── date_parsing.py              # NEW: Natural date parsing skill
│   │   ├── task_filtering.py            # NEW: Task filtering skill
│   │   ├── input_validation.py          # NEW: Input validation skill
│   │   └── error_translation.py         # NEW: Error translation skill (en/ur)
│   ├── blueprints/
│   │   ├── __init__.py                  # NEW: Blueprint module
│   │   ├── generator.py                 # NEW: Blueprint generation logic
│   │   └── templates/
│   │       ├── aws_lambda.tf.j2         # NEW: AWS Lambda Terraform template
│   │       ├── aws_rds.tf.j2            # NEW: AWS RDS Terraform template
│   │       ├── gcp_function.tf.j2       # NEW: GCP Cloud Functions template
│   │       ├── gcp_sql.tf.j2            # NEW: GCP Cloud SQL template
│   │       ├── azure_function.json.j2   # NEW: Azure Functions ARM template
│   │       └── azure_db.json.j2         # NEW: Azure Database ARM template
│   └── api/
│       └── routes/
│           └── blueprints.py            # NEW: /api/blueprints/generate endpoint
└── tests/
    ├── skills/
    │   ├── test_date_parsing.py         # NEW: Date parsing skill tests
    │   ├── test_task_filtering.py       # NEW: Filtering skill tests
    │   ├── test_input_validation.py     # NEW: Validation skill tests
    │   └── test_error_translation.py    # NEW: Error translation tests
    └── blueprints/
        ├── test_aws_generator.py        # NEW: AWS blueprint generation tests
        ├── test_gcp_generator.py        # NEW: GCP blueprint generation tests
        └── test_azure_generator.py      # NEW: Azure blueprint generation tests

migrations/
└── 006_add_language_voice_columns.sql   # NEW: DB schema migration (messages table)

.specify/
└── agent-context/
    └── claude-context.md                # UPDATED: New technologies added
```

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations.** All constitutional principles satisfied (see Constitution Check section above).

---

## Post-Design Constitution Re-Check

*Required gate after Phase 1 design completion*

### Design Artifacts Generated ✅
- ✅ research.md: All technology decisions documented with alternatives
- ✅ data-model.md: Entity schemas defined (minimal DB changes: +2 columns)
- ✅ contracts/: 4 contract files (language, voice, skills, blueprints)
- ✅ quickstart.md: Developer onboarding guide

### Architecture Validation ✅

**MCP-First Stateless**: ✅ PASS
- Language detection: client-side (stateless)
- Voice input: client-side (stateless)
- Skills: pure functions (stateless)
- Blueprints: file generation (stateless)
- **No new server state introduced**

**Performance Targets**: ✅ PASS
- Language detection: <50ms (Unicode analysis)
- Voice transcription: <3s p95 (Web Speech API)
- Blueprint generation: <10s p95 (Jinja2 templates)
- Skill overhead: <10ms (dictionary lookup)
- **All targets achievable with chosen technologies**

**Security**: ✅ PASS
- Secrets management: Cloud-native secrets managers (no hardcoding)
- Voice privacy: Audio never persisted
- Language preference: Client-side localStorage (no server tracking)
- SQL injection: Parameterized queries (existing protection maintained)
- **No new security vulnerabilities introduced**

**Simplicity**: ✅ PASS
- Decorator pattern: 10 lines implementation
- i18next: Industry standard (no custom i18n)
- Web Speech API: Browser-native (zero infrastructure)
- Jinja2: Python-native templating
- **No unnecessary complexity added**

### NFR Coverage ✅

| NFR Category | Addressed | Evidence |
|--------------|-----------|----------|
| Accuracy | ✅ | Language detection 95%+, voice 90%+ (spec requirements) |
| Performance | ✅ | Targets specified for all operations (<50ms, <3s, <10s) |
| Usability | ✅ | Voice button, transcription verification, manual override |
| Maintainability | ✅ | Skills documented, versioned, independently testable |
| Security | ✅ | Secrets managers, audio privacy, no hardcoded credentials |
| Observability | ✅ | Structured logging for language, voice, skills, blueprints |
| Scalability | ✅ | Client-side processing, stateless skills, horizontal scaling |

**FINAL GATE VERDICT: ✅ PASS** - Design satisfies all constitutional principles. Ready for Phase 2 (tasks.md generation via /sp.tasks).

---

## Next Steps

1. ✅ **Phase 0 Complete**: Research decisions documented
2. ✅ **Phase 1 Complete**: Design artifacts generated (data-model, contracts, quickstart)
3. ⏭️ **Phase 2**: Run `/sp.tasks` to generate concrete implementation tasks
4. ⏭️ **Implementation**: Execute tasks.md following TDD (Red-Green-Refactor)

**Command to proceed**: `/sp.tasks`
