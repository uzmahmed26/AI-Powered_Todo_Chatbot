/**
 * Language Context
 *
 * Global language state management with localStorage persistence.
 * Provides language preference, RTL state, and translation functions.
 */

import React, { createContext, useState, useEffect, useCallback } from 'react';
import type { Language, TranslationContextValue } from '../types/translation';
import { translateText } from '../services/translation';
import { isRTLLanguage, applyRTL } from '../utils/rtl';
import { translations as enTranslations } from '../locales/en';
import { translations as urTranslations } from '../locales/ur';

const LANGUAGE_STORAGE_KEY = 'app_language';
const DEFAULT_LANGUAGE: Language = 'en';

/**
 * Language Context
 */
export const LanguageContext = createContext<TranslationContextValue | undefined>(undefined);

/**
 * Language Provider Props
 */
interface LanguageProviderProps {
  children: React.ReactNode;
}

/**
 * Language Provider Component
 *
 * Wraps the application to provide language state and translation functions.
 */
export const LanguageProvider: React.FC<LanguageProviderProps> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>(DEFAULT_LANGUAGE);
  const [isLoading, setIsLoading] = useState(false);

  /**
   * Load language preference from localStorage on mount
   */
  useEffect(() => {
    try {
      const savedLanguage = localStorage.getItem(LANGUAGE_STORAGE_KEY) as Language;
      if (savedLanguage === 'en' || savedLanguage === 'ur') {
        setLanguageState(savedLanguage);
      }
    } catch (error) {
      console.warn('[LanguageContext] Failed to load language preference:', error);
    }
  }, []);

  /**
   * Apply RTL direction when language changes
   */
  useEffect(() => {
    const isRTL = isRTLLanguage(language);
    applyRTL(isRTL);
  }, [language]);

  /**
   * Set language and persist to localStorage
   */
  const setLanguage = useCallback((lang: Language) => {
    setLanguageState(lang);
    try {
      localStorage.setItem(LANGUAGE_STORAGE_KEY, lang);
    } catch (error) {
      console.warn('[LanguageContext] Failed to save language preference:', error);
    }
  }, []);

  /**
   * Toggle between EN and UR
   */
  const toggleLanguage = useCallback(() => {
    setLanguage(language === 'en' ? 'ur' : 'en');
  }, [language, setLanguage]);

  /**
   * Synchronous translate function
   * Returns translation from locale files based on current language
   */
  const translate = useCallback(
    (text: string): string => {
      // Return the text as-is since we're now using locale files directly
      // The component should pass the text from the appropriate locale file
      return text;
    },
    []
  );

  /**
   * Get translations object for current language
   */
  const getTranslations = useCallback(() => {
    return language === 'ur' ? urTranslations : enTranslations;
  }, [language]);

  /**
   * Asynchronous translate function
   * Uses Google Translate API with caching for dynamic content (chat messages)
   */
  const translateAsync = useCallback(
    async (text: string): Promise<string> => {
      // For dynamic text (chat messages), use translation service
      if (language === 'en') {
        return text; // No translation needed for English
      }

      setIsLoading(true);
      try {
        const translated = await translateText(text, language);
        return translated;
      } catch (error) {
        console.error('[LanguageContext] Translation failed:', error);
        return text; // Fallback to original
      } finally {
        setIsLoading(false);
      }
    },
    [language]
  );

  /**
   * Compute RTL state
   */
  const isRTL = isRTLLanguage(language);

  /**
   * Context value
   */
  const value: TranslationContextValue = {
    language,
    setLanguage,
    isRTL,
    translate,
    translateAsync,
    toggleLanguage,
    isLoading,
    getTranslations,
  };

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
};
