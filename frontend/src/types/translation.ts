/**
 * Translation Type Definitions
 *
 * Defines types for the translation system including language codes,
 * cache structures, and translation service configuration.
 */

/**
 * Supported languages
 */
export type Language = 'en' | 'ur' | 'ar' | 'zh' | 'tr';

/**
 * Translation cache structure
 * Maps cache keys to translated strings
 *
 * Cache key format: `${targetLang}:${hashCode(text)}`
 * Example: "ur:h2f8a9d1" -> "ایک ٹاسک شامل کریں"
 */
export interface TranslationCache {
  [key: string]: string;
}

/**
 * Translation service configuration
 */
export interface TranslationServiceConfig {
  apiKey: string;
  projectId?: string;
  cacheEnabled: boolean;
  maxCacheSize: number; // in bytes
}

/**
 * Translation request payload for Google Translate API
 */
export interface TranslateRequest {
  q: string | string[]; // Text to translate (single or batch)
  target: Language; // Target language
  source: Language; // Source language
  format: 'text' | 'html';
}

/**
 * Translation response from Google Translate API
 */
export interface TranslateResponse {
  data: {
    translations: Array<{
      translatedText: string;
      detectedSourceLanguage?: string;
    }>;
  };
}

/**
 * Cache entry with metadata
 */
export interface CacheEntry {
  text: string;
  translation: string;
  timestamp: number;
  accessCount: number;
}

/**
 * Translation context value
 */
export interface TranslationContextValue {
  language: Language;
  setLanguage: (lang: Language) => void;
  isRTL: boolean;
  translate: (text: string) => string;
  translateAsync: (text: string) => Promise<string>;
  toggleLanguage: () => void;
  isLoading: boolean;
  getTranslations: () => any;
}
