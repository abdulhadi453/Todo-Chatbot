'use client';

/**
 * Chat page -- full-page chat UI with conversation sidebar and streaming
 * response support.
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '@/context/auth-context';
import { chatApi } from '@/lib/api/chatClient';
import { MessageHistory } from '@/components/MessageHistory';
import { MessageInput } from '@/components/MessageInput';
import { LoadingIndicator } from '@/components/LoadingIndicator';
import { StreamingMessage, StreamingStyles } from '@/components/StreamingHandler';
import { useStreaming } from '@/hooks/useStreaming';
import { Message, Conversation, ChatResponse } from '@/types/chat';

const ChatPage = () => {
  const { user, isLoading: authLoading } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loadingConversations, setLoadingConversations] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Streaming hook
  const {
    streamedText,
    status: streamStatus,
    sendStreaming,
    cancel: cancelStream,
    reset: resetStream,
  } = useStreaming();

  const isStreaming = streamStatus === 'connecting' || streamStatus === 'streaming';

  // --------------------------------------------------------------------------
  // Effects
  // --------------------------------------------------------------------------

  // Load conversations when user is available
  useEffect(() => {
    if (user) {
      loadConversations();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  // Scroll to bottom when messages change or streaming text updates
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamedText]);

  // --------------------------------------------------------------------------
  // Conversation management
  // --------------------------------------------------------------------------

  const loadConversations = useCallback(async () => {
    if (!user) return;

    setLoadingConversations(true);
    try {
      const userConversations = await chatApi.getUserConversations(user.id);
      setConversations(
        (userConversations as Array<Record<string, unknown>>).map((conv) => ({
          id: conv.id as string,
          title:
            (conv.title as string) ||
            `Chat ${new Date(conv.created_at as string).toLocaleDateString()}`,
          createdAt: conv.created_at as string,
          updatedAt: conv.updated_at as string,
          messageCount: conv.message_count as number,
        }))
      );
    } catch (err: unknown) {
      console.error('Error loading conversations:', err);
      setError(err instanceof Error ? err.message : 'Failed to load conversations');
    } finally {
      setLoadingConversations(false);
    }
  }, [user]);

  const handleConversationSelect = useCallback(
    async (conversationId: string) => {
      if (!user) return;

      try {
        setError(null);

        const conversationData = (await chatApi.getConversation(
          user.id,
          conversationId
        )) as { messages: Array<Record<string, unknown>> };

        setCurrentConversationId(conversationId);
        resetStream();

        const conversationMessages: Message[] = conversationData.messages.map(
          (msg: Record<string, unknown>) => ({
            id: msg.id as string,
            role: msg.role as Message['role'],
            content: msg.content as string,
            timestamp: msg.timestamp as string,
            conversationId: conversationId,
          })
        );

        setMessages(conversationMessages);
      } catch (err: unknown) {
        console.error('Error loading conversation:', err);
        setError(err instanceof Error ? err.message : 'Failed to load conversation');
      }
    },
    [user, resetStream]
  );

  const handleNewConversation = useCallback(() => {
    cancelStream();
    resetStream();
    setCurrentConversationId(null);
    setMessages([]);
    setError(null);
  }, [cancelStream, resetStream]);

  // --------------------------------------------------------------------------
  // Message sending with streaming
  // --------------------------------------------------------------------------

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
        loadConversations();
      }
    },
    [currentConversationId, resetStream, loadConversations]
  );

  const handleSendMessage = useCallback(
    async (messageText: string) => {
      if (!user || !messageText.trim()) return;

      setError(null);

      // Optimistically add user message
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

        // Revert the optimistic user message
        setMessages((prev) => prev.slice(0, -1));
        resetStream();
      }
    },
    [user, currentConversationId, sendStreaming, finaliseAssistantMessage, resetStream]
  );

  // --------------------------------------------------------------------------
  // Loading / unauthenticated states
  // --------------------------------------------------------------------------

  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <LoadingIndicator message="Loading..." />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center bg-white p-8 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">Access Denied</h2>
          <p className="text-gray-600">Please log in to access the chat feature.</p>
        </div>
      </div>
    );
  }

  // --------------------------------------------------------------------------
  // Render
  // --------------------------------------------------------------------------

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <StreamingStyles />

      {/* Header */}
      <header className="bg-white shadow-sm py-4 px-6">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">AI Chat Assistant</h1>
            <p className="text-gray-600 text-sm">Ask questions about your tasks and get help</p>
          </div>
          <button
            onClick={handleNewConversation}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2"
          >
            New Chat
          </button>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 flex flex-col max-w-6xl w-full mx-auto p-4">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 flex-1">
          {/* Sidebar: conversation list */}
          <aside className="lg:col-span-1">
            <div className="bg-white p-4 rounded-lg shadow border h-full">
              <h2 className="text-lg font-semibold mb-4 text-gray-800">Conversations</h2>

              {loadingConversations ? (
                <div className="flex justify-center py-4">
                  <LoadingIndicator message="Loading..." />
                </div>
              ) : (
                <div className="space-y-2 max-h-[calc(100vh-240px)] overflow-y-auto">
                  {conversations.map((conv) => (
                    <div
                      key={conv.id}
                      className={`p-3 rounded cursor-pointer hover:bg-gray-100 transition-colors ${
                        conv.id === currentConversationId
                          ? 'bg-blue-50 border border-blue-300'
                          : 'border border-transparent'
                      }`}
                      onClick={() => handleConversationSelect(conv.id)}
                      role="button"
                      tabIndex={0}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          handleConversationSelect(conv.id);
                        }
                      }}
                      aria-label={`Open conversation: ${conv.title}`}
                      aria-current={conv.id === currentConversationId ? 'true' : undefined}
                    >
                      <div className="font-medium truncate text-gray-800 text-sm">
                        {conv.title}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {new Date(conv.updatedAt).toLocaleDateString()} -- {conv.messageCount}{' '}
                        messages
                      </div>
                    </div>
                  ))}

                  {conversations.length === 0 && (
                    <div className="text-gray-500 text-sm italic py-4 text-center">
                      No conversations yet
                    </div>
                  )}
                </div>
              )}
            </div>
          </aside>

          {/* Chat area */}
          <section className="lg:col-span-3 flex flex-col" aria-label="Chat messages">
            {/* Error banner */}
            {error && (
              <div
                className="mb-4 p-3 bg-red-50 border-l-4 border-red-500 text-red-700 rounded flex items-center justify-between"
                role="alert"
              >
                <span>{error}</span>
                <button
                  type="button"
                  onClick={() => setError(null)}
                  className="text-red-500 hover:text-red-700 ml-2 text-sm font-medium"
                  aria-label="Dismiss error"
                >
                  Dismiss
                </button>
              </div>
            )}

            {/* Message history */}
            <div className="flex-1 bg-white rounded-lg shadow p-4 mb-4 min-h-[400px] max-h-[calc(100vh-320px)] overflow-y-auto">
              <MessageHistory messages={messages} />

              {/* Streaming message */}
              {(streamStatus === 'connecting' || streamStatus === 'streaming') && (
                <div className="mt-4">
                  <StreamingMessage
                    text={streamedText}
                    status={streamStatus}
                    onCancel={cancelStream}
                  />
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <MessageInput onSendMessage={handleSendMessage} disabled={isStreaming} />
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-4 text-center text-gray-500 text-sm">
        AI Chat Assistant -- Secure by Better Auth
      </footer>
    </div>
  );
};

export default ChatPage;
