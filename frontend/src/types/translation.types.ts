/**
 * Translation Type Definitions
 *
 * TypeScript types for i18next translations and language support
 */

export type Language = 'en' | 'ur' | 'ar' | 'zh' | 'tr';

export interface TranslationResources {
  en: Translation;
  ur: Translation;
  ar: Translation;
  zh: Translation;
  tr: Translation;
}

export interface Translation {
  chat: {
    placeholder: string;
    voiceButton: string;
    voiceButtonRecording: string;
    send: string;
    typing: string;
    listening: string;
  };
  tasks: {
    created: string;
    updated: string;
    deleted: string;
    completed: string;
    error: string;
    notFound: string;
    listEmpty: string;
  };
  errors: {
    generic: string;
    network: string;
    unauthorized: string;
    voiceNotSupported: string;
    voicePermissionDenied: string;
    voiceNoSpeech: string;
    voiceTimeout: string;
    languageDetectionFailed: string;
  };
  language: {
    en: string;
    ur: string;
    ar: string;
    zh: string;
    tr: string;
    separator: string;
  };
  voice: {
    startRecording: string;
    stopRecording: string;
    transcribing: string;
    transcriptPreview: string;
    confirm: string;
    cancel: string;
    edit: string;
    retryPrompt: string;
  };
}

/**
 * i18next module augmentation for type safety
 */
declare module 'i18next' {
  interface CustomTypeOptions {
    defaultNS: 'translation';
    resources: {
      translation: Translation;
    };
  }
}

/**
 * Language preference stored in localStorage
 */
export interface LanguagePreference {
  userId: string;
  preferredLanguage: Language;
  autoDetectEnabled: boolean;
  lastDetectedLanguage: Language;
  updatedAt: string; // ISO 8601 timestamp
}

/**
 * Language detection result
 */
export interface LanguageDetectionResult {
  language: Language;
  confidence: number; // 0.0 - 1.0
  arabicCharCount: number;
  latinCharCount: number;
}
