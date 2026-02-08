/**
 * ConversationHistory component - Displays a list of past conversations/agent sessions.
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/context/auth-context';
import { chatApi } from '@/lib/api/chatClient';
import { Message } from '@/types/chat';

interface Conversation {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  messageCount: number;
}

interface ConversationHistoryProps {
  onSelectConversation: (conversationId: string) => void;
  onCreateNewConversation: () => void;
  selectedConversationId?: string;
}

export const ConversationHistory: React.FC<ConversationHistoryProps> = ({
  onSelectConversation,
  onCreateNewConversation,
  selectedConversationId
}) => {
  const { user } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user?.id) {
      loadConversations();
    }
  }, [user?.id]);

  const loadConversations = async () => {
    if (!user?.id) return;

    try {
      setLoading(true);
      setError(null);

      const response = await chatApi.getUserConversations(user.id);

      // The API response format may vary, so we need to adapt it
      // If the response is a flat array of conversation objects
      if (Array.isArray(response)) {
        const formattedConversations = response.map((conv: any) => ({
          id: conv.id || conv.conversation_id,
          title: conv.title || conv.conversation_title || `Conversation ${conv.id?.substring(0, 8)}`,
          createdAt: conv.created_at || conv.created_at || new Date().toISOString(),
          updatedAt: conv.updated_at || conv.updated_at || new Date().toISOString(),
          messageCount: conv.message_count || conv.messages?.length || 0
        }));

        setConversations(formattedConversations);
      } else {
        // If the response has a different structure
        setConversations([]);
      }
    } catch (err) {
      console.error('Error loading conversations:', err);
      setError('Failed to load conversations');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteConversation = async (conversationId: string) => {
    if (!user?.id) return;

    if (!window.confirm('Are you sure you want to delete this conversation?')) {
      return;
    }

    try {
      await chatApi.deleteConversation(user.id, conversationId);
      // Refresh the conversation list
      await loadConversations();
    } catch (err) {
      console.error('Error deleting conversation:', err);
      setError('Failed to delete conversation');
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (loading) {
    return (
      <div className="p-4">
        <div className="animate-pulse flex flex-col space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-10 bg-muted rounded-md"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Conversations</h2>
          <button
            onClick={onCreateNewConversation}
            className="px-3 py-1 bg-primary text-primary-foreground rounded-md text-sm hover:bg-primary/90 transition-colors"
          >
            New
          </button>
        </div>

        {error && (
          <div className="text-destructive text-sm mb-2">{error}</div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto">
        {conversations.length === 0 ? (
          <div className="p-4 text-center text-muted-foreground text-sm">
            No conversations yet
          </div>
        ) : (
          <ul className="divide-y">
            {conversations.map((conversation) => (
              <li
                key={conversation.id}
                className={`p-3 hover:bg-accent cursor-pointer transition-colors ${
                  selectedConversationId === conversation.id ? 'bg-muted' : ''
                }`}
                onClick={() => onSelectConversation(conversation.id)}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium truncate text-sm">
                      {conversation.title}
                    </h3>
                    <div className="text-xs text-muted-foreground mt-1">
                      {formatDate(conversation.updatedAt)} • {conversation.messageCount} messages
                    </div>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteConversation(conversation.id);
                    }}
                    className="ml-2 text-destructive hover:text-destructive/80 opacity-0 group-hover:opacity-100 transition-opacity"
                    aria-label="Delete conversation"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M3 6h18" />
                      <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
                      <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
                    </svg>
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default ConversationHistory;