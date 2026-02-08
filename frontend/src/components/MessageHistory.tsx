/**
 * MessageHistory component -- Displays the conversation history.
 * Uses design-token classes for theme consistency.
 */

import React from 'react';
import { Message } from '@/types/chat';

interface MessageHistoryProps {
  messages: Message[];
}

export const MessageHistory: React.FC<MessageHistoryProps> = ({ messages }) => {
  if (messages.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-muted-foreground py-12">
        <p className="text-lg font-medium">No messages yet</p>
        <p className="text-sm mt-2">Start a conversation by sending a message</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col space-y-4">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          aria-live="polite"
          aria-atomic="true"
        >
          <div
            className={`max-w-[80%] rounded-lg px-4 py-3 ${
              message.role === 'user'
                ? 'bg-primary text-primary-foreground rounded-tr-none'
                : 'bg-muted text-foreground rounded-tl-none'
            }`}
          >
            <div className="whitespace-pre-wrap break-words leading-relaxed">
              {message.content}
            </div>
            <div
              className={`text-xs mt-1 ${
                message.role === 'user' ? 'text-primary-foreground/70' : 'text-muted-foreground'
              }`}
            >
              {new Date(message.timestamp).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
