# Research: Advanced Features Technical Decisions

**Feature**: 006-bonus-features
**Date**: 2025-12-31
**Phase**: 0 - Research & Technology Selection

## Overview

This document captures research findings and technology decisions for implementing multi-language support, voice commands, agent skills, and cloud deployment blueprints.

## 1. Multi-language Support

### Decision: Unicode Character-Set Analysis for Language Detection

**Chosen**: Client-side Unicode range detection (Latin script → English, Arabic script → Urdu)

**Rationale**:
- **Performance**: Instant detection (<50ms), no network latency
- **Offline capability**: Works without server connection
- **Accuracy**: ~98% for distinct scripts (English uses Latin U+0000-U+007F, Urdu uses Arabic U+0600-U+06FF)
- **Cost**: Zero infrastructure, zero API costs
- **Simplicity**: Lightweight JavaScript implementation (~50 lines)

**Alternatives Considered**:

| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| NLU model language ID (GPT-4) | High accuracy (99%+), handles transliteration | Latency (+500ms), API cost, requires network | Overkill for binary choice; user experience degraded by latency |
| Hybrid (character-set + NLU fallback) | Best accuracy | Increased complexity | YAGNI - character-set sufficient for clear inputs per spec |
| Browser locale preference | Simple implementation | Ignores actual input language | Doesn't adapt to mid-conversation language switches |

**Implementation Details**:
```javascript
function detectLanguage(text: string): 'en' | 'ur' {
  const arabicRegex = /[\u0600-\u06FF]/;
  const latinRegex = /[a-zA-Z]/;

  const arabicChars = (text.match(arabicRegex) || []).length;
  const latinChars = (text.match(latinRegex) || []).length;

  return arabicChars > latinChars ? 'ur' : 'en';
}
```

**References**:
- Unicode Standard: Arabic block U+0600–U+06FF
- MDN: String.prototype.match() for regex counting

---

## 2. Speech-to-Text API

### Decision: Web Speech API (Browser Native)

**Chosen**: Browser-native Web Speech API (SpeechRecognition interface)

**Rationale**:
- **Zero cost**: No backend proxy, no API subscription fees
- **Zero infrastructure**: No server components needed
- **Low latency**: <1s for interim results (streaming recognition)
- **Privacy**: Audio processed locally in browser (Chrome/Edge) or via browser vendor API
- **Urdu support**: Available via 'ur-PK' locale
- **Browser coverage**: 95%+ users (Chrome, Edge, Safari)

**Alternatives Considered**:

| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| Google Cloud Speech-to-Text | Highest accuracy (96%+ Urdu), best noise handling | $0.006/15sec, requires backend proxy, adds latency | Cost and complexity unjustified for MVP; Web Speech API meets 90%+ accuracy target |
| Azure Speech Services | Strong Urdu support, regional dialects | Requires backend + API key, competitive pricing | Same concerns as Google Cloud; infrastructure overhead |
| OpenAI Whisper API | Excellent multilingual (100+ languages) | $0.006/minute, slower transcription (non-streaming) | Non-streaming UX inferior for voice chat; cost accumulation |

**Implementation Details**:
```typescript
const recognition = new webkitSpeechRecognition(); // or SpeechRecognition
recognition.lang = detectedLanguage === 'ur' ? 'ur-PK' : 'en-US';
recognition.interimResults = true;
recognition.continuous = false;
recognition.maxAlternatives = 1;

recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
  displayTranscript(transcript); // Show for user verification
};
```

**Browser Compatibility**:
- Chrome 90+: Full support (desktop + mobile)
- Edge 90+: Full support
- Safari 14+: Supported (requires user permission)
- Firefox: ❌ Not supported (graceful degradation to text input)

**References**:
- MDN Web Speech API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API
- Can I Use: Web Speech API coverage 94.8% global users

---

## 3. Agent Skills Architecture

### Decision: Decorator Pattern with Registry Dictionary

**Chosen**: Python decorator (`@skill`) with centralized `SKILL_REGISTRY` dictionary

**Rationale**:
- **Simplicity**: Minimal boilerplate (~10 lines decorator implementation)
- **Pythonic**: Idiomatic pattern, familiar to Python developers
- **Type-safe**: Leverages Python type hints + Pydantic for contracts
- **Testable**: Skills are pure functions, easily mocked/tested
- **No framework overhead**: Zero external dependencies beyond Pydantic (already in stack)
- **Discovery**: Registry auto-populated at import time

**Alternatives Considered**:

| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| Plugin system (entry points, importlib) | Most flexible, hot-reloading | Complex discovery, fragile import paths, overkill for 4-6 skills | YAGNI - decorator pattern sufficient for static skill set |
| Microservices per skill (REST APIs) | Maximum isolation, language-agnostic | High overhead (networking, deployment), latency, operational complexity | Massive over-engineering for simple functions; violates simplicity principle |
| Class-based inheritance (BaseSkill ABC) | Traditional OOP, encapsulation | More boilerplate than decorators, less Pythonic | Decorator pattern achieves same goals with less code |

