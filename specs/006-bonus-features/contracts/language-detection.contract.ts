/**
 * Language Detection Contract
 *
 * Client-side language detection using Unicode character-set analysis.
 * No backend API required - pure frontend implementation.
 */

export type Language = 'en' | 'ur';

export interface LanguageDetectionInput {
  text: string;
}

export interface LanguageDetectionOutput {
  language: Language;
  confidence: number; // 0.0 - 1.0
  arabicCharCount: number;
  latinCharCount: number;
}

export interface LanguagePreference {
  userId: string;
  preferredLanguage: Language;
  autoDetectEnabled: boolean;
  lastDetectedLanguage: Language;
  updatedAt: string; // ISO 8601
}

/**
 * Detects language from text using Unicode character ranges.
 *
 * @param text - Input text to analyze
 * @returns Detected language with confidence score
 *
 * @example
 * detectLanguage({ text: "Hello world" })
 * // => { language: 'en', confidence: 1.0, arabicCharCount: 0, latinCharCount: 10 }
 *
 * detectLanguage({ text: "مرحبا بك" })
 * // => { language: 'ur', confidence: 1.0, arabicCharCount: 8, latinCharCount: 0 }
 *
 * detectLanguage({ text: "Hello مرحبا" }) // Mixed
 * // => { language: 'ur', confidence: 0.8, arabicCharCount: 5, latinCharCount: 5 }
 */
export function detectLanguage(input: LanguageDetectionInput): LanguageDetectionOutput;

/**
 * Gets user's language preference from localStorage.
 *
 * @param userId - User identifier
 * @returns Language preference or null if not set
 */
export function getLanguagePreference(userId: string): LanguagePreference | null;

/**
 * Saves user's language preference to localStorage.
 *
 * @param preference - Language preference to save
 */
export function saveLanguagePreference(preference: LanguagePreference): void;

/**
 * Determines effective language considering auto-detection and user preference.
 *
 * @param userId - User identifier
 * @param inputText - Current user input text
 * @returns Effective language to use for response
 *
 * @logic
 * - If user has manual preference (autoDetectEnabled=false), use preferredLanguage
 * - If autoDetectEnabled=true, detect from inputText
 * - If inputText is empty, use lastDetectedLanguage from preference
 * - If no preference exists, default to 'en'
 */
export function getEffectiveLanguage(userId: string, inputText: string): Language;
