/**
 * Language Detection Tests (TDD Red Phase)
 * Feature: 006-bonus-features - Multi-language Support
 * 
 * Tests cover:
 * - T013: English text detection
 * - T014: Urdu/Arabic script detection
 * - T015: Mixed-language dominant language detection
 * - T016: Auto-detection with preferences
 * - T017: Language preference persistence
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { 
  detectLanguage, 
  getEffectiveLanguage,
  saveLanguagePreference,
  loadLanguagePreference 
} from '../../src/utils/languageDetection';
import type { Language, LanguageDetectionResult } from '../../src/types/translation.types';

describe('Language Detection', () => {
  // Clean up localStorage before and after each test
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('detectLanguage', () => {
    // T013: English text detection
    it('should detect English text correctly', () => {
      const text = 'Hello world';
      const result: LanguageDetectionResult = detectLanguage(text);
      
      expect(result.language).toBe('en');
      expect(result.confidence).toBeGreaterThan(0.8);
      expect(result.latinCharCount).toBeGreaterThan(0);
      expect(result.arabicCharCount).toBe(0);
    });

    // T014: Urdu/Arabic script detection
    it('should detect Urdu/Arabic script text correctly', () => {
      const text = 'مرحبا'; // "Hello" in Arabic
      const result: LanguageDetectionResult = detectLanguage(text);
      
      expect(result.language).toBe('ur');
      expect(result.confidence).toBeGreaterThan(0.8);
      expect(result.arabicCharCount).toBeGreaterThan(0);
      expect(result.latinCharCount).toBe(0);
    });

    // T015: Mixed-language dominant language detection
    it('should detect dominant language in mixed-language text', () => {
      const text = 'Hello مرحبا مرحبا'; // More Arabic than English
      const result: LanguageDetectionResult = detectLanguage(text);
      
      expect(result.language).toBe('ur');
      expect(result.arabicCharCount).toBeGreaterThan(result.latinCharCount);
    });

    it('should handle empty strings gracefully', () => {
      const text = '';
      const result: LanguageDetectionResult = detectLanguage(text);
      
      expect(result.language).toBe('en'); // Default to English
      expect(result.confidence).toBe(0);
    });

    it('should handle whitespace-only strings', () => {
      const text = '   \n\t  ';
      const result: LanguageDetectionResult = detectLanguage(text);
      
      expect(result.language).toBe('en'); // Default to English
      expect(result.confidence).toBe(0);
    });

    it('should handle numbers and punctuation', () => {
      const text = '123 !@# 456';
      const result: LanguageDetectionResult = detectLanguage(text);
      
      expect(result.language).toBe('en'); // Default to English for neutral characters
    });
  });

  // T016: Auto-detection with preferences
  describe('getEffectiveLanguage', () => {
    it('should use auto-detected language when auto-detection is enabled', () => {
      const messageText = 'مرحبا بك'; // Arabic greeting
      const preferences = {
        userId: 'test-user-1',
        preferredLanguage: 'en' as Language,
        autoDetectEnabled: true,
        lastDetectedLanguage: 'en' as Language,
        updatedAt: new Date().toISOString()
      };

      const effectiveLanguage = getEffectiveLanguage(messageText, preferences);
      
      expect(effectiveLanguage).toBe('ur');
    });

    it('should use preferred language when auto-detection is disabled', () => {
      const messageText = 'مرحبا بك'; // Arabic text
      const preferences = {
        userId: 'test-user-2',
        preferredLanguage: 'en' as Language,
        autoDetectEnabled: false,
        lastDetectedLanguage: 'ur' as Language,
        updatedAt: new Date().toISOString()
      };

      const effectiveLanguage = getEffectiveLanguage(messageText, preferences);
      
      expect(effectiveLanguage).toBe('en'); // Should ignore detected language
    });

    it('should default to English when preferences are null', () => {
      const messageText = 'Hello world';
      const effectiveLanguage = getEffectiveLanguage(messageText, null);
      
      expect(effectiveLanguage).toBe('en');
    });
  });

  // T017: Language preference persistence
  describe('Language Preference Persistence', () => {
    it('should save language preference to localStorage', () => {
      const userId = 'test-user-persist';
      const language: Language = 'ur';
      const autoDetect = true;

      saveLanguagePreference(userId, language, autoDetect);

      const stored = localStorage.getItem(`language_pref_${userId}`);
      expect(stored).not.toBeNull();
      
      if (stored) {
        const parsed = JSON.parse(stored);
        expect(parsed.preferredLanguage).toBe('ur');
        expect(parsed.autoDetectEnabled).toBe(true);
        expect(parsed.userId).toBe(userId);
      }
    });

    it('should load language preference from localStorage', () => {
      const userId = 'test-user-load';
      const mockPreference = {
        userId,
        preferredLanguage: 'ur' as Language,
        autoDetectEnabled: false,
        lastDetectedLanguage: 'en' as Language,
        updatedAt: new Date().toISOString()
      };

      localStorage.setItem(`language_pref_${userId}`, JSON.stringify(mockPreference));

      const loaded = loadLanguagePreference(userId);
      
      expect(loaded).not.toBeNull();
      expect(loaded?.preferredLanguage).toBe('ur');
      expect(loaded?.autoDetectEnabled).toBe(false);
      expect(loaded?.userId).toBe(userId);
    });

    it('should return null when no preference exists in localStorage', () => {
      const userId = 'nonexistent-user';
      const loaded = loadLanguagePreference(userId);
      
      expect(loaded).toBeNull();
    });

    it('should handle corrupted localStorage data gracefully', () => {
      const userId = 'corrupted-user';
      localStorage.setItem(`language_pref_${userId}`, 'invalid-json-{{{');

      const loaded = loadLanguagePreference(userId);
      
      expect(loaded).toBeNull();
    });

    it('should update lastDetectedLanguage when saving new preference', () => {
      const userId = 'test-user-update';
      
      saveLanguagePreference(userId, 'en', true);
      let loaded = loadLanguagePreference(userId);
      expect(loaded?.preferredLanguage).toBe('en');

      saveLanguagePreference(userId, 'ur', true);
      loaded = loadLanguagePreference(userId);
      expect(loaded?.preferredLanguage).toBe('ur');
      expect(loaded?.lastDetectedLanguage).toBe('ur');
    });
  });
});
