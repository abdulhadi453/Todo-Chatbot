/**
 * useStreaming hook -- manages streaming chat responses.
 *
 * Consumes the async generator returned by chatApi.streamMessage and exposes
 * the progressive text, status, and control functions (cancel) to the UI.
 */

import { useCallback, useRef, useState } from 'react';
import { chatApi } from '@/lib/api/chatClient';
import {
  ChatResponse,
  StreamStatus,
  StreamState,
  StreamingOptions,
  Message,
} from '@/types/chat';

export interface UseStreamingReturn extends StreamState {
  /** Start streaming a message. Resolves when complete or cancelled. */
  sendStreaming: (
    userId: string,
    message: string,
    conversationId?: string
  ) => Promise<ChatResponse | null>;
  /** Cancel the current stream. */
  cancel: () => void;
  /** Reset state back to idle. */
  reset: () => void;
}

const INITIAL_STATE: StreamState = {
  streamedText: '',
  status: 'idle',
  error: null,
  response: null,
};

export function useStreaming(options?: StreamingOptions): UseStreamingReturn {
  const [state, setState] = useState<StreamState>(INITIAL_STATE);
  const abortRef = useRef<AbortController | null>(null);
  // Guard against state updates after unmount
  const mountedRef = useRef(true);

  // Clean-up on unmount handled by the consuming component via cancel()

  const cancel = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
    setState((prev) => ({
      ...prev,
      status: prev.status === 'streaming' || prev.status === 'connecting' ? 'cancelled' : prev.status,
    }));
  }, []);

  const reset = useCallback(() => {
    cancel();
    setState(INITIAL_STATE);
  }, [cancel]);

  const sendStreaming = useCallback(
    async (
      userId: string,
      message: string,
      conversationId?: string
    ): Promise<ChatResponse | null> => {
      // Abort any previous in-flight stream
      if (abortRef.current) {
        abortRef.current.abort();
      }

      const controller = new AbortController();
      abortRef.current = controller;

      setState({
        streamedText: '',
        status: 'connecting',
        error: null,
        response: null,
      });

      let accumulated = '';
      let finalResponse: ChatResponse | null = null;

      try {
        setState((prev) => ({ ...prev, status: 'streaming' }));

        const generator = chatApi.streamMessage(userId, message, conversationId, {
          ...options,
          signal: controller.signal,
        });

        for await (const chunk of generator) {
          if (controller.signal.aborted) {
            break;
          }

          accumulated += chunk.content;

          // Call user-provided onChunk callback
          options?.onChunk?.(chunk.content, accumulated);

          setState((prev) => ({
            ...prev,
            streamedText: accumulated,
            status: chunk.done ? 'complete' : 'streaming',
            response: chunk.response ?? prev.response,
          }));

          if (chunk.done && chunk.response) {
            finalResponse = chunk.response;
          }
        }

        if (!controller.signal.aborted) {
          options?.onComplete?.(accumulated);
          setState((prev) => ({
            ...prev,
            status: 'complete',
          }));
        }

        return finalResponse;
      } catch (err: unknown) {
        if (err instanceof DOMException && err.name === 'AbortError') {
          // Cancellation is not an error
          setState((prev) => ({ ...prev, status: 'cancelled' }));
          return null;
        }

        const error = err instanceof Error ? err : new Error(String(err));

        setState((prev) => ({
          ...prev,
          status: 'error',
          error,
        }));

        options?.onError?.(error);
        throw error;
      }
    },
    [options]
  );

  return {
    ...state,
    sendStreaming,
    cancel,
    reset,
  };
}