**Implementation Pattern**:
```python
from typing import Callable, Dict, Any
from pydantic import BaseModel

SKILL_REGISTRY: Dict[str, Dict[str, Any]] = {}

def skill(name: str, version: str):
    def decorator(func: Callable):
        SKILL_REGISTRY[name] = {
            'function': func,
            'version': version,
            'signature': func.__annotations__
        }
        return func
    return decorator

# Usage example
@skill(name="task_filtering", version="1.0.0")
def filter_tasks(tasks: List[Task], filters: FilterCriteria) -> List[Task]:
    """Filter tasks by status, date, priority."""
    return [t for t in tasks if meets_criteria(t, filters)]

# Invocation
skill_func = SKILL_REGISTRY['task_filtering']['function']
filtered = skill_func(tasks, filters)
```

**Skill Versioning**:
- Version stored in decorator parameter
- Future: Support `SKILL_REGISTRY[f"{name}:{version}"]` for multi-version coexistence
- MVP: Single version per skill name

**References**:
- Python Decorator Pattern: PEP 318
- Pydantic Models: https://docs.pydantic.dev/

---

## 4. Deployment Blueprint Secrets Management

### Decision: Cloud-Native Secrets Managers with Data Source References

**Chosen**: Terraform/CloudFormation data sources referencing AWS Secrets Manager, GCP Secret Manager, Azure Key Vault

**Rationale**:
- **Zero hardcoded secrets**: Blueprints never contain credentials
- **Cloud-native best practice**: Leverages platform-provided secrets management
- **Audit trail**: All secret access logged by cloud provider
- **Rotation support**: Secrets managers handle automatic rotation
- **Compliance**: Meets security audit requirements (SOC 2, ISO 27001)
- **IAM integration**: Fine-grained access control via cloud IAM

**Alternatives Considered**:

| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| Environment variables (.env.example) | Simple, universal | Secrets could leak in source control, manual rotation, no audit trail | High security risk; fails audit requirements |
| Encrypted secrets in blueprints (KMS/PGP) | Version-controlled, deployable | Decryption keys become new secret, hard to rotate, limited audit | Moves problem to key management; not cloud-native |
| Manual TODOs in generated files | Safest from leakage | Error-prone, breaks automation, poor DevOps UX | Defeats purpose of blueprint automation |

**Implementation Pattern**:

**AWS (Terraform)**:
```hcl
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "prod/database/password"
}

resource "aws_db_instance" "main" {
  password = data.aws_secretsmanager_secret_version.db_password.secret_string
  # ... other config
}
```

**GCP (Terraform)**:
```hcl
data "google_secret_manager_secret_version" "db_password" {
  secret = "db-password"
}

resource "google_sql_database_instance" "main" {
  settings {
    user_password = data.google_secret_manager_secret_version.db_password.secret_data
  }
}
```

**Azure (Terraform)**:
```hcl
data "azurerm_key_vault_secret" "db_password" {
  name         = "db-password"
  key_vault_id = azurerm_key_vault.main.id
}

resource "azurerm_mysql_server" "main" {
  administrator_login_password = data.azurerm_key_vault_secret.db_password.value
}
```

**Blueprint Documentation**:
- Include comments instructing operators to pre-populate secrets: `# Pre-create secret: aws secretsmanager create-secret --name prod/database/password`
- IAM policy examples for granting Lambda/Cloud Functions read access to secrets
- Rotation recommendations (30-90 days)

**References**:
- AWS Secrets Manager: https://aws.amazon.com/secrets-manager/
- GCP Secret Manager: https://cloud.google.com/secret-manager
- Azure Key Vault: https://azure.microsoft.com/en-us/services/key-vault/

---

## 5. Voice Input Language Selection

### Decision: Automatic Language Sync with Conversation Context

**Chosen**: Use current detected conversation language to set Web Speech API language parameter

**Rationale**:
- **Seamless UX**: No extra UI controls needed
- **Consistency**: Voice language matches text language automatically
- **Context-aware**: Adapts to mid-conversation language switches
- **Fail-safe default**: Falls back to English if no prior messages

**Alternatives Considered**:

| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| Manual language toggle button | Explicit user control | UI clutter, extra click, users forget to switch | Poor UX; defeats "automatic" detection goal |
| Attempt English first, retry Urdu if low confidence | Covers both languages | 2x recognition latency, poor UX during retry | User waits 6s instead of 3s; unacceptable |
| Browser locale preference | Simple implementation | Ignores conversation language, static | Doesn't adapt to user switching languages |

**Implementation Logic**:
```typescript
function getVoiceRecognitionLanguage(conversationHistory: Message[]): string {
  if (conversationHistory.length === 0) {
    return navigator.language.startsWith('ur') ? 'ur-PK' : 'en-US';
  }

  const lastMessage = conversationHistory[conversationHistory.length - 1];
  const detectedLang = detectLanguage(lastMessage.text);

  return detectedLang === 'ur' ? 'ur-PK' : 'en-US';
}

// Usage
recognition.lang = getVoiceRecognitionLanguage(messages);
```

