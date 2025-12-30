# Multi-Language Support - Examples

## Supported Languages

- 🇬🇧 **English (en)** - Default
- 🇵🇰 **Urdu (ur)** - اردو
- 🇸🇦 **Arabic (ar)** - العربية
- 🇨🇳 **Chinese (zh)** - 中文
- 🇹🇷 **Turkish (tr)** - Türkçe

---

## How It Works

1. **Auto-Detection**: Language is automatically detected from user input
2. **Translation to English**: Commands are translated to English for processing
3. **Skill Execution**: All skills execute with English commands
4. **Response Translation**: Responses are translated back to user's language

---

## Example Commands

### English (en)
```
Add buy milk to my tasks
Show my pending tasks
Mark task 5 as complete
What are my high priority tasks?
```

### Urdu (ur) - اردو
```
دودھ خریدنے کا کام شامل کریں
میرے زیر التواء کام دکھائیں
کام نمبر 5 کو مکمل کے طور پر نشان زد کریں
میرے اہم کام کون سے ہیں؟
```

### Arabic (ar) - العربية
```
أضف شراء الحليب إلى مهامي
أظهر مهامي المعلقة
ضع علامة على المهمة 5 كمنجزة
ما هي مهامي ذات الأولوية العالية؟
```

### Chinese (zh) - 中文
```
添加买牛奶到我的任务
显示我的待办任务
将任务5标记为完成
我的高优先级任务是什么？
```

### Turkish (tr) - Türkçe
```
Görevlerime süt almayı ekle
Bekleyen görevlerimi göster
Görev 5'i tamamlandı olarak işaretle
Yüksek öncelikli görevlerim neler?
```

---

## API Response Format

```json
{
  "response": "✓ Added 'buy milk' to your tasks",
  "tool_calls": [...],
  "success": true,
  "detected_language": "en"
}
```

The `detected_language` field shows which language was detected.

---

## Language Detection Rules

### Chinese Detection
- Detects if >30% of characters are CJK (Chinese, Japanese, Korean)
- Priority: Highest (checked first)

### Arabic/Urdu Detection
- Detects if >40% of characters are Arabic script
- Differentiates Urdu by checking for Urdu-specific characters: ں ے ہ ڈ ٹ ڑ ژ

### Turkish Detection
- Detects if Turkish-specific characters are present: ğ ş ı ö ü ç

### English (Default)
- All other cases default to English

---

## Integration Steps

### 1. Install Dependencies
```bash
cd backend
# No additional dependencies needed - uses OpenAI for translation
```

### 2. Language Detection is Automatic
```python
from src.i18n.detector import LanguageDetector

# Auto-detect language
lang = LanguageDetector.detect("添加买牛奶")  # Returns: "zh"
```

### 3. Translation is Handled by Agent
```python
from src.agent.agent import TodoAgent

# Agent automatically:
# 1. Detects language
# 2. Translates to English
# 3. Executes skills
# 4. Translates response back

agent = TodoAgent(user_id="user123")
result = await agent.process_message("添加买牛奶")
# Response in Chinese: "✓ 已添加'买牛奶'到您的任务列表"
```

---

## Testing

### Test Language Detection
```python
from src.i18n.detector import LanguageDetector

# Test cases
assert LanguageDetector.detect("Add task") == "en"
assert LanguageDetector.detect("کام شامل کریں") == "ur"
assert LanguageDetector.detect("أضف مهمة") == "ar"
assert LanguageDetector.detect("添加任务") == "zh"
assert LanguageDetector.detect("Görev ekle") == "tr"
```

### Test Translation
```python
from src.i18n.translator import TranslationService
from src.agent.client import get_async_openai_client

client = get_async_openai_client()
translator = TranslationService(client)

# Translate to English
result = await translator.translate_to_english("添加买牛奶", "zh")
# Expected: "Add buy milk"

# Translate from English
result = await translator.translate_from_english("Task added successfully", "zh")
# Expected: "任务添加成功"
```

---

## Performance

- **Language Detection**: <1ms (heuristic-based)
- **Translation**: ~500-800ms (OpenAI GPT-4)
- **Total Overhead**: ~1 second per message (for non-English languages)

---

## Fallback Behavior

If translation fails:
- System logs the error
- Returns original text as fallback
- Continues processing (graceful degradation)

---

## Notes

- All skill execution happens in English (internal standard)
- Conversation history is stored in the original language
- Language is re-detected for each message (supports language switching mid-conversation)
