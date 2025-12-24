/**
 * RTL (Right-to-Left) Utilities
 *
 * Utilities for managing text direction and RTL layout for languages like Urdu.
 */

import type { Language } from '../types/translation';

/**
 * Check if a language is RTL
 */
export const isRTLLanguage = (language: Language): boolean => {
  const rtlLanguages: Language[] = ['ur'];
  return rtlLanguages.includes(language);
};

/**
 * Apply RTL direction to document
 *
 * @param isRTL - Whether to apply RTL direction
 */
export const applyRTL = (isRTL: boolean): void => {
  const dir = isRTL ? 'rtl' : 'ltr';
  document.documentElement.setAttribute('dir', dir);
  document.documentElement.setAttribute('lang', isRTL ? 'ur' : 'en');
};

/**
 * Get RTL class name
 *
 * @param isRTL - Whether RTL is active
 * @returns RTL class name or empty string
 */
export const getRTLClass = (isRTL: boolean): string => {
  return isRTL ? 'rtl' : '';
};

/**
 * Get text alignment based on RTL
 *
 * @param isRTL - Whether RTL is active
 * @returns 'right' or 'left'
 */
export const getTextAlign = (isRTL: boolean): 'left' | 'right' => {
  return isRTL ? 'right' : 'left';
};

/**
 * Get flex direction based on RTL
 *
 * @param isRTL - Whether RTL is active
 * @returns 'row-reverse' or 'row'
 */
export const getFlexDirection = (isRTL: boolean): 'row' | 'row-reverse' => {
  return isRTL ? 'row-reverse' : 'row';
};