**Edge Case Handling**:
- First voice input (no conversation history) → use browser locale or default 'en-US'
- User can manually override via language toggle if recognition incorrect
- Override persisted in localStorage for future sessions

**References**:
- Web Speech API lang property: https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition/lang

---

## 6. Internationalization (i18n) Library

### Decision: i18next for Frontend Translations

**Chosen**: i18next (React integration via react-i18next)

**Rationale**:
- **Industry standard**: Most popular i18n library (11k+ GitHub stars)
- **React integration**: First-class hooks (`useTranslation`, `Trans` component)
- **Namespace support**: Organize translations by feature
- **Pluralization**: Built-in support for language-specific plural rules
- **Lazy loading**: Load only needed translations
- **TypeScript support**: Type-safe translation keys

**Alternatives Considered**:

| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| react-intl (FormatJS) | Strong ICU message format, React-focused | More verbose syntax, heavier bundle | i18next more concise for simple translations |
| Custom solution (JSON + context) | Minimal dependencies | Reinvent wheel (pluralization, interpolation), no TypeScript support | YAGNI - i18next solves all requirements |
| Backend translations (API response) | Single source of truth | Latency, network dependency, complicates offline | Client-side UX requirement (instant language switch) |

**Translation Structure**:
```json
{
  "en": {
    "chat": {
      "placeholder": "Type a message...",
      "voiceButton": "Start voice input",
      "send": "Send"
    },
    "tasks": {
      "created": "Task created successfully",
      "deleted": "Task deleted",
      "error": "Failed to create task"
    }
  },
  "ur": {
    "chat": {
      "placeholder": "پیغام لکھیں...",
      "voiceButton": "صوتی ان پٹ شروع کریں",
      "send": "بھیجیں"
    },
    "tasks": {
      "created": "کام کامیابی سے بنایا گیا",
      "deleted": "کام حذف کیا گیا",
      "error": "کام بنانے میں ناکامی"
    }
  }
}
```

**Usage in React**:
```typescript
import { useTranslation } from 'react-i18next';

function ChatInput() {
  const { t } = useTranslation();

  return (
    <input placeholder={t('chat.placeholder')} />
  );
}
```

**References**:
- i18next: https://www.i18next.com/
- react-i18next: https://react.i18next.com/

---

## 7. Blueprint Template Engine

### Decision: Jinja2 for Infrastructure-as-Code Generation

**Chosen**: Jinja2 templating engine (Python)

**Rationale**:
- **Python native**: Already in backend stack (FastAPI)
- **Powerful syntax**: Loops, conditionals, filters, macros
- **Template inheritance**: Base templates for common patterns
- **HCL/YAML-friendly**: No syntax conflicts with Terraform/CloudFormation
- **Battle-tested**: Used by Ansible, Airflow, Flask

**Alternatives Considered**:

| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| Python f-strings / % formatting | No dependencies, simple | No template reuse, poor readability for large files | Not suitable for multi-file IaC generation |
| Terraform CDK | Type-safe, programmatic | Heavy dependency (Node.js), learning curve, generates JSON (not HCL) | Over-engineering; templates simpler for declarative IaC |
| Mustache | Logic-less, simple | Too limited (no conditionals, loops), multiple files per platform | Insufficient for complex blueprint logic |

**Template Example (AWS Lambda)**:
```jinja2
resource "aws_lambda_function" "{{ function_name }}" {
  function_name = "{{ function_name }}"
  runtime       = "{{ runtime }}"
  handler       = "{{ handler }}"
  role          = aws_iam_role.{{ function_name }}_role.arn

  environment {
    variables = {
      {% for key, value in env_vars.items() %}
      {{ key }} = "{{ value }}"
      {% endfor %}
    }
  }

  {% if secrets %}
  # Secrets sourced from AWS Secrets Manager
  # Pre-create secrets with: aws secretsmanager create-secret --name {{ secret_name }}
  {% for secret in secrets %}
  # - {{ secret.name }}: {{ secret.arn }}
  {% endfor %}
  {% endif %}
}
```

**References**:
- Jinja2 Documentation: https://jinja.palletsprojects.com/

---

## Summary of Research Decisions

| Component | Technology | Key Rationale |
|-----------|-----------|---------------|
| Language Detection | Unicode character-set analysis (client-side) | Instant (<50ms), offline, 98% accuracy, zero cost |
| Speech-to-Text | Web Speech API (browser native) | Zero cost, <3s latency, 95% browser coverage, Urdu support |
| Agent Skills | Python decorator + registry dict | Simple, Pythonic, type-safe, testable, zero framework |
| Blueprint Secrets | Cloud secrets manager data sources | Zero hardcoded credentials, audit trail, cloud-native best practice |
| Voice Language Selection | Auto-sync with conversation language | Seamless UX, context-aware, no extra UI |
| i18n Library | i18next + react-i18next | Industry standard, React hooks, TypeScript support |
| Blueprint Templates | Jinja2 | Python-native, powerful syntax, IaC-friendly |

**No unresolved NEEDS CLARIFICATION items remain.** All technology choices finalized and justified.
