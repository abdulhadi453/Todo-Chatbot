/**
 * LoadingIndicator component -- Shows loading state during AI response generation.
 * Uses design-token classes for theme consistency.
 */

import React from 'react';

interface LoadingIndicatorProps {
  message?: string;
}

export const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  message = 'AI is thinking...',
}) => {
  return (
    <div
      className="flex items-center justify-center p-4"
      role="status"
      aria-live="polite"
    >
      <div className="flex items-center">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary mr-3" />
        <span className="text-muted-foreground">{message}</span>
      </div>
    </div>
  );
};
