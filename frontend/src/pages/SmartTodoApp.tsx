/**
 * Smart Todo App Page - Main chat interface using OpenAI ChatKit
 *
 * This component provides the conversational todo management interface:
 * - OpenAI ChatKit UI for chat
 * - API integration with FastAPI backend
 * - Conversation persistence (localStorage)
 * - Typing indicators and error handling
 */

import React, { useState, useEffect } from "react";
import { apiClient, ChatResponse } from "../services/api";
import { useTranslation } from "../hooks/useTranslation";
import LanguageToggle from "../components/LanguageToggle";
import "../styles/SmartTodoApp.css";
import "../styles/rtl.css";

// Note: OpenAI ChatKit types - install @openai/chatkit package
// For now, using placeholder types until package is available
interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp?: Date;
}

const SmartTodoApp: React.FC = () => {
  // Translation hook
  const { translateAsync, language, isRTL, getTranslations } = useTranslation();

  // Get translations for current language
  const translations = getTranslations();

  // State
  const [messages, setMessages] = useState<Message[]>([]);
  const [translatedMessages, setTranslatedMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Hardcoded user ID for MVP (will be replaced with Better Auth in Phase 6)
  const userId = "demo-user";

  // Load conversation ID from localStorage on mount
  useEffect(() => {
    const savedConversationId = localStorage.getItem("conversationId");
    if (savedConversationId) {
      setConversationId(parseInt(savedConversationId, 10));
    }
  }, []);

  // Save conversation ID to localStorage when it changes
  useEffect(() => {
    if (conversationId) {
      localStorage.setItem("conversationId", conversationId.toString());
    }
  }, [conversationId]);

  // Translate messages when language changes
  useEffect(() => {
    const translateMessages = async () => {
      if (language === 'ur' && messages.length > 0) {
        const translated = await Promise.all(
          messages.map(async (msg) => ({
            ...msg,
            content: await translateAsync(msg.content),
          }))
        );
        setTranslatedMessages(translated);
      } else {
        setTranslatedMessages(messages);
      }
    };
    translateMessages();
  }, [messages, language, translateAsync]);

  /**
   * Send message to API and update chat
   */
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputMessage.trim()) {
      return;
    }

    // Add user message to UI immediately
    const userMessage: Message = {
      role: "user",
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);
    setError(null);

    try {
      // Send to API
      const response: ChatResponse = await apiClient.sendMessage(
        userId,
        inputMessage,
        conversationId
      );

      // Update conversation ID if new
      if (!conversationId && response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      // Add assistant response to UI
      const assistantMessage: Message = {
        role: "assistant",
        content: response.response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error("Error sending message:", err);
      const errorMessage = err instanceof Error ? err.message : "Failed to send message";
      setError(errorMessage);

      // Add error message to chat
      const errorMsg: Message = {
        role: "assistant",
        content: `❌ ${errorMessage}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Clear conversation and start fresh
   */
  const handleNewConversation = () => {
    setMessages([]);
    setConversationId(null);
    localStorage.removeItem("conversationId");
    setError(null);
  };

  return (
    <div className={`smart-todo-app ${isRTL ? 'rtl' : ''}`}>
      {/* Header */}
      <header className="app-header">
        <LanguageToggle />
        <h1>🤖 {translations.header.title}</h1>
        <p className="subtitle">{translations.header.subtitle}</p>
        <button
          className="btn-new-chat"
          onClick={handleNewConversation}
          title={translations.header.newChatTooltip}
        >
          {translations.header.newChatButton}
        </button>
      </header>

      {/* Chat Container */}
      <div className="chat-container">
        {/* Messages */}
        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message">
              <h2>{translations.welcome.heading} {translations.welcome.emoji}</h2>
              <p>{translations.welcome.intro}</p>
              <ul>
                {translations.welcome.examples.map((example: string, index: number) => (
                  <li key={index}>{example}</li>
                ))}
              </ul>
            </div>
          )}

          {translatedMessages.map((msg, index) => (
            <div
              key={index}
              className={`message ${msg.role === "user" ? "user-message" : "assistant-message"}`}
            >
              <div className="message-avatar">
                {msg.role === "user" ? translations.messages.userAvatar : translations.messages.assistantAvatar}
              </div>
              <div className="message-content">
                <div className="message-text">{msg.content}</div>
                {msg.timestamp && (
                  <div className="message-timestamp">
                    {msg.timestamp.toLocaleTimeString()}
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Loading indicator */}
          {isLoading && (
            <div className="message assistant-message typing-indicator">
              <div className="message-avatar">{translations.messages.assistantAvatar}</div>
              <div className="message-content">
                <div className="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Form */}
        <form className="input-form" onSubmit={handleSendMessage}>
          <input
            type="text"
            className="message-input"
            placeholder={translations.input.placeholder}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            disabled={isLoading}
          />
          <button type="submit" className="send-button" disabled={isLoading || !inputMessage.trim()}>
            {isLoading ? translations.input.sendingButton : translations.input.sendButton}
          </button>
        </form>

        {/* Error Display */}
        {error && (
          <div className="error-banner">
            <span>{translations.errors.prefix} {error}</span>
            <button onClick={() => setError(null)}>{translations.errors.close}</button>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="app-footer">
        <p>
          {conversationId ? (
            <>{translations.footer.conversationLabel}{conversationId}</>
          ) : (
            <>{translations.footer.defaultMessage}</>
          )}
        </p>
      </footer>
    </div>
  );
};

export default SmartTodoApp;
