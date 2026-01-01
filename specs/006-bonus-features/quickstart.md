# Quickstart Guide: Advanced Features

**Feature**: 006-bonus-features
**For**: Developers implementing multi-language, voice, skills, and blueprints

---

## Overview

This feature adds four bonus enhancements to the todo chatbot:

1. **Multi-language Support**: English + Urdu with automatic detection
2. **Voice Commands**: Hands-free input via Web Speech API
3. **Agent Skills**: Reusable functions for common patterns
4. **Cloud Blueprints**: IaC generation for AWS/GCP/Azure

---

## Prerequisites

- **Frontend**: Node.js 18+, TypeScript 5+, React 18+
- **Backend**: Python 3.11+, FastAPI, Pydantic
- **Database**: PostgreSQL 14+ (existing)
- **Browsers**: Chrome 90+, Edge 90+, or Safari 14+ (for voice)

---

## Quick Start (5 Minutes)

### 1. Multi-language Support

**Frontend Setup**:

```bash
cd frontend
npm install i18next react-i18next
```

**Create Language Detector** (`src/utils/languageDetection.ts`):

```typescript
export function detectLanguage(text: string): 'en' | 'ur' {
  const arabicRegex = /[\u0600-\u06FF]/g;
  const latinRegex = /[a-zA-Z]/g;

  const arabicChars = (text.match(arabicRegex) || []).length;
  const latinChars = (text.match(latinRegex) || []).length;

  return arabicChars > latinChars ? 'ur' : 'en';
}
```

**Test**:

```typescript
console.log(detectLanguage("Hello world")); // => 'en'
console.log(detectLanguage("مرحبا")); // => 'ur'
```

### 2. Voice Input

**Create Voice Hook** (`src/hooks/useVoiceInput.ts`):

```typescript
import { useState } from 'react';

export function useVoiceInput(language: 'en' | 'ur') {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');

  const startRecording = () => {
    const recognition = new (window as any).webkitSpeechRecognition();
    recognition.lang = language === 'ur' ? 'ur-PK' : 'en-US';
    recognition.interimResults = true;

    recognition.onresult = (event: any) => {
      const text = event.results[0][0].transcript;
      setTranscript(text);
    };

    recognition.start();
    setIsRecording(true);
  };

  return { isRecording, transcript, startRecording };
}
```

**Test**:

```typescript
const { transcript, startRecording } = useVoiceInput('en');
// Click mic button → speak → see transcript
```

### 3. Agent Skills

**Backend Setup**:

```bash
cd backend
# No new dependencies needed (uses existing Python stack)
```

**Create Skill Decorator** (`src/skills/registry.py`):

```python
from typing import Callable, Dict, Any

SKILL_REGISTRY: Dict[str, Callable] = {}

def skill(name: str, version: str):
    def decorator(func: Callable):
        SKILL_REGISTRY[name] = func
        return func
    return decorator
```

**Define First Skill** (`src/skills/date_parsing.py`):

```python
from .registry import skill
from datetime import date, timedelta

@skill(name="date_parsing", version="1.0.0")
def parse_natural_date(text: str) -> date:
    """Parse 'tomorrow', 'next Friday', etc."""
    if text.lower() == "tomorrow":
        return date.today() + timedelta(days=1)
    # ... more parsing logic
    return date.today()
```

**Test**:

```python
from skills.registry import SKILL_REGISTRY

parse_fn = SKILL_REGISTRY["date_parsing"]
result = parse_fn("tomorrow")
print(result)  # => 2025-01-01 (if today is 2024-12-31)
```

### 4. Cloud Blueprints

**Backend Setup**:

```bash
pip install jinja2  # For template rendering
```

**Create Blueprint Skill** (`src/skills/blueprints.py`):

```python
from .registry import skill
from jinja2 import Template

AWS_LAMBDA_TEMPLATE = """
resource "aws_lambda_function" "{{ app_name }}" {
  function_name = "{{ app_name }}"
  runtime       = "{{ runtime }}"
  handler       = "main.handler"
  # ... more config
}
"""

@skill(name="generate_aws_blueprint", version="1.0.0")
def generate_aws_blueprint(app_name: str, runtime: str) -> str:
    """Generate AWS Terraform config."""
    template = Template(AWS_LAMBDA_TEMPLATE)
    return template.render(app_name=app_name, runtime=runtime)
```

