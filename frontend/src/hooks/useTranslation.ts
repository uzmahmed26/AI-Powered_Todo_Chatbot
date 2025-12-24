/**
 * useTranslation Hook
 *
 * Convenient hook to access translation functionality in components.
 * Wraps the LanguageContext with a simple API.
 */

import { useContext } from 'react';
import { LanguageContext } from '../contexts/LanguageContext';
import type { TranslationContextValue } from '../types/translation';

/**
 * useTranslation Hook
 *
 * Provides translation functions and language state.
 *
 * @returns Translation context value
 *
 * @example
 * ```tsx
 * const { t, language, isRTL, toggleLanguage } = useTranslation();
 *
 * // Translate static UI text (from locale files)
 * <h1>{t('header.title')}</h1>
 *
 * // Translate dynamic text (chat messages)
 * const translatedMessage = await translateAsync(message.content);
 * ```
 */
export const useTranslation = (): TranslationContextValue => {
  const context = useContext(LanguageContext);

  if (!context) {
    throw new Error('useTranslation must be used within a LanguageProvider');
  }

  return context;
};

/**
 * Alias: `t` function for shorter syntax
 *
 * @example
 * ```tsx
 * import { t } from '../hooks/useTranslation';
 *
 * // Can be used outside React components for static translations
 * const errorMessage = t('errors.network');
 * ```
 */
export const t = (key: string): string => {
  // This is a static helper, not a hook
  // It can only return the key since we don't have context
  // Use the hook version inside components
  return key;
};
