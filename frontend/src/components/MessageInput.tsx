/**
 * MessageInput component -- Handles user input for chat messages.
 * Uses design-token classes for theme consistency.
 */

import React, { useState, KeyboardEvent } from 'react';

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  disabled: boolean;
}

export const MessageInput: React.FC<MessageInputProps> = ({ onSendMessage, disabled }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = () => {
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex items-end border border-border rounded-lg bg-card p-2">
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your message..."
        disabled={disabled}
        className="flex-1 border-0 focus:ring-0 focus:outline-none py-2 px-3 text-foreground bg-transparent placeholder:text-muted-foreground resize-none"
        aria-label="Type your message"
      />
      <button
        onClick={handleSubmit}
        disabled={disabled || !message.trim()}
        className={`ml-2 px-4 py-2 rounded-lg font-medium transition-colors ${
          disabled || !message.trim()
            ? 'bg-muted text-muted-foreground cursor-not-allowed'
            : 'bg-primary text-primary-foreground hover:bg-primary/90'
        }`}
        aria-label="Send message"
      >
        Send
      </button>
    </div>
  );
};
