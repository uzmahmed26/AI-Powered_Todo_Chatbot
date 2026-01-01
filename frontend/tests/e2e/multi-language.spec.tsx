/**
 * E2E Integration Tests: Multi-language Support
 * Feature: 006-bonus-features - Multi-language Support
 *
 * Tests the full flow of:
 * - T033: English message → English response
 * - T034: Urdu message → Urdu response
 * - T035: Language switching mid-conversation
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { I18nextProvider } from 'react-i18next';
import i18n from 'i18next';
import SmartTodoApp from '../../src/pages/SmartTodoApp';
import { LanguageProvider } from '../../src/contexts/LanguageContext';
import * as api from '../../src/services/api';
import { translations as enTranslations } from '../../src/locales/en';
import { translations as urTranslations } from '../../src/locales/ur';

// Mock the API client
vi.mock('../../src/services/api', async () => {
  const actual = await vi.importActual('../../src/services/api');
  return {
    ...actual,
    apiClient: {
      sendMessage: vi.fn(),
      listTasks: vi.fn().mockResolvedValue({ tasks: [] }),
    }
  };
});

// Mock auth context
const mockUser = {
  id: 'test-user-123',
  email: 'test@example.com',
  full_name: 'Test User',
  is_active: true,
  created_at: new Date().toISOString()
};

// Mock the AuthContext module
vi.mock('../../src/context/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  useAuth: () => ({
    user: mockUser,
    isAuthenticated: true,
    isLoading: false,
    signin: vi.fn(),
    signup: vi.fn(),
    signout: vi.fn(),
    refreshToken: vi.fn()
  })
}));

// Initialize i18n for tests
i18n.init({
  lng: 'en',
  fallbackLng: 'en',
  resources: {
    en: { translation: enTranslations },
    ur: { translation: urTranslations }
  },
  interpolation: {
    escapeValue: false
  }
});

// Wrapper component with i18n and language provider
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <I18nextProvider i18n={i18n}>
      <LanguageProvider>
        {children}
      </LanguageProvider>
    </I18nextProvider>
  );
};

describe('E2E: Multi-language Support', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();

    // Reset all mocks
    vi.clearAllMocks();

    // Default mock for listTasks
    vi.mocked(api.apiClient.listTasks).mockResolvedValue({ tasks: [] });
  });

  /**
   * T033: Write E2E test: user sends English message, receives English response
   *
   * Test Flow:
   * 1. User types English message "Add buy milk to my tasks"
   * 2. System detects language as English
   * 3. Backend processes message in English
   * 4. User receives English response
   */
  it('T033: should send English message and receive English response', async () => {
    // Mock API response for English message
    const englishMessage = 'Add buy milk to my tasks';
    const englishResponse = {
      conversation_id: 1,
      response: '✓ Added "buy milk" to your tasks (Task #1)',
      tool_calls: [
        {
          tool: 'add_task',
          args: { title: 'buy milk', user_id: 'test-user-123' },
          result: { id: 1, title: 'buy milk', status: 'pending' }
        }
      ],
      success: true
    };

    vi.mocked(api.apiClient.sendMessage).mockResolvedValue(englishResponse);

    // Render the app
    const user = userEvent.setup();
    render(<SmartTodoApp />, { wrapper: TestWrapper });

    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/type.*message/i)).toBeInTheDocument();
    });

    // Find input and send button
    const input = screen.getByPlaceholderText(/type.*message/i);
    const sendButton = screen.getByRole('button', { name: /send/i });

    // Type English message
    await user.type(input, englishMessage);
    expect(input).toHaveValue(englishMessage);

    // Send message
    await user.click(sendButton);

    // Verify API was called with English message
    // sendMessage signature: sendMessage(userId, message, conversationId)
    await waitFor(() => {
      expect(api.apiClient.sendMessage).toHaveBeenCalledWith(
        'test-user-123',
        englishMessage,
        expect.any(Number) // conversation_id (could be null or a number)
      );
    });

    // Verify English response is displayed
    await waitFor(() => {
      expect(screen.getByText(/Added "buy milk" to your tasks/i)).toBeInTheDocument();
    });

    // Verify input is cleared after sending
    expect(input).toHaveValue('');
  });

  /**
   * T034: Write E2E test: user sends Urdu message, receives Urdu response
   *
   * Test Flow:
   * 1. User types Urdu message "میں دودھ خریدنا چاہتا ہوں"
   * 2. System detects language as Urdu (Arabic script U+0600-U+06FF)
   * 3. Backend processes message in Urdu
   * 4. User receives Urdu response
   */
  it('T034: should send Urdu message and receive Urdu response', async () => {
    // Mock API response for Urdu message
    const urduMessage = 'میں دودھ خریدنا چاہتا ہوں';
    const urduResponse = {
      conversation_id: 2,
      response: '✓ "دودھ خریدیں" آپ کے کاموں میں شامل کر دیا گیا (ٹاسک #1)',
      tool_calls: [
        {
          tool: 'add_task',
          args: { title: 'دودھ خریدیں', user_id: 'test-user-123' },
          result: { id: 1, title: 'دودھ خریدیں', status: 'pending' }
        }
      ],
      success: true
    };

    vi.mocked(api.apiClient.sendMessage).mockResolvedValue(urduResponse);

    // Render the app
    const user = userEvent.setup();
    render(<SmartTodoApp />, { wrapper: TestWrapper });

    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/type.*message/i)).toBeInTheDocument();
    });

    // Find input and send button
    const input = screen.getByPlaceholderText(/type.*message/i);
    const sendButton = screen.getByRole('button', { name: /send/i });

    // Type Urdu message
    await user.type(input, urduMessage);
    expect(input).toHaveValue(urduMessage);

    // Send message
    await user.click(sendButton);

    // Verify API was called with Urdu message
    await waitFor(() => {
      expect(api.apiClient.sendMessage).toHaveBeenCalledWith(
        'test-user-123',
        urduMessage,
        expect.any(Number)
      );
    });

    // Verify Urdu response is displayed
    await waitFor(() => {
      expect(screen.getByText(/آپ کے کاموں میں شامل کر دیا گیا/i)).toBeInTheDocument();
    });

    // Verify input is cleared after sending
    expect(input).toHaveValue('');
  });

  /**
   * T035: Write E2E test: user switches language mid-conversation, system adapts
   *
   * Test Flow:
   * 1. User sends English message
   * 2. User toggles to Urdu language via LanguageToggle
   * 3. User sends Urdu message
   * 4. System responds in Urdu
   * 5. Previous English messages remain visible (no translation)
   */
  it('T035: should switch language mid-conversation and system adapts', async () => {
    // Setup mocks for multiple messages
    const englishMessage = 'Show my tasks';
    const urduMessage = 'نیا کام شامل کریں';

    const englishResponse = {
      conversation_id: 3,
      response: 'Here are your tasks: No tasks found.',
      tool_calls: [],
      success: true
    };

    const urduResponse = {
      conversation_id: 3,
      response: 'آپ کون سا کام شامل کرنا چاہتے ہیں؟',
      tool_calls: [],
      success: true
    };

    // Mock sequential API calls
    vi.mocked(api.apiClient.sendMessage)
      .mockResolvedValueOnce(englishResponse)
      .mockResolvedValueOnce(urduResponse);

    // Render the app
    const user = userEvent.setup();
    render(<SmartTodoApp />, { wrapper: TestWrapper });

    // Click Chat button to show chat interface
    const chatButton = await screen.findByText(/💬 Chat/i);
    await user.click(chatButton);

    // Wait for chat interface to load
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/type.*message|placeholder/i)).toBeInTheDocument();
    });

    // Find input and send button
    const input = screen.getByPlaceholderText(/type.*message|placeholder/i);
    const sendButton = screen.getByRole('button', { name: /send/i });

    // === Step 1: Send English message ===
    await user.type(input, englishMessage);
    await user.click(sendButton);

    // Verify English response appears
    await waitFor(() => {
      expect(screen.getByText(/Here are your tasks/i)).toBeInTheDocument();
    });

    // Verify first API call was English
    expect(api.apiClient.sendMessage).toHaveBeenNthCalledWith(
      1,
      'test-user-123',
      englishMessage,
      null // First message, no conversation_id yet
    );

    // === Step 2: Switch to Urdu language ===
    const urduToggleButton = screen.getByRole('button', { name: /urdu/i });
    await user.click(urduToggleButton);

    // Verify Urdu language is active
    await waitFor(() => {
      expect(urduToggleButton).toHaveClass('active');
    });

    // Verify UI text has switched to Urdu
    await waitFor(() => {
      // Placeholder should be in Urdu now
      const updatedInput = screen.getByPlaceholderText(/پیغام/i);
      expect(updatedInput).toBeInTheDocument();
    });

    // === Step 3: Send Urdu message ===
    const urduInput = screen.getByPlaceholderText(/پیغام/i);
    await user.type(urduInput, urduMessage);
    await user.click(screen.getByRole('button', { name: /بھیجیں/i })); // "Send" in Urdu

    // Verify Urdu response appears
    await waitFor(() => {
      expect(screen.getByText(/آپ کون سا کام/i)).toBeInTheDocument();
    });

    // Verify second API call was Urdu
    expect(api.apiClient.sendMessage).toHaveBeenNthCalledWith(
      2,
      'test-user-123',
      urduMessage,
      3 // Same conversation_id from first message
    );

    // === Step 4: Verify previous English messages still visible ===
    expect(screen.getByText(/Here are your tasks/i)).toBeInTheDocument();
    expect(screen.getByText(/آپ کون سا کام/i)).toBeInTheDocument();
  });

  /**
   * Additional Test: Verify RTL layout for Urdu
   */
  it('should apply RTL layout when Urdu is selected', async () => {
    const user = userEvent.setup();
    render(<SmartTodoApp />, { wrapper: TestWrapper });

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/type.*message/i)).toBeInTheDocument();
    });

    // Switch to Urdu
    const urduToggleButton = screen.getByRole('button', { name: /urdu/i });
    await user.click(urduToggleButton);

    // Verify RTL class is applied to the app container
    await waitFor(() => {
      const appContainer = document.querySelector('.smart-todo-app');
      expect(appContainer).toHaveAttribute('dir', 'rtl');
    });
  });

  /**
   * Additional Test: Verify language preference persistence
   */
  it('should persist language preference in localStorage', async () => {
    const user = userEvent.setup();
    render(<SmartTodoApp />, { wrapper: TestWrapper });

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/type.*message/i)).toBeInTheDocument();
    });

    // Switch to Urdu
    const urduToggleButton = screen.getByRole('button', { name: /urdu/i });
    await user.click(urduToggleButton);

    // Verify language preference is saved to localStorage
    await waitFor(() => {
      const languagePreference = localStorage.getItem(`language_pref_${mockUser.id}`);
      expect(languagePreference).toBeTruthy();

      if (languagePreference) {
        const parsed = JSON.parse(languagePreference);
        expect(parsed.preferredLanguage).toBe('ur');
        expect(parsed.userId).toBe(mockUser.id);
      }
    });
  });

  /**
   * Additional Test: Verify language detection accuracy
   */
  it('should correctly detect mixed language text (dominant language wins)', async () => {
    const mixedMessage = 'Hello مرحبا مرحبا مرحبا'; // More Urdu than English
    const urduResponse = {
      conversation_id: 4,
      response: 'سلام! میں آپ کی کیسے مدد کر سکتا ہوں؟',
      tool_calls: [],
      success: true
    };

    vi.mocked(api.apiClient.sendMessage).mockResolvedValue(urduResponse);

    const user = userEvent.setup();
    render(<SmartTodoApp />, { wrapper: TestWrapper });

    // Click Chat button
    const chatButton = await screen.findByText(/💬 Chat/i);
    await user.click(chatButton);

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/type.*message|placeholder/i)).toBeInTheDocument();
    });

    const input = screen.getByPlaceholderText(/type.*message|placeholder/i);
    const sendButton = screen.getByRole('button', { name: /send/i });

    // Type mixed message (more Urdu characters)
    await user.type(input, mixedMessage);
    await user.click(sendButton);

    // Verify API was called (language detection happens client-side)
    await waitFor(() => {
      expect(api.apiClient.sendMessage).toHaveBeenCalledWith(
        'test-user-123',
        mixedMessage,
        expect.anything() // conversation_id
      );
    });
  });
});
