"""
Language detection module.

Auto-detects language from user input using character-based heuristics
and pattern matching. Supports: English, Urdu, Arabic, Chinese, Turkish.
"""

import re
import logging
from typing import Literal

logger = logging.getLogger(__name__)

SupportedLanguage = Literal["en", "ur", "ar", "zh", "tr"]


class LanguageDetector:
    """Detect language from text using character-based heuristics."""

    # Unicode ranges for different scripts
    ARABIC_RANGE = (0x0600, 0x06FF)  # Arabic script
    URDU_RANGE = (0x0600, 0x06FF)    # Same as Arabic (Urdu uses Arabic script)
    CHINESE_RANGE = (0x4E00, 0x9FFF)  # CJK Unified Ideographs
    TURKISH_SPECIAL = ["ğ", "ş", "ı", "ö", "ü", "ç", "Ğ", "Ş", "İ", "Ö", "Ü", "Ç"]

    # Urdu-specific characters (not in standard Arabic)
    URDU_SPECIFIC = [
        "ں", "ے", "ہ", "ڈ", "ٹ", "ڑ", "ژ"  # Nun Ghunna, Yeh Barree, etc.
    ]

    @classmethod
    def detect(cls, text: str) -> SupportedLanguage:
        """
        Detect language from text.

        Args:
            text: Input text

        Returns:
            Language code (en, ur, ar, zh, tr)

        Algorithm:
        1. Check for Chinese characters (highest priority)
        2. Check for Arabic/Urdu script
        3. Check for Turkish special characters
        4. Default to English
        """
        if not text or not text.strip():
            return "en"

        text = text.strip()

        # Count character types
        chinese_count = sum(1 for char in text if cls._is_chinese(char))
        arabic_count = sum(1 for char in text if cls._is_arabic(char))
        urdu_specific_count = sum(1 for char in text if char in cls.URDU_SPECIFIC)
        turkish_count = sum(1 for char in text if char in cls.TURKISH_SPECIAL)

        total_chars = len(text)

        # 1. Chinese: If >30% of characters are Chinese
        if chinese_count > 0 and (chinese_count / total_chars) > 0.3:
            logger.info(f"Detected language: Chinese (zh) - {chinese_count}/{total_chars} Chinese chars")
            return "zh"

        # 2. Arabic/Urdu: If >40% of characters are Arabic script
        if arabic_count > 0 and (arabic_count / total_chars) > 0.4:
            # Differentiate between Urdu and Arabic
            if urdu_specific_count > 0:
                logger.info(f"Detected language: Urdu (ur) - {urdu_specific_count} Urdu-specific chars")
                return "ur"
            else:
                logger.info(f"Detected language: Arabic (ar) - {arabic_count}/{total_chars} Arabic chars")
                return "ar"

        # 3. Turkish: If Turkish special characters are present
        if turkish_count > 0:
            logger.info(f"Detected language: Turkish (tr) - {turkish_count} Turkish chars")
            return "tr"

        # 4. Default: English
        logger.info("Detected language: English (en) - default")
        return "en"

    @staticmethod
    def _is_chinese(char: str) -> bool:
        """Check if character is Chinese (CJK)."""
        code = ord(char)
        return LanguageDetector.CHINESE_RANGE[0] <= code <= LanguageDetector.CHINESE_RANGE[1]

    @staticmethod
    def _is_arabic(char: str) -> bool:
        """Check if character is Arabic script (includes Urdu)."""
        code = ord(char)
        return LanguageDetector.ARABIC_RANGE[0] <= code <= LanguageDetector.ARABIC_RANGE[1]

    @staticmethod
    def get_language_name(code: SupportedLanguage) -> str:
        """Get language name from code."""
        names = {
            "en": "English",
            "ur": "Urdu (اردو)",
            "ar": "Arabic (العربية)",
            "zh": "Chinese (中文)",
            "tr": "Turkish (Türkçe)",
        }
        return names.get(code, "English")
