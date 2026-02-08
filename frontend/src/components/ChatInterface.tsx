/**
 * ChatInterface component -- Main container for chat functionality.
 *
 * Integrates the useStreaming hook for progressive response rendering.
 * Uses design-token classes for theme consistency.
 */

'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '@/context/auth-context';
import { MessageHistory } from './MessageHistory';
import { MessageInput } from './MessageInput';
import { StreamingMessage, StreamingStyles } from './StreamingHandler';
import { useStreaming } from '@/hooks/useStreaming';
import { Message, ChatResponse } from '@/types/chat';

interface ChatInterfaceProps {
  initialConversationId?: string;
  /** Called when the conversation ID changes (e.g. first message creates one). */
  onConversationChange?: (conversationId: string) => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  initialConversationId,
  onConversationChange,
}) => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(
    initialConversationId || null
  );
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    streamedText,
    status: streamStatus,
    sendStreaming,
    cancel: cancelStream,
    reset: resetStream,
  } = useStreaming();

  const isLoading = streamStatus === 'connecting' || streamStatus === 'streaming';

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamedText]);

  useEffect(() => {
    if (initialConversationId) {
      setCurrentConversationId(initialConversationId);
    }
  }, [initialConversationId]);

  const finaliseAssistantMessage = useCallback(
    (response: ChatResponse) => {
      const aiMessage: Message = {
        id: response.message_id,
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
        conversationId: response.conversation_id,
      };

      setMessages((prev) => [...prev, aiMessage]);
      resetStream();

      if (response.conversation_id && response.conversation_id !== currentConversationId) {
        setCurrentConversationId(response.conversation_id);
        onConversationChange?.(response.conversation_id);
      }
    },
    [currentConversationId, onConversationChange, resetStream]
  );

  const handleSendMessage = useCallback(
    async (messageText: string) => {
      if (!user || !messageText.trim()) return;

      setError(null);

      const userMessage: Message = {
        id: `temp-${Date.now()}`,
        role: 'user',
        content: messageText,
        timestamp: new Date().toISOString(),
        conversationId: currentConversationId,
      };
      setMessages((prev) => [...prev, userMessage]);

      try {
        const response = await sendStreaming(
          user.id,
          messageText,
          currentConversationId ?? undefined
        );

        if (response) {
          finaliseAssistantMessage(response);
        }
      } catch (err: unknown) {
        const errorMsg =
          err instanceof Error ? err.message : 'Failed to send message. Please try again.';
        console.error('Error sending message:', err);
        setError(errorMsg);

        setMessages((prev) => prev.slice(0, -1));
        resetStream();
      }
    },
    [user, currentConversationId, sendStreaming, finaliseAssistantMessage, resetStream]
  );

  return (
    <div
      className="flex flex-col h-full bg-card rounded-lg shadow-md overflow-hidden relative border border-border"
      role="region"
      aria-label="Chat interface"
    >
      <StreamingStyles />

      {/* Error banner */}
      {error && (
        <div
          className="mb-0 p-3 bg-destructive/10 border-l-4 border-destructive text-destructive m-2 rounded"
          role="alert"
          aria-live="polite"
        >
          <div className="flex items-center justify-between">
            <span className="text-sm">{error}</span>
            <button
              type="button"
              onClick={() => setError(null)}
              className="text-destructive hover:text-destructive/80 ml-2 text-sm font-medium"
              aria-label="Dismiss error"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <MessageHistory messages={messages} />

        {(streamStatus === 'connecting' || streamStatus === 'streaming') && (
          <StreamingMessage
            text={streamedText}
            status={streamStatus}
            onCancel={cancelStream}
          />
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="p-4 border-t border-border">
        <MessageInput onSendMessage={handleSendMessage} disabled={isLoading} />
      </div>
    </div>
  );
};

export default ChatInterface;
