"""
Internationalization (i18n) module for multi-language support.

Supports: English, Urdu, Arabic, Chinese, Turkish
"""

from .detector import LanguageDetector
from .translator import TranslationService

__all__ = ["LanguageDetector", "TranslationService"]
