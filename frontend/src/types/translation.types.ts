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
  header: {
    title: string;
    subtitle: string;
    newChatButton: string;
    newChatTooltip: string;
  };
  welcome: {
    heading: string;
    emoji: string;
    intro: string;
    examples: string[];
  };
  input: {
    placeholder: string;
    sendButton: string;
    sendingButton: string;
    disabledTooltip: string;
  };
  footer: {
    conversationLabel: string;
    defaultMessage: string;
  };
  messages: {
    userAvatar: string;
    assistantAvatar: string;
    typingIndicator: string;
  };
  errors: {
    prefix: string;
    close: string;
    invalidRequest: string;
    permission: string;
    notFound: string;
    serviceUnavailable: string;
    timeout: string;
    generic: string;
    network: string;
    unexpected: string;
    sendFailed: string;
    requestSetupFailed: string;
    unauthorized?: string;
    voiceNotSupported?: string;
    voicePermissionDenied?: string;
    voiceNoSpeech?: string;
    voiceTimeout?: string;
    languageDetectionFailed?: string;
  };
  language: {
    en: string;
    ur: string;
    ar: string;
    zh: string;
    tr: string;
    separator: string;
  };
  home: {
    hero: {
      title: string;
      subtitle: string;
      description: string;
      getStarted: string;
      signIn: string;
      goToDashboard: string;
    };
    preview: {
      user1: string;
      assistant1: string;
      user2: string;
      assistant2: string;
    };
    features: {
      title: string;
      subtitle: string;
      naturalLanguage: {
        title: string;
        description: string;
      };
      multiLanguage: {
        title: string;
        description: string;
      };
      voiceInput: {
        title: string;
        description: string;
      };
      recurringTasks: {
        title: string;
        description: string;
      };
      smartSearch: {
        title: string;
        description: string;
      };
      aiPowered: {
        title: string;
        description: string;
      };
    };
    cta: {
      title: string;
      subtitle: string;
      button: string;
    };
    footer: {
      text: string;
    };
  };
  auth: {
    signin: {
      title: string;
      subtitle: string;
      signupLink: string;
      emailPlaceholder: string;
      passwordPlaceholder: string;
      submitButton: string;
      submittingButton: string;
      invalidCredentials: string;
    };
    signup: {
      title: string;
      subtitle: string;
      signinLink: string;
      fullNamePlaceholder: string;
      emailPlaceholder: string;
      passwordPlaceholder: string;
      confirmPasswordPlaceholder: string;
      submitButton: string;
      submittingButton: string;
      passwordMismatch: string;
      passwordTooShort: string;
      signupFailed: string;
    };
  };
  tasks: {
    search: {
      placeholder: string;
    };
    filter: {
      status: string;
      priority: string;
      category: string;
      all: string;
      pending: string;
      completed: string;
      high: string;
      medium: string;
      low: string;
    };
    sort: {
      label: string;
      dueDate: string;
      priority: string;
      title: string;
    };
    empty: {
      icon: string;
      title: string;
      description: string;
    };
    card: {
      complete: string;
      delete: string;
      recurring: string;
      due: string;
    };
    categories: {
      work: string;
      home: string;
      study: string;
      shopping: string;
      health: string;
      fitness: string;
      personal: string;
    };
    // Legacy fields for backwards compatibility
    created?: string;
    updated?: string;
    deleted?: string;
    error?: string;
    notFound?: string;
    listEmpty?: string;
  };
  chat?: {
    placeholder?: string;
    voiceButton?: string;
    voiceButtonRecording?: string;
    send?: string;
    typing?: string;
    listening?: string;
  };
  voice?: {
    startRecording?: string;
    stopRecording?: string;
    transcribing?: string;
    transcriptPreview?: string;
    confirm?: string;
    cancel?: string;
    edit?: string;
    retryPrompt?: string;
  };
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
