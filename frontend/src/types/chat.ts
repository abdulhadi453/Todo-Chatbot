/**
 * Type definitions for chat functionality
 */

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  conversationId?: string | null;
}

export interface Conversation {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  messageCount: number;
}

export interface SendMessageRequest {
  message: string;
  conversation_id?: string;
  model_preferences?: {
    temperature?: number;
  };
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  timestamp: string;
  message_id: string;
  conversation_title: string;
  tool_calls?: ToolCallData[] | null;
  tool_results?: ToolResultData[] | null;
  using_stub?: boolean;
  error?: string;
}

export interface ErrorResponse {
  error: string;
  message: string;
  status_code: number;
  details?: unknown;
}

// --- Streaming types ---

/** Represents the current state of a streaming response. */
export type StreamStatus = 'idle' | 'connecting' | 'streaming' | 'complete' | 'error' | 'cancelled';

/** A chunk of streamed text received from the backend. */
export interface StreamChunk {
  /** The text content in this chunk. */
  content: string;
  /** Whether this is the final chunk. */
  done: boolean;
  /** Optional metadata attached to this chunk. */
  metadata?: Record<string, unknown>;
}

/** Configuration options for streaming behavior. */
export interface StreamingOptions {
  /** Delay in ms between rendering chunks for simulated streaming (default: 18). */
  chunkDelayMs?: number;
  /** Number of characters per simulated chunk (default: 3). */
  chunkSize?: number;
  /** AbortSignal to cancel the stream externally. */
  signal?: AbortSignal;
  /** Callback fired on each chunk as it arrives. */
  onChunk?: (chunk: string, accumulated: string) => void;
  /** Callback fired when streaming completes. */
  onComplete?: (fullText: string) => void;
  /** Callback fired on error. */
  onError?: (error: Error) => void;
}

/** State exposed by the useStreaming hook. */
export interface StreamState {
  /** The text accumulated so far during streaming. */
  streamedText: string;
  /** Current status of the stream. */
  status: StreamStatus;
  /** Error if status is 'error'. */
  error: Error | null;
  /** The full ChatResponse once complete (null while streaming). */
  response: ChatResponse | null;
}

/** Tool call data from the backend agent response. */
export interface ToolCallData {
  id: string;
  name: string;
  arguments: Record<string, unknown>;
}

/** Tool result data from the backend agent response. */
export interface ToolResultData {
  tool_call_id: string;
  name: string;
  result: Record<string, unknown>;
}