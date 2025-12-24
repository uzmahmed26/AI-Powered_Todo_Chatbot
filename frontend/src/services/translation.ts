/**
 * Translation Service
 *
 * Centralized translation service using Google Translate API with two-layer caching:
 * 1. In-memory session cache (fast, cleared on refresh)
 * 2. localStorage persistent cache (survives refresh, 5MB limit)
 */

import axios from 'axios';
import type { Language, TranslationCache, TranslateResponse } from '../types/translation';

// Google Translate API configuration
const GOOGLE_TRANSLATE_API_URL = 'https://translation.googleapis.com/language/translate/v2';
const CACHE_KEY_PREFIX = 'translation_cache_v1';
const MAX_CACHE_SIZE = 5 * 1024 * 1024; // 5MB in bytes

/**
 * In-memory session cache
 * Fast access, cleared on page refresh
 */
const sessionCache = new Map<string, string>();

/**
 * Generate hash code for string
 * Used for cache keys to keep them short
 */
const hashCode = (str: string): string => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash).toString(36);
};

/**
 * Generate cache key
 */
const getCacheKey = (text: string, targetLang: Language): string => {
  return `${targetLang}:${hashCode(text)}`;
};

/**
 * Get cached translation from localStorage
 */
export const getCachedTranslation = (text: string, lang: Language): string | null => {
  // Check session cache first (fastest)
  const sessionKey = getCacheKey(text, lang);
  if (sessionCache.has(sessionKey)) {
    return sessionCache.get(sessionKey)!;
  }

  // Check localStorage (persistent)
  try {
    const cacheData = localStorage.getItem(CACHE_KEY_PREFIX);
    if (cacheData) {
      const cache: TranslationCache = JSON.parse(cacheData);
      if (cache[sessionKey]) {
        // Add to session cache for faster future access
        sessionCache.set(sessionKey, cache[sessionKey]);
        return cache[sessionKey];
      }
    }
  } catch (error) {
    console.warn('[Translation] Failed to read cache:', error);
  }

  return null;
};

/**
 * Set cached translation in both layers
 */
export const setCachedTranslation = (text: string, lang: Language, translation: string): void => {
  const cacheKey = getCacheKey(text, lang);

  // Add to session cache
  sessionCache.set(cacheKey, translation);

  // Add to localStorage
  try {
    const cacheData = localStorage.getItem(CACHE_KEY_PREFIX);
    const cache: TranslationCache = cacheData ? JSON.parse(cacheData) : {};

    cache[cacheKey] = translation;

    // Check cache size and evict if needed
    const cacheString = JSON.stringify(cache);
    if (cacheString.length > MAX_CACHE_SIZE) {
      // Simple LRU: keep only recent 50% of entries
      const entries = Object.entries(cache);
      const halfLength = Math.floor(entries.length / 2);
      const newCache = Object.fromEntries(entries.slice(-halfLength));
      localStorage.setItem(CACHE_KEY_PREFIX, JSON.stringify(newCache));
    } else {
      localStorage.setItem(CACHE_KEY_PREFIX, cacheString);
    }
  } catch (error) {
    console.warn('[Translation] Failed to write cache:', error);
  }
};

/**
 * Clear all translation caches
 */
export const clearCache = (): void => {
  sessionCache.clear();
  try {
    localStorage.removeItem(CACHE_KEY_PREFIX);
  } catch (error) {
    console.warn('[Translation] Failed to clear cache:', error);
  }
};

/**
 * Translate text using Google Translate API
 *
 * @param text - Text to translate
 * @param targetLang - Target language ('en' or 'ur')
 * @returns Translated text
 */
export const translateText = async (text: string, targetLang: Language): Promise<string> => {
  // If target is English or text is empty, return original
  if (targetLang === 'en' || !text.trim()) {
    return text;
  }

  // Check cache first
  const cached = getCachedTranslation(text, targetLang);
  if (cached) {
    return cached;
  }

  // Get API key from environment
  const apiKey = import.meta.env.VITE_GOOGLE_TRANSLATE_API_KEY;

  if (!apiKey) {
    console.warn('[Translation] Google Translate API key not configured. Returning original text.');
    return text; // Fallback to original text
  }

  try {
    // Call Google Translate API
    const response = await axios.post<TranslateResponse>(
      GOOGLE_TRANSLATE_API_URL,
      {
        q: text,
        target: targetLang,
        source: 'en',
        format: 'text',
      },
      {
        params: { key: apiKey },
        timeout: 10000, // 10 second timeout
      }
    );

    const translatedText = response.data.data.translations[0].translatedText;

    // Cache the translation
    setCachedTranslation(text, targetLang, translatedText);

    return translatedText;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('[Translation] API error:', error.response?.data || error.message);
    } else {
      console.error('[Translation] Unknown error:', error);
    }

    // Fallback to original text on error
    return text;
  }
};

/**
 * Translate multiple texts in batch
 *
 * @param texts - Array of texts to translate
 * @param targetLang - Target language
 * @returns Array of translated texts
 */
export const translateBatch = async (texts: string[], targetLang: Language): Promise<string[]> => {
  // If target is English, return originals
  if (targetLang === 'en') {
    return texts;
  }

  // Get API key
  const apiKey = import.meta.env.VITE_GOOGLE_TRANSLATE_API_KEY;

  if (!apiKey) {
    console.warn('[Translation] Google Translate API key not configured. Returning original texts.');
    return texts;
  }

  // Check cache for all texts
  const results: string[] = [];
  const uncachedIndices: number[] = [];
  const uncachedTexts: string[] = [];

  texts.forEach((text, index) => {
    const cached = getCachedTranslation(text, targetLang);
    if (cached) {
      results[index] = cached;
    } else {
      results[index] = ''; // Placeholder
      uncachedIndices.push(index);
      uncachedTexts.push(text);
    }
  });

  // If all cached, return immediately
  if (uncachedTexts.length === 0) {
    return results;
  }

  try {
    // Call Google Translate API with batch
    const response = await axios.post<TranslateResponse>(
      GOOGLE_TRANSLATE_API_URL,
      {
        q: uncachedTexts,
        target: targetLang,
        source: 'en',
        format: 'text',
      },
      {
        params: { key: apiKey },
        timeout: 15000, // 15 second timeout for batch
      }
    );

    const translations = response.data.data.translations;

    // Cache and insert translations
    translations.forEach((translation, i) => {
      const originalIndex = uncachedIndices[i];
      const translatedText = translation.translatedText;

      results[originalIndex] = translatedText;
      setCachedTranslation(uncachedTexts[i], targetLang, translatedText);
    });

    return results;
  } catch (error) {
    console.error('[Translation] Batch translation error:', error);

    // Fill uncached with originals on error
    uncachedIndices.forEach((index, i) => {
      results[index] = uncachedTexts[i];
    });

    return results;
  }
};

/**
 * Get cache statistics
 */
export const getCacheStats = (): {
  sessionCacheSize: number;
  localStorageCacheSize: number;
  totalEntries: number;
} => {
  let localStorageCacheSize = 0;
  let totalEntries = 0;

  try {
    const cacheData = localStorage.getItem(CACHE_KEY_PREFIX);
    if (cacheData) {
      localStorageCacheSize = new Blob([cacheData]).size;
      totalEntries = Object.keys(JSON.parse(cacheData)).length;
    }
  } catch (error) {
    console.warn('[Translation] Failed to get cache stats:', error);
  }

  return {
    sessionCacheSize: sessionCache.size,
    localStorageCacheSize,
    totalEntries,
  };
};
