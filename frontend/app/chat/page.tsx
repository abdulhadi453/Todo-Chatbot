'use client';

/**
 * Chat page -- full-page chat UI with conversation sidebar and streaming
 * response support. Uses the shared Layout and design-token styling.
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../../src/context/auth-context';
import { chatApi } from '@/lib/api/chatClient';
import { MessageHistory } from '../../src/components/MessageHistory';
import { MessageInput } from '../../src/components/MessageInput';
import { LoadingIndicator } from '../../src/components/LoadingIndicator';
import { StreamingMessage, StreamingStyles } from '../../src/components/StreamingHandler';
import { useStreaming } from '../../src/hooks/useStreaming';
import { Message, Conversation, ChatResponse } from '../../src/types/chat';
import Layout from '../../src/components/layout/layout';
import ProtectedRoute from '../../src/components/protected-route';
import { Card, CardContent, CardHeader, CardTitle } from '../../src/components/ui/card';
import { MessageSquare, Plus } from 'lucide-react';
import { Button } from '../../src/components/ui/button';

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

  useEffect(() => {
    if (user) {
      loadConversations();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

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

  // --------------------------------------------------------------------------
  // Loading state
  // --------------------------------------------------------------------------

  if (authLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center flex-1">
          <LoadingIndicator message="Loading..." />
        </div>
      </Layout>
    );
  }

  // --------------------------------------------------------------------------
  // Render
  // --------------------------------------------------------------------------

  return (
    <ProtectedRoute>
      <Layout>
        <StreamingStyles />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full flex-1 flex flex-col py-6">
          {/* Page header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
            <div>
              <h1 className="text-3xl md:text-4xl font-bold text-foreground">
                AI Chat Assistant
              </h1>
              <p className="text-muted-foreground text-lg mt-1">
                Ask questions about your tasks and get help
              </p>
            </div>

            <Button
              onClick={handleNewConversation}
              className="gap-2 bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-primary-foreground"
            >
              <Plus className="h-4 w-4" aria-hidden="true" />
              New Chat
            </Button>
          </div>

          {/* Error banner */}
          {error && (
            <div
              className="mb-4 p-3 bg-destructive/10 border-l-4 border-destructive text-destructive rounded flex items-center justify-between"
              role="alert"
            >
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
          )}

          {/* Main grid */}
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 flex-1 min-h-0">
            {/* Sidebar */}
            <aside className="lg:col-span-1">
              <Card className="border bg-card shadow-sm h-full">
                <CardHeader className="pb-3">
                  <CardTitle className="text-xl font-bold text-foreground flex items-center gap-2">
                    <MessageSquare className="h-5 w-5 text-primary" aria-hidden="true" />
                    Conversations
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {loadingConversations ? (
                    <div className="flex justify-center py-4">
                      <LoadingIndicator message="Loading..." />
                    </div>
                  ) : (
                    <div className="space-y-2 max-h-[calc(100vh-360px)] overflow-y-auto">
                      {conversations.map((conv) => (
                        <div
                          key={conv.id}
                          className={`p-3 rounded-lg cursor-pointer transition-colors ${
                            conv.id === currentConversationId
                              ? 'bg-primary/10 border border-primary/30'
                              : 'hover:bg-muted border border-transparent'
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
                          <div className="font-medium truncate text-foreground text-sm">
                            {conv.title}
                          </div>
                          <div className="text-xs text-muted-foreground mt-1">
                            {new Date(conv.updatedAt).toLocaleDateString()} -- {conv.messageCount}{' '}
                            messages
                          </div>
                        </div>
                      ))}

                      {conversations.length === 0 && (
                        <div className="text-muted-foreground text-sm italic py-4 text-center">
                          No conversations yet. Start a new chat!
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            </aside>

            {/* Chat area */}
            <section className="lg:col-span-3 flex flex-col min-h-0" aria-label="Chat messages">
              <Card className="border bg-card shadow-sm flex-1 flex flex-col min-h-0">
                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 min-h-[300px] max-h-[calc(100vh-380px)]">
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

                {/* Input area */}
                <div className="border-t border-border p-4">
                  <MessageInput onSendMessage={handleSendMessage} disabled={isStreaming} />
                </div>
              </Card>
            </section>
          </div>
        </div>
      </Layout>
    </ProtectedRoute>
  );
};

export default ChatPage;