**Test**:

```python
result = generate_aws_blueprint("todo-api", "python3.11")
print(result)
# => resource "aws_lambda_function" "todo-api" { ... }
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    Frontend (React)                  │
├─────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────────────────┐ │
│  │ Language        │  │ Voice Input              │ │
│  │ Detection       │  │ (Web Speech API)         │ │
│  │ (Unicode)       │  │ - ur-PK / en-US          │ │
│  └─────────────────┘  └──────────────────────────┘ │
│  ┌───────────────────────────────────────────────┐ │
│  │ i18next Translations (en.json, ur.json)       │ │
│  └───────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────┐ │
│  │ localStorage: Language Preference             │ │
│  └───────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
                         ↕ HTTP/JSON
┌─────────────────────────────────────────────────────┐
│                  Backend (FastAPI)                   │
├─────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐│
│  │ Agent Skills Registry                           ││
│  │  - task_filtering                               ││
│  │  - date_parsing                                 ││
│  │  - input_validation                             ││
│  │  - error_translation                            ││
│  └─────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────┐│
│  │ Blueprint Generation Skills                     ││
│  │  - generate_aws_blueprint                       ││
│  │  - generate_gcp_blueprint                       ││
│  │  - generate_azure_blueprint                     ││
│  └─────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────┘
                         ↕ SQL
┌─────────────────────────────────────────────────────┐
│               PostgreSQL Database                    │
├─────────────────────────────────────────────────────┤
│  messages table (+2 columns):                        │
│    - detected_language (en | ur)                     │
│    - voice_input (boolean)                           │
└─────────────────────────────────────────────────────┘
```

---

## File Structure

```
frontend/
├── src/
│   ├── utils/
│   │   └── languageDetection.ts       # NEW: Unicode analysis
│   ├── hooks/
│   │   └── useVoiceInput.ts           # NEW: Web Speech API hook
│   ├── components/
│   │   ├── LanguageToggle.tsx         # NEW: Manual override UI
│   │   └── VoiceInputButton.tsx       # NEW: Microphone button
│   ├── locales/
│   │   ├── en.json                    # NEW: English translations
│   │   └── ur.json                    # NEW: Urdu translations
│   └── contexts/
│       └── LanguageContext.tsx        # NEW: i18next provider

backend/
├── src/
│   ├── skills/
│   │   ├── __init__.py
│   │   ├── registry.py                # NEW: @skill decorator
│   │   ├── date_parsing.py            # NEW: Skill implementation
│   │   ├── task_filtering.py          # NEW: Skill implementation
│   │   ├── input_validation.py        # NEW: Skill implementation
│   │   └── error_translation.py       # NEW: Skill implementation
│   ├── blueprints/
│   │   ├── __init__.py
│   │   ├── generator.py               # NEW: Blueprint generator
│   │   └── templates/
│   │       ├── aws_lambda.tf.j2       # NEW: Terraform template
│   │       ├── gcp_function.tf.j2     # NEW: Terraform template
│   │       └── azure_function.json.j2 # NEW: ARM template
│   └── api/
│       └── routes/
│           └── blueprints.py          # NEW: /api/blueprints/generate

migrations/
└── 006_add_language_voice_columns.sql # NEW: DB migration
```

---

## Database Migration

**Run Migration**:

```bash
psql -U postgres -d todo_chatbot -f migrations/006_add_language_voice_columns.sql
```

**Migration SQL** (`migrations/006_add_language_voice_columns.sql`):

```sql
-- Add language and voice input tracking columns
ALTER TABLE messages
  ADD COLUMN detected_language VARCHAR(5) DEFAULT 'en',
  ADD COLUMN voice_input BOOLEAN DEFAULT FALSE;

-- Add index for language-based analytics
CREATE INDEX idx_messages_language ON messages(detected_language);

-- Verify migration
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'messages'
  AND column_name IN ('detected_language', 'voice_input');
```

