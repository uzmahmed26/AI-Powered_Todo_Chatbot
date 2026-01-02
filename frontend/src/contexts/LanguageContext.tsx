/**
 * Language Context
 * Feature: 006-bonus-features - Multi-language Support
 * 
 * Provides i18next initialization and language switching functionality.
 * Manages language preferences with localStorage persistence.
 */

import React, { createContext, useContext, useEffect, useState } from 'react';
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import type { Language } from '../types/translation.types';

// Import translation files
import { translations as en } from '../locales/en';
import { translations as ur } from '../locales/ur';
import { translations as ar } from '../locales/ar';
import { translations as zh } from '../locales/zh';
import { translations as tr } from '../locales/tr';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  isRTL: boolean;
}

export const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

// Initialize i18next
i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      ur: { translation: ur },
      ar: { translation: ar },
      zh: { translation: zh },
      tr: { translation: tr }
    },
    fallbackLng: 'en',
    lng: localStorage.getItem('i18nextLng') || 'en',
    interpolation: {
      escapeValue: false // React already escapes
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
      lookupLocalStorage: 'i18nextLng'
    }
  });

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>(
    (localStorage.getItem('i18nextLng') as Language) || 'en'
  );

  // RTL languages: Arabic and Urdu
  const isRTLLanguage = (lang: Language) => lang === 'ur' || lang === 'ar';
  const [isRTL, setIsRTL] = useState(isRTLLanguage(language));

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    i18n.changeLanguage(lang);
    localStorage.setItem('i18nextLng', lang);

    // Update RTL direction for Arabic and Urdu
    const rtl = isRTLLanguage(lang);
    setIsRTL(rtl);
    document.documentElement.dir = rtl ? 'rtl' : 'ltr';
    document.documentElement.lang = lang;
  };

  // Set initial direction on mount
  useEffect(() => {
    const rtl = isRTLLanguage(language);
    document.documentElement.dir = rtl ? 'rtl' : 'ltr';
    document.documentElement.lang = language;
  }, [language]);

  return (
    <LanguageContext.Provider value={{ language, setLanguage, isRTL }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = (): LanguageContextType => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
