/**
 * API client for chat functionality.
 *
 * Provides both synchronous (sendMessage) and streaming (streamMessage)
 * interfaces for the /api/{user_id}/chat endpoint.
 */

import axios, { AxiosInstance } from 'axios';
import {
  SendMessageRequest,
  ChatResponse,
  StreamingOptions,
} from '@/types/chat';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

/**
 * Returns the auth token from localStorage.
 * Centralised so both axios and fetch paths use the same key.
 */
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  // Phase II stores the token under 'access_token'
  return localStorage.getItem('access_token') || localStorage.getItem('auth-token');
}

class ChatApi {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 60000, // 60 second timeout (agent calls can be slow)
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor to handle common errors
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('auth-token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // ---------------------------------------------------------------------------
  // Synchronous (non-streaming) send
  // ---------------------------------------------------------------------------

  /**
   * Send a message to the agent endpoint and wait for the full response.
   */
  async sendMessage(
    userId: string,
    message: string,
    conversationId?: string,
    modelPreferences?: { temperature?: number }
  ): Promise<ChatResponse> {
    const requestData: SendMessageRequest = {
      message,
      conversation_id: conversationId,
      model_preferences: modelPreferences,
    };

    try {
      const response = await this.api.post<ChatResponse>(
        `/api/${userId}/chat`,
        requestData
      );
      return response.data;
    } catch (error: unknown) {
      throw this.normaliseError(error);
    }
  }

  // ---------------------------------------------------------------------------
  // Streaming send
  // ---------------------------------------------------------------------------

  /**
   * Send a message and stream the response back chunk-by-chunk.
   *
   * The current backend returns a full JSON response (not SSE). This method
   * fetches the full response via the native `fetch` API (to allow
   * AbortController cancellation) and then progressively yields the text in
   * small chunks so the UI can render it incrementally.
   *
   * When the backend gains true SSE support the internal implementation can
   * switch to `ReadableStream` parsing without changing the public API.
   *
   * @returns An async generator that yields `{ content, done }` objects.
   */
  async *streamMessage(
    userId: string,
    message: string,
    conversationId?: string,
    options: StreamingOptions = {}
  ): AsyncGenerator<{ content: string; done: boolean; response?: ChatResponse }> {
    const {
      chunkDelayMs = 18,
      chunkSize = 3,
      signal,
    } = options;

    const token = getAuthToken();

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const body = JSON.stringify({
      message,
      conversation_id: conversationId,
    } satisfies SendMessageRequest);

    const res = await fetch(`${API_BASE_URL}/api/${userId}/chat`, {
      method: 'POST',
      headers,
      body,
      signal,
    });

    if (!res.ok) {
      let errorMessage = res.statusText;
      try {
        const errorBody = await res.json();
        errorMessage = errorBody.detail || errorBody.error || errorMessage;
      } catch {
        // ignore JSON parse failure
      }

      if (res.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('auth-token');
        window.location.href = '/login';
      }

      throw new Error(errorMessage);
    }

    const data: ChatResponse = await res.json();
    const fullText = data.response;

    // Progressively yield the text in small chunks for a streaming effect
    let offset = 0;
    while (offset < fullText.length) {
      // Respect abort signal between chunks
      if (signal?.aborted) {
        return;
      }

      const end = Math.min(offset + chunkSize, fullText.length);
      const chunk = fullText.slice(offset, end);
      offset = end;

      const done = offset >= fullText.length;

      yield {
        content: chunk,
        done,
        ...(done ? { response: data } : {}),
      };

      // Small delay between chunks for visual streaming effect
      if (!done) {
        await new Promise<void>((resolve) => setTimeout(resolve, chunkDelayMs));
      }
    }
  }

  // ---------------------------------------------------------------------------
  // Conversations
  // ---------------------------------------------------------------------------

  /**
   * Get all conversations for a user
   */
  async getUserConversations(userId: string): Promise<unknown[]> {
    try {
      const response = await this.api.get(`/api/${userId}/conversations`);
      return Array.isArray(response.data) ? response.data : response.data.conversations || [];
    } catch (error: unknown) {
      throw this.normaliseError(error);
    }
  }

  /**
   * Get a specific conversation and its messages
   */
  async getConversation(userId: string, conversationId: string): Promise<unknown> {
    try {
      const response = await this.api.get(`/api/${userId}/conversations/${conversationId}`);
      return response.data;
    } catch (error: unknown) {
      throw this.normaliseError(error);
    }
  }

  /**
   * Delete a conversation
   */
  async deleteConversation(userId: string, conversationId: string): Promise<void> {
    try {
      await this.api.delete(`/api/${userId}/conversations/${conversationId}`);
    } catch (error: unknown) {
      throw this.normaliseError(error);
    }
  }

  // ---------------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------------

  /** Normalise axios / generic errors into a plain Error. */
  private normaliseError(error: unknown): Error {
    if (axios.isAxiosError(error)) {
      if (error.response) {
        const errorMessage = error.response.data?.error || error.response.data?.detail || error.response.statusText;
        return new Error(errorMessage);
      } else if (error.request) {
        return new Error('Network error: Unable to reach the server');
      }
    }
    if (error instanceof Error) {
      return error;
    }
    return new Error('Unknown error occurred');
  }
}

export const chatApi = new ChatApi();