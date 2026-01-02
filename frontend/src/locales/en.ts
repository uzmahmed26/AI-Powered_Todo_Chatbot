/**
 * English Translations
 *
 * All UI text in English for the Smart Todo ChatKit application.
 * This serves as the source language for translations.
 */

export const translations = {
  header: {
    title: 'Smart Todo Assistant',
    subtitle: 'Chat naturally to manage your tasks',
    newChatButton: '+ New Chat',
    newChatTooltip: 'Start new conversation',
  },

  welcome: {
    heading: 'Welcome!',
    emoji: '👋',
    intro: "I'm your AI todo assistant. Try saying:",
    examples: [
      '"Add buy groceries to my tasks"',
      '"Remind me to call mom tomorrow"',
      '"Show my tasks"',
      '"Mark buy groceries as done"',
    ],
  },

  input: {
    placeholder: "Type a message... (e.g., 'Add buy milk')",
    sendButton: 'Send',
    sendingButton: '⏳',
    disabledTooltip: 'Enter a message to send',
  },

  footer: {
    conversationLabel: 'Conversation #',
    defaultMessage: 'Start a new conversation',
  },

  messages: {
    userAvatar: '👤',
    assistantAvatar: '🤖',
    typingIndicator: 'Typing...',
  },

  errors: {
    prefix: '⚠️',
    close: '✕',
    invalidRequest: 'Invalid request. Please check your input.',
    permission: "You don't have permission to access this conversation.",
    notFound: 'Resource not found.',
    serviceUnavailable: 'Service is currently unavailable. Please try again in a moment.',
    timeout: 'Request timed out. Please try again.',
    generic: 'An error occurred. Please try again.',
    network: 'Unable to reach the server. Please check your connection.',
    unexpected: 'An unexpected error occurred.',
    sendFailed: 'Failed to send message',
    requestSetupFailed: 'Failed to send request. Please try again.',
  },

  language: {
    en: 'EN',
    ur: 'UR',
    ar: 'AR',
    zh: 'ZH',
    tr: 'TR',
    separator: '|',
  },

  home: {
    hero: {
      title: 'Smart Todo Assistant',
      subtitle: 'Chat naturally with AI to manage your tasks effortlessly',
      description: "Your intelligent task manager powered by GPT-4. Just tell me what you need to do, and I'll help you organize, prioritize, and complete your tasks.",
      getStarted: 'Get Started - It\'s Free',
      signIn: 'Sign In',
      goToDashboard: 'Go to Dashboard →',
    },
    preview: {
      user1: 'Add buy groceries to my tasks',
      assistant1: 'Added \'buy groceries\' to your tasks!',
      user2: 'Show my tasks for today',
      assistant2: 'You have 3 tasks: buy groceries, call mom, finish report',
    },
    features: {
      title: 'Powerful Features',
      subtitle: 'Everything you need to stay organized',
      naturalLanguage: {
        title: 'Natural Language',
        description: 'Just talk naturally - no complex commands or buttons to click',
      },
      multiLanguage: {
        title: 'Multi-Language',
        description: 'Supports English, Urdu, Arabic, Chinese, and Turkish',
      },
      voiceInput: {
        title: 'Voice Input',
        description: 'Speak your tasks - hands-free task management',
      },
      recurringTasks: {
        title: 'Recurring Tasks',
        description: 'Set daily, weekly, or monthly repeating tasks',
      },
      smartSearch: {
        title: 'Smart Search',
        description: 'Find tasks instantly with powerful search and filters',
      },
      aiPowered: {
        title: 'AI-Powered',
        description: 'GPT-4 understands context and helps you stay organized',
      },
    },
    cta: {
      title: 'Ready to get organized?',
      subtitle: 'Join thousands of users managing their tasks with AI',
      button: 'Start Free Now →',
    },
    footer: {
      text: '© 2026 Smart Todo Assistant. Built with GPT-4 and ❤️',
    },
  },

  auth: {
    signin: {
      title: 'Sign in to your account',
      subtitle: "Don't have an account?",
      signupLink: 'Sign up',
      emailPlaceholder: 'Email address',
      passwordPlaceholder: 'Password',
      submitButton: 'Sign in',
      submittingButton: 'Signing in...',
      invalidCredentials: 'Invalid email or password',
    },
    signup: {
      title: 'Create your account',
      subtitle: 'Already have an account?',
      signinLink: 'Sign in',
      fullNamePlaceholder: 'Full name',
      emailPlaceholder: 'Email address',
      passwordPlaceholder: 'Password (min 8 characters)',
      confirmPasswordPlaceholder: 'Confirm password',
      submitButton: 'Sign up',
      submittingButton: 'Creating account...',
      passwordMismatch: 'Passwords do not match',
      passwordTooShort: 'Password must be at least 8 characters',
      signupFailed: 'Signup failed',
    },
  },

  tasks: {
    search: {
      placeholder: 'Search tasks...',
    },
    filter: {
      status: 'Status:',
      priority: 'Priority:',
      category: 'Category:',
      all: 'All',
      pending: 'Pending',
      completed: 'Completed',
      high: 'High',
      medium: 'Medium',
      low: 'Low',
    },
    sort: {
      label: 'Sort by:',
      dueDate: 'Due Date',
      priority: 'Priority',
      title: 'Title',
    },
    empty: {
      icon: '📝',
      title: 'No tasks found',
      description: 'Try adjusting your search or filters',
    },
    card: {
      complete: 'Complete',
      delete: 'Delete',
      recurring: 'Recurring',
      due: 'Due',
    },
    categories: {
      work: 'Work',
      home: 'Home',
      study: 'Study',
      shopping: 'Shopping',
      health: 'Health',
      fitness: 'Fitness',
      personal: 'Personal',
    },
  },
};
