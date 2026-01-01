/**
 * Language Detection Utilities
 * Feature: 006-bonus-features - Multi-language Support
 * 
 * Implements Unicode character-set analysis for language detection:
 * - Arabic script (U+0600-U+06FF) → Urdu
 * - Latin script → English
 * 
 * Provides localStorage-based language preference persistence.
 */

import type { 
  Language, 
  LanguageDetectionResult, 
  LanguagePreference 
} from '../types/translation.types';

/**
 * Unicode character ranges for language detection
 */
const UNICODE_RANGES = {
  // Arabic script (U+0600-U+06FF) - includes Urdu, Arabic, Persian
  ARABIC: { start: 0x0600, end: 0x06FF },
  
  // Latin script (U+0000-U+024F) - includes English and European languages
  LATIN: { start: 0x0000, end: 0x024F }
} as const;

/**
 * T018: Detect language based on Unicode character ranges
 * 
 * Uses character-set analysis to determine if text is English or Urdu.
 * Arabic script (U+0600-U+06FF) indicates Urdu.
 * Latin script indicates English.
 * 
 * @param text - Input text to analyze
 * @returns Language detection result with confidence score
 */
export function detectLanguage(text: string): LanguageDetectionResult {
  // Handle empty or whitespace-only strings
  if (!text || text.trim().length === 0) {
    return {
      language: 'en',
      confidence: 0,
      arabicCharCount: 0,
      latinCharCount: 0
    };
  }

  let arabicCharCount = 0;
  let latinCharCount = 0;

  // Count characters in each script
  for (const char of text) {
    const codePoint = char.codePointAt(0);
    
    if (!codePoint) continue;

    // Check if character is in Arabic range
    if (codePoint >= UNICODE_RANGES.ARABIC.start && 
        codePoint <= UNICODE_RANGES.ARABIC.end) {
      arabicCharCount++;
    }
    // Check if character is in Latin range (letters only, not punctuation)
    else if (codePoint >= 0x0041 && codePoint <= 0x007A) { // A-Z, a-z
      latinCharCount++;
    }
  }

  const totalChars = arabicCharCount + latinCharCount;

  // Default to English for neutral characters (numbers, punctuation, etc.)
  if (totalChars === 0) {
    return {
      language: 'en',
      confidence: 0,
      arabicCharCount,
      latinCharCount
    };
  }

  // Determine dominant language
  const language: Language = arabicCharCount > latinCharCount ? 'ur' : 'en';
  const confidence = totalChars > 0 
    ? Math.max(arabicCharCount, latinCharCount) / totalChars 
    : 0;

  return {
    language,
    confidence,
    arabicCharCount,
    latinCharCount
  };
}

/**
 * T019: Load language preference from localStorage
 * 
 * @param userId - User ID to load preference for
 * @returns Language preference or null if not found
 */
export function loadLanguagePreference(userId: string): LanguagePreference | null {
  try {
    const key = `language_pref_${userId}`;
    const stored = localStorage.getItem(key);
    
    if (!stored) {
      return null;
    }

    const parsed = JSON.parse(stored) as LanguagePreference;
    
    // Validate the parsed data has required fields
    if (!parsed.userId || !parsed.preferredLanguage) {
      return null;
    }

    return parsed;
  } catch (error) {
    // Handle corrupted or invalid JSON
    console.error('Failed to load language preference:', error);
    return null;
  }
}

/**
 * T020: Save language preference to localStorage
 * 
 * @param userId - User ID to save preference for
 * @param language - Preferred language
 * @param autoDetect - Whether auto-detection is enabled
 */
export function saveLanguagePreference(
  userId: string, 
  language: Language, 
  autoDetect: boolean
): void {
  const preference: LanguagePreference = {
    userId,
    preferredLanguage: language,
    autoDetectEnabled: autoDetect,
    lastDetectedLanguage: language,
    updatedAt: new Date().toISOString()
  };

  const key = `language_pref_${userId}`;
  localStorage.setItem(key, JSON.stringify(preference));
}

/**
 * T021: Get effective language for a message
 * 
 * Determines which language to use based on preferences and auto-detection.
 * - If auto-detection enabled: detect from message text
 * - If auto-detection disabled: use preferred language
 * - If no preferences: default to English
 * 
 * @param messageText - Current message text
 * @param preferences - User language preferences (null if not set)
 * @returns Effective language to use
 */
export function getEffectiveLanguage(
  messageText: string, 
  preferences: LanguagePreference | null
): Language {
  // No preferences: default to English
  if (!preferences) {
    return 'en';
  }

  // Auto-detection enabled: detect from message text
  if (preferences.autoDetectEnabled) {
    const detected = detectLanguage(messageText);
    return detected.language;
  }

  // Auto-detection disabled: use preferred language
  return preferences.preferredLanguage;
}
