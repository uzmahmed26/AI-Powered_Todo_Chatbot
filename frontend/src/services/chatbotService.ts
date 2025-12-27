/**
 * Chatbot Service
 * ============================================================================
 * Phase III: Frontend service for AI chatbot interactions
 * Handles communication with backend chatbot API
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: Date;
}

export interface ChatRequest {
  message: string;
  conversation_history: ChatMessage[];
  use_tools?: boolean;
}

export interface ChatResponse {
  message: string;
  tool_calls?: Array<{
    id: string;
    function: {
      name: string;
      args: any;
    };
  }>;
  conversation_id?: string;
}

/**
 * ChatbotService class for managing chatbot interactions
 */
export class ChatbotService {
  private conversationHistory: ChatMessage[] = [];

  /**
   * Send a message to the chatbot
   */
  async sendMessage(message: string, useTools: boolean = true): Promise<ChatResponse> {
    try {
      const request: ChatRequest = {
        message,
        conversation_history: this.conversationHistory,
        use_tools: useTools,
      };

      const response = await axios.post<ChatResponse>(
        `${API_BASE_URL}/chatbot/chat`,
        request
      );

      // Add user message to history
      this.conversationHistory.push({
        role: 'user',
        content: message,
        timestamp: new Date(),
      });

      // Add assistant response to history
      if (response.data.message) {
        this.conversationHistory.push({
          role: 'assistant',
          content: response.data.message,
          timestamp: new Date(),
        });
      }

      return response.data;
    } catch (error) {
      console.error('Chatbot error:', error);
      throw new Error('Failed to send message to chatbot');
    }
  }

  /**
   * Execute a tool function
   */
  async executeTool(toolName: string, toolArgs: any): Promise<any> {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/chatbot/execute-tool`,
        null,
        {
          params: {
            tool_name: toolName,
          },
          data: {
            arguments: toolArgs,
          },
        }
      );

      return response.data;
    } catch (error) {
      console.error('Tool execution error:', error);
      throw new Error('Failed to execute tool');
    }
  }

  /**
   * Get conversation history
   */
  getHistory(): ChatMessage[] {
    return [...this.conversationHistory];
  }

  /**
   * Clear conversation history
   */
  clearHistory(): void {
    this.conversationHistory = [];
  }

  /**
   * Check if chatbot service is healthy
   */
  async checkHealth(): Promise<boolean> {
    try {
      const response = await axios.get(`${API_BASE_URL}/chatbot/health`);
      return response.data.status === 'healthy';
    } catch (error) {
      console.error('Chatbot health check failed:', error);
      return false;
    }
  }

  /**
   * Process tool calls and execute them
   */
  async processToolCalls(toolCalls: ChatResponse['tool_calls']): Promise<any[]> {
    if (!toolCalls || toolCalls.length === 0) {
      return [];
    }

    const results = await Promise.all(
      toolCalls.map(async (toolCall) => {
        try {
          const result = await this.executeTool(
            toolCall.function.name,
            toolCall.function.args
          );
          return {
            tool_call_id: toolCall.id,
            function_name: toolCall.function.name,
            result,
          };
        } catch (error) {
          return {
            tool_call_id: toolCall.id,
            function_name: toolCall.function.name,
            error: (error as Error).message,
          };
        }
      })
    );

    return results;
  }
}

// Export singleton instance
export const chatbotService = new ChatbotService();
