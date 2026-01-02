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

    // Add token to requests
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        // Log in development
        if (import.meta.env.DEV) {
          console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
        }
        return config;
      },
      (error) => {
        console.error("[API] Request error:", error);
        return Promise.reject(error);
      }
    );

    // Add response interceptor for logging (development only)
    if (import.meta.env.DEV) {
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
   * List tasks with filters and sorting
   */
  async listTasks(
    userId: string,
    options?: {
      search?: string;
      status?: 'pending' | 'completed';
      priority?: 'high' | 'medium' | 'low';
      category?: string;
      sort_by?: 'due_date' | 'priority' | 'title';
      sort_order?: 'asc' | 'desc';
    }
  ): Promise<{ tasks: any[] }> {
    try {
      const params = new URLSearchParams();
      if (options?.search) params.append('search', options.search);
      if (options?.status) params.append('status', options.status);
      if (options?.priority) params.append('priority', options.priority);
      if (options?.category) params.append('category', options.category);
      if (options?.sort_by) params.append('sort_by', options.sort_by);
      if (options?.sort_order) params.append('sort_order', options.sort_order);

      const queryString = params.toString();
      const url = `/${userId}/tasks${queryString ? '?' + queryString : ''}`;

      const response = await this.client.get(url);
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  /**
   * Complete a task
   */
  async completeTask(userId: string, taskId: number): Promise<any> {
    try {
      const response = await this.client.post(`/${userId}/tasks/${taskId}/complete`);
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  /**
   * Delete a task
   */
  async deleteTask(userId: string, taskId: number): Promise<any> {
    try {
      const response = await this.client.delete(`/${userId}/tasks/${taskId}`);
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error;
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
        `/${userId}/chat`,
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
   * User signup
   */
  async signup(email: string, password: string, fullName: string): Promise<any> {
    try {
      const response = await this.client.post('/api/auth/signup', {
        email,
        password,
        full_name: fullName,
      });
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  /**
   * User signin
   */
  async signin(email: string, password: string): Promise<any> {
    try {
      const response = await this.client.post('/api/auth/signin', {
        email,
        password,
      });
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  /**
   * Refresh access token
   */
  async refreshToken(refreshToken: string): Promise<any> {
    try {
      const response = await this.client.post('/api/auth/refresh', {
        refresh_token: refreshToken,
      });
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  /**
   * Get current user
   */
  async getCurrentUser(): Promise<any> {
    try {
      const response = await this.client.get('/api/auth/me');
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
