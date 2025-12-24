/**
 * Language Toggle Component
 *
 * Displays a toggle button to switch between English (EN) and Urdu (UR).
 * Active language is highlighted with accent color.
 */

import React from 'react';
import { useTranslation } from '../hooks/useTranslation';
import type { Language } from '../types/translation';
import './LanguageToggle.css';

const LanguageToggle: React.FC = () => {
  const { language, setLanguage } = useTranslation();

  const handleLanguageChange = (lang: Language) => {
    setLanguage(lang);
  };

  return (
    <div className="language-toggle">
      <button
        className={`lang-option ${language === 'en' ? 'active' : ''}`}
        onClick={() => handleLanguageChange('en')}
        aria-label="Switch to English"
      >
        EN
      </button>
      <span className="lang-separator">|</span>
      <button
        className={`lang-option ${language === 'ur' ? 'active' : ''}`}
        onClick={() => handleLanguageChange('ur')}
        aria-label="Switch to Urdu"
      >
        UR
      </button>
    </div>
  );
};

export default LanguageToggle;
