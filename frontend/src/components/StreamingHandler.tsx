/**
 * StreamingMessage component -- renders an assistant message that is still
 * being streamed. Shows a blinking cursor, a cancel button, and smooth
 * character-by-character text appearance.
 *
 * Uses design-token classes for theme consistency.
 * The streaming logic lives in the `useStreaming` hook.
 */

'use client';

import React, { useEffect, useRef } from 'react';
import { StreamStatus } from '@/types/chat';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface StreamingMessageProps {
  /** The text accumulated so far. */
  text: string;
  /** Current status of the stream. */
  status: StreamStatus;
  /** Called when the user clicks the stop button. */
  onCancel?: () => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const StreamingMessage: React.FC<StreamingMessageProps> = ({
  text,
  status,
  onCancel,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll the container into view as text grows
  useEffect(() => {
    containerRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [text]);

  const isActive = status === 'streaming' || status === 'connecting';

  if (!isActive && !text) {
    return null;
  }

  return (
    <div
      ref={containerRef}
      className="flex justify-start"
      role="status"
      aria-live="polite"
      aria-label="Assistant is responding"
    >
      <div className="max-w-[80%] rounded-lg rounded-tl-none px-4 py-3 bg-muted text-foreground">
        {/* Streaming text */}
        <div className="whitespace-pre-wrap break-words leading-relaxed">
          {text || '\u00A0'}
          {/* Blinking cursor while streaming */}
          {isActive && (
            <span
              className="inline-block w-[2px] h-[1em] ml-[1px] align-text-bottom bg-foreground/60 streaming-cursor"
              aria-hidden="true"
            />
          )}
        </div>

        {/* Footer: status + cancel */}
        <div className="flex items-center justify-between mt-2">
          {/* Status label */}
          <span className="text-xs text-muted-foreground">
            {status === 'connecting' && 'Connecting...'}
            {status === 'streaming' && 'Generating response...'}
            {status === 'complete' && 'Done'}
            {status === 'cancelled' && 'Stopped'}
            {status === 'error' && 'Error'}
          </span>

          {/* Cancel button */}
          {isActive && onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="ml-3 text-xs font-medium text-destructive hover:text-destructive/80 transition-colors focus:outline-none focus:underline"
              aria-label="Stop generating"
            >
              Stop
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Inline cursor animation (injected once via <style>)
// ---------------------------------------------------------------------------

/**
 * StreamingStyles -- renders a <style> tag with the cursor blink keyframe.
 * Mount this once in the chat page or layout.
 */
export const StreamingStyles: React.FC = () => (
  <style>{`
    @keyframes streaming-blink {
      0%, 100% { opacity: 1; }
      50% { opacity: 0; }
    }
    .streaming-cursor {
      animation: streaming-blink 0.8s step-end infinite;
    }
  `}</style>
);

export default StreamingMessage;
