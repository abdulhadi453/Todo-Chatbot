/**
 * TypingIndicator component - Shows visual feedback when the agent is 'typing'.
 */

import React from 'react';

interface TypingIndicatorProps {
  isTyping?: boolean;
  className?: string;
  text?: string;
}

export const TypingIndicator: React.FC<TypingIndicatorProps> = ({
  isTyping = true,
  className = '',
  text = 'Thinking...'
}) => {
  if (!isTyping) {
    return null;
  }

  return (
    <div className={`flex items-center space-x-2 p-3 ${className}`} aria-live="polite" aria-busy="true">
      <div className="flex space-x-1 items-center">
        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
      </div>
      <span className="text-sm text-muted-foreground ml-2">{text}</span>
    </div>
  );
};

export default TypingIndicator;