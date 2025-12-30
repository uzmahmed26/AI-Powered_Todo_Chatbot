"""
Translation service for multi-language support.

Uses OpenAI GPT-4 for high-quality translation between supported languages.
"""

import logging
from typing import Optional
from openai import AsyncOpenAI
from .detector import SupportedLanguage

logger = logging.getLogger(__name__)


class TranslationService:
    """Translation service using OpenAI GPT-4."""

    def __init__(self, openai_client: AsyncOpenAI):
        """
        Initialize translation service.

        Args:
            openai_client: Async OpenAI client
        """
        self.client = openai_client

    async def translate_to_english(
        self,
        text: str,
        source_lang: SupportedLanguage
    ) -> str:
        """
        Translate text to English.

        Args:
            text: Text to translate
            source_lang: Source language code

        Returns:
            Translated text in English
        """
        if source_lang == "en":
            return text

        try:
            lang_names = {
                "ur": "Urdu",
                "ar": "Arabic",
                "zh": "Chinese",
                "tr": "Turkish",
            }

            system_prompt = f"""You are a professional translator. Translate the following {lang_names[source_lang]} text to English.

Rules:
- Preserve the intent and meaning
- Maintain task-related terminology (todo, task, priority, category, etc.)
- Keep it natural and conversational
- Return ONLY the translated text, no explanations"""

            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.3,
            )

            translated = response.choices[0].message.content.strip()
            logger.info(f"Translated from {source_lang} to English: '{text[:50]}...' -> '{translated[:50]}...'")
            return translated

        except Exception as e:
            logger.error(f"Translation to English failed: {e}")
            # Fallback: return original text
            return text

    async def translate_from_english(
        self,
        text: str,
        target_lang: SupportedLanguage
    ) -> str:
        """
        Translate text from English to target language.

        Args:
            text: English text to translate
            target_lang: Target language code

        Returns:
            Translated text in target language
        """
        if target_lang == "en":
            return text

        try:
            lang_names = {
                "ur": "Urdu",
                "ar": "Arabic",
                "zh": "Chinese",
                "tr": "Turkish",
            }

            system_prompt = f"""You are a professional translator. Translate the following English text to {lang_names[target_lang]}.

Rules:
- Preserve the intent and meaning
- Maintain task-related terminology appropriately
- Keep it natural and conversational
- Use proper {lang_names[target_lang]} grammar and script
- Return ONLY the translated text, no explanations"""

            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.3,
            )

            translated = response.choices[0].message.content.strip()
            logger.info(f"Translated from English to {target_lang}: '{text[:50]}...' -> '{translated[:50]}...'")
            return translated

        except Exception as e:
            logger.error(f"Translation from English failed: {e}")
            # Fallback: return original text
            return text

    async def translate(
        self,
        text: str,
        source_lang: SupportedLanguage,
        target_lang: SupportedLanguage
    ) -> str:
        """
        Translate text between any two supported languages.

        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            Translated text

        Note:
            If source and target are the same, returns original text.
            Otherwise, translates via English as intermediate language.
        """
        if source_lang == target_lang:
            return text

        # If neither is English, translate via English
        if source_lang != "en" and target_lang != "en":
            english_text = await self.translate_to_english(text, source_lang)
            return await self.translate_from_english(english_text, target_lang)

        # Direct translation
        if source_lang != "en":
            return await self.translate_to_english(text, source_lang)
        else:
            return await self.translate_from_english(text, target_lang)