---

## Testing

### Language Detection

```typescript
import { detectLanguage } from './utils/languageDetection';

describe('Language Detection', () => {
  it('detects English', () => {
    expect(detectLanguage('Hello world')).toBe('en');
  });

  it('detects Urdu', () => {
    expect(detectLanguage('مرحبا بك')).toBe('ur');
  });

  it('handles mixed input (dominant language)', () => {
    expect(detectLanguage('Hello مرحبا مرحبا')).toBe('ur'); // More Arabic chars
  });
});
```

### Voice Input

```typescript
import { render, screen } from '@testing-library/react';
import { useVoiceInput } from './hooks/useVoiceInput';

test('voice input starts recording', async () => {
  const { startRecording } = useVoiceInput('en');
  startRecording();
  // Assert Web Speech API called
});
```

### Agent Skills

```python
from skills.date_parsing import parse_natural_date
from datetime import date, timedelta

def test_parse_tomorrow():
    result = parse_natural_date("tomorrow")
    expected = date.today() + timedelta(days=1)
    assert result == expected
```

---

## Configuration

### Frontend Environment Variables

```env
# .env.local
REACT_APP_SUPPORTED_LANGUAGES=en,ur
REACT_APP_DEFAULT_LANGUAGE=en
REACT_APP_VOICE_MAX_DURATION=30000  # 30 seconds
```

### Backend Environment Variables

```env
# .env
SUPPORTED_LANGUAGES=en,ur
BLUEPRINT_OUTPUT_DIR=/tmp/blueprints
BLUEPRINT_EXPIRY_HOURS=24
```

---

## Common Pitfalls

### 1. Voice API Not Supported (Firefox)

**Problem**: Web Speech API unavailable in Firefox

**Solution**: Show graceful degradation message

```typescript
if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
  return <div>Voice input not supported in this browser. Try Chrome or Edge.</div>;
}
```

### 2. Language Detection Fails for Transliteration

**Problem**: Roman Urdu (Latin characters) detected as English

**Solution**: Show manual language toggle button

```typescript
<LanguageToggle currentLang={detectedLang} onToggle={setLanguage} />
```

### 3. Skills Not Registered

**Problem**: `@skill` decorator not executed (module not imported)

**Solution**: Import all skill modules in `__init__.py`

```python
# backend/src/skills/__init__.py
from .date_parsing import *
from .task_filtering import *
from .input_validation import *
from .error_translation import *
```

---

## Next Steps

1. **Read**: [research.md](./research.md) for technology decisions
2. **Read**: [data-model.md](./data-model.md) for entity schemas
3. **Read**: [contracts/](./contracts/) for API contracts
4. **Run**: `/sp.tasks` to generate implementation tasks
5. **Implement**: Follow TDD (Red-Green-Refactor) for P3 feature

---

## Support

- **Documentation**: See `specs/006-bonus-features/` directory
- **Constitution**: See `.specify/memory/constitution.md` for principles
- **Issues**: Check existing plan.md for known constraints

---

## Example End-to-End Flow

### User sends Urdu voice message:

1. User clicks microphone button
2. Frontend detects current language: 'ur' (from last message)
3. Web Speech API initialized with lang='ur-PK'
4. User speaks: "کل کے لیے دودھ خریدنے کا کام شامل کریں" (Add task to buy milk for tomorrow)
5. Transcript displayed: "کل کے لیے دودھ خریدنے کا کام شامل کریں"
6. User confirms → sent to backend
7. Backend receives message, detects language='ur' (Unicode analysis)
8. GPT-4 processes intent (create task, due_date=tomorrow)
9. `date_parsing` skill invoked: parse_natural_date("کل") → tomorrow's date
10. Task created in DB with title in Urdu
11. Backend responds in Urdu: "کام کامیابی سے شامل کیا گیا" (Task added successfully)
12. Frontend displays response + updates task list
13. Message saved with detected_language='ur', voice_input=true

**Total latency**: <5 seconds (voice transcription <3s + agent processing <2s)

---

**Ready to implement!** Run `/sp.tasks` to generate concrete implementation tasks.
