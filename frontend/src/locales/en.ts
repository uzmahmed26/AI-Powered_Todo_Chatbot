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

export type TranslationKeys = {
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
  };
  language: {
    en: string;
    ur: string;
    ar: string;
    zh: string;
    tr: string;
    separator: string;
  };
};
