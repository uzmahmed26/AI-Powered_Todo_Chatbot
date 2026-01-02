/**
 * Language Toggle Component
 * Feature: 006-bonus-features - Multi-language Support
 *
 * Provides a dropdown to switch between all supported languages:
 * English, Urdu, Arabic, Chinese, Turkish
 */

import React from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import type { Language } from '../types/translation.types';
import './LanguageToggle.css';

interface LanguageOption {
  code: Language;
  label: string;
  flag: string;
}

const languages: LanguageOption[] = [
  { code: 'en', label: 'English', flag: '🇬🇧' },
  { code: 'ur', label: 'اردو', flag: '🇵🇰' },
  { code: 'ar', label: 'العربية', flag: '🇸🇦' },
  { code: 'zh', label: '中文', flag: '🇨🇳' },
  { code: 'tr', label: 'Türkçe', flag: '🇹🇷' },
];

export const LanguageToggle: React.FC = () => {
  const { language, setLanguage } = useLanguage();

  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setLanguage(e.target.value as Language);
  };

  return (
    <div className="language-toggle">
      <select
        value={language}
        onChange={handleLanguageChange}
        className="language-toggle__select"
        aria-label="Select Language"
      >
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.flag} {lang.label}
          </option>
        ))}
      </select>
    </div>
  );
};
