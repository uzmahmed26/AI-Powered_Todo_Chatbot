/**
 * API client for Phase III Smart Todo ChatKit App.
 *
 * Provides type-safe API communication with the FastAPI backend.
 */

import axios, { AxiosInstance, AxiosError } from "axios";
import { translations } from "../locales/en";

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Chat request payload
 */
export interface ChatRequest {
  message: string;
  conversation_id?: number | null;
}

/**
 * Tool call information
 */
export interface ToolCall {
  tool: string;
  args: Record<string, any>;
  result: Record<string, any>;
}

/**
 * Chat response from API
 */
export interface ChatResponse {
  conversation_id: number;
  response: string;
  tool_calls: ToolCall[];
  success: boolean;
}

/**
 * Error response from API
 */
export interface ErrorResponse {
  error: string;
  detail?: string;
  status_code: number;
}

/**
 * API Client class for Smart Todo App
 */
class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000, // 30 second timeout
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Add request interceptor for logging (development only)
    if (import.meta.env.DEV) {
      this.client.interceptors.request.use(
        (config) => {
          console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
          return config;
        },
        (error) => {
          console.error("[API] Request error:", error);
          return Promise.reject(error);
        }
      );

      // Add response interceptor for logging
      this.client.interceptors.response.use(
        (response) => {
          console.log(`[API] Response ${response.status}:`, response.data);
          return response;
        },
        (error) => {
          console.error("[API] Response error:", error);
          return Promise.reject(error);
        }
      );
    }
  }

  /**
   * Send a chat message to the API
   *
   * @param userId - User ID from Better Auth
   * @param message - User's message
   * @param conversationId - Optional conversation ID for resuming
   * @returns Chat response with agent's reply
   */
  async sendMessage(
    userId: string,
    message: string,
    conversationId?: number | null
  ): Promise<ChatResponse> {
    try {
      const request: ChatRequest = {
        message,
        conversation_id: conversationId,
      };

      const response = await this.client.post<ChatResponse>(
        `/api/${userId}/chat`,
        request
      );

      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error; // TypeScript requires this after handleError
    }
  }

  /**
   * Get conversation history (for initial load)
   *
   * Note: This endpoint will be implemented in Phase 3 User Story 3
   * For now, history is loaded implicitly by the backend
   */
  async getConversationHistory(
    _userId: string,
    _conversationId: number
  ): Promise<any[]> {
    // Placeholder for Phase 3 User Story 3
    console.warn("Conversation history endpoint not yet implemented");
    return [];
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<{ status: string; service: string }> {
    try {
      const response = await this.client.get("/health");
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  /**
   * Handle API errors with user-friendly messages
   */
  private handleError(error: unknown): never {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ErrorResponse>;

      if (axiosError.response) {
        // Server responded with error
        const errorData = axiosError.response.data;
        const statusCode = axiosError.response.status;

        switch (statusCode) {
          case 400:
            throw new Error(errorData.detail || translations.errors.invalidRequest);
          case 403:
            throw new Error(translations.errors.permission);
          case 404:
            throw new Error(translations.errors.notFound);
          case 503:
            throw new Error(translations.errors.serviceUnavailable);
          case 504:
            throw new Error(translations.errors.timeout);
          default:
            throw new Error(errorData.detail || translations.errors.generic);
        }
      } else if (axiosError.request) {
        // Request made but no response
        throw new Error(translations.errors.network);
      } else {
        // Request setup error
        throw new Error(translations.errors.requestSetupFailed);
      }
    }

    // Unknown error type
    throw new Error(translations.errors.unexpected);
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
