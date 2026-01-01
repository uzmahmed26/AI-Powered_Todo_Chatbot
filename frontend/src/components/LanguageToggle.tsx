/**
 * Language Toggle Component
 * Feature: 006-bonus-features - Multi-language Support
 *
 * Provides a UI toggle to switch between English and Urdu languages.
 * Supports RTL layout for Urdu.
 */

import React from 'react';
import { useTranslation } from 'react-i18next';
import { useLanguage } from '../contexts/LanguageContext';
import type { Language } from '../types/translation.types';
import './LanguageToggle.css';

export const LanguageToggle: React.FC = () => {
  const { t } = useTranslation();
  const { language, setLanguage } = useLanguage();

  const toggleLanguage = () => {
    const newLanguage: Language = language === 'en' ? 'ur' : 'en';
    setLanguage(newLanguage);
  };

  return (
    <div className="language-toggle">
      <button
        className={`language-toggle__button ${language === 'en' ? 'active' : ''}`}
        onClick={() => setLanguage('en')}
        aria-label={t('language.english')}
      >
        EN
      </button>
      <button
        className={`language-toggle__button ${language === 'ur' ? 'active' : ''}`}
        onClick={() => setLanguage('ur')}
        aria-label={t('language.urdu')}
      >
        UR
      </button>
      <div
        className="language-toggle__slider"
        style={{
          transform: language === 'en' ? 'translateX(0)' : 'translateX(100%)'
        }}
      />
    </div>
  );
};
