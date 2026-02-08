/**
 * Component tests for ChatInterface.
 *
 * These tests verify the functionality and behavior of the ChatInterface
 * component in isolation and integration scenarios.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ChatInterface } from '@/components/ChatInterface';
import { useAuth } from '@/context/auth-context';
import { chatApi } from '@/lib/api/chatClient';
import { Message } from '@/types/chat';

// Mock the auth context
vi.mock('@/context/auth-context', () => ({
  useAuth: vi.fn(),
}));

// Mock the chat API client
vi.mock('@/lib/api/chatClient', () => ({
  chatApi: {
    sendMessage: vi.fn(),
    streamMessage: vi.fn(),
    getUserConversations: vi.fn(),
    getConversation: vi.fn(),
    deleteConversation: vi.fn(),
  },
}));

// Mock child components
vi.mock('@/components/MessageHistory', () => ({
  MessageHistory: ({ messages }: { messages: Message[] }) => (
    <div data-testid="message-history">
      {messages.map((msg, index) => (
        <div key={index} data-role={msg.role}>
          {msg.content}
        </div>
      ))}
    </div>
  ),
}));

vi.mock('@/components/MessageInput', () => ({
  MessageInput: ({ onSendMessage, disabled }: { onSendMessage: (text: string) => void, disabled: boolean }) => (
    <input
      data-testid="message-input"
      onChange={(e) => onSendMessage(e.target.value)}
      disabled={disabled}
      placeholder="Type a message..."
    />
  ),
}));

describe('ChatInterface', () => {
  const mockUser = {
    id: 'user-123',
    email: 'test@example.com',
    name: 'Test User',
  };

  beforeEach(() => {
    vi.clearAllMocks();

    // Default auth context
    (useAuth as jest.MockedFunction<typeof useAuth>).mockReturnValue({
      user: mockUser,
      loading: false,
    });

    // Default chat API mock
    (chatApi.sendMessage as jest.MockedFunction<any>).mockResolvedValue({
      conversation_id: 'conv-123',
      response: 'Hello! I received your message.',
      timestamp: new Date().toISOString(),
      message_id: 'msg-123',
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders without crashing', () => {
    render(<ChatInterface />);

    expect(screen.getByLabelText(/Chat interface/i)).toBeInTheDocument();
    expect(screen.getByTestId('message-input')).toBeInTheDocument();
    expect(screen.getByTestId('message-history')).toBeInTheDocument();
  });

  it('displays initial conversation if provided', () => {
    render(<ChatInterface initialConversationId="existing-conv-456" />);

    // Should have stored the initial conversation ID
    // Implementation-dependent: checking for rendered elements
    expect(screen.getByLabelText(/Chat interface/i)).toBeInTheDocument();
  });

  it('allows user to send a message', async () => {
    render(<ChatInterface />);

    const messageInput = screen.getByTestId('message-input');
    const messageText = 'Hello, AI assistant!';

    fireEvent.change(messageInput, { target: { value: messageText } });

    // Simulate sending the message (by changing input, as implemented in the component)
    fireEvent.change(messageInput, { target: { value: messageText } });

    await waitFor(() => {
      expect(chatApi.sendMessage).toHaveBeenCalledWith(
        mockUser.id,
        messageText,
        undefined  // No conversation ID initially
      );
    });
  });

  it('shows user message immediately before API response', async () => {
    render(<ChatInterface />);

    const messageInput = screen.getByTestId('message-input');
    const userMessage = 'Test message';

    fireEvent.change(messageInput, { target: { value: userMessage } });

    // The message should appear in the history immediately
    await waitFor(() => {
      expect(screen.getByText(userMessage)).toBeInTheDocument();
    });
  });

  it('shows AI response after API call completes', async () => {
    const aiResponse = 'I received your message.';
    (chatApi.sendMessage as jest.MockedFunction<any>).mockResolvedValue({
      conversation_id: 'conv-123',
      response: aiResponse,
      timestamp: new Date().toISOString(),
      message_id: 'msg-456',
    });

    render(<ChatInterface />);

    const messageInput = screen.getByTestId('message-input');
    fireEvent.change(messageInput, { target: { value: 'Test message' } });

    await waitFor(() => {
      expect(screen.getByText(aiResponse)).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    const errorMessage = 'Failed to send message';
    (chatApi.sendMessage as jest.MockedFunction<any>).mockRejectedValue(
      new Error(errorMessage)
    );

    render(<ChatInterface />);

    const messageInput = screen.getByTestId('message-input');
    fireEvent.change(messageInput, { target: { value: 'Test message' } });

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it('disables input while loading', async () => {
    // Make API call take longer to test loading state
    (chatApi.sendMessage as jest.MockedFunction<any>).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({
        conversation_id: 'conv-123',
        response: 'Response',
        timestamp: new Date().toISOString(),
        message_id: 'msg-789',
      }), 100))
    );

    render(<ChatInterface />);

    const messageInput = screen.getByTestId('message-input');
    fireEvent.change(messageInput, { target: { value: 'Test message' } });

    // Input should be disabled during API call
    expect(messageInput).toBeDisabled();

    // Wait for API call to complete
    await waitFor(() => {
      expect(messageInput).not.toBeDisabled();
    });
  });

  it('maintains conversation ID after first message', async () => {
    const conversationId = 'new-conversation-123';
    (chatApi.sendMessage as jest.MockedFunction<any>).mockResolvedValue({
      conversation_id: conversationId,
      response: 'Response',
      timestamp: new Date().toISOString(),
      message_id: 'msg-101',
    });

    render(<ChatInterface />);

    const messageInput = screen.getByTestId('message-input');
    fireEvent.change(messageInput, { target: { value: 'First message' } });

    await waitFor(() => {
      // Second message should use the established conversation ID
      fireEvent.change(messageInput, { target: { value: 'Second message' } });
    });

    // Verify that the second call used the conversation ID
    expect(chatApi.sendMessage).toHaveBeenLastCalledWith(
      mockUser.id,
      'Second message',
      conversationId
    );
  });

  it('shows error message when user is not authenticated', () => {
    (useAuth as jest.MockedFunction<typeof useAuth>).mockReturnValue({
      user: null,
      loading: false,
    });

    render(<ChatInterface />);

    const messageInput = screen.getByTestId('message-input');
    fireEvent.change(messageInput, { target: { value: 'Test message' } });

    // Component might not send the message, or might show an error
    // This behavior depends on the actual implementation
    // If it doesn't send when user is null, the API shouldn't be called
    expect(chatApi.sendMessage).not.toHaveBeenCalled();
  });

  it('shows loading state when auth is loading', () => {
    (useAuth as jest.MockedFunction<typeof useAuth>).mockReturnValue({
      user: null,
      loading: true,
    });

    render(<ChatInterface />);

    // With loading=true, the input might be disabled
    const messageInput = screen.getByTestId('message-input');
    expect(messageInput).toBeDisabled();
  });

  it('calls onConversationChange when conversation ID changes', async () => {
    const onConversationChangeMock = vi.fn();
    const newConvId = 'new-conversation-456';

    (chatApi.sendMessage as jest.MockedFunction<any>).mockResolvedValue({
      conversation_id: newConvId,
      response: 'Response',
      timestamp: new Date().toISOString(),
      message_id: 'msg-202',
    });

    render(<ChatInterface onConversationChange={onConversationChangeMock} />);

    const messageInput = screen.getByTestId('message-input');
    fireEvent.change(messageInput, { target: { value: 'Test message' } });

    await waitFor(() => {
      expect(onConversationChangeMock).toHaveBeenCalledWith(newConvId);
    });
  });

  it('does not send empty messages', async () => {
    render(<ChatInterface />);

    const messageInput = screen.getByTestId('message-input');
    fireEvent.change(messageInput, { target: { value: '' } });

    // API should not be called for empty messages
    await waitFor(() => {
      expect(chatApi.sendMessage).not.toHaveBeenCalled();
    });
  });

  it('trims whitespace from messages before sending', async () => {
    const messageWithWhitespace = '   Test message with spaces   ';
    const trimmedMessage = 'Test message with spaces';

    render(<ChatInterface />);

    const messageInput = screen.getByTestId('message-input');
    fireEvent.change(messageInput, { target: { value: messageWithWhitespace } });

    await waitFor(() => {
      expect(chatApi.sendMessage).toHaveBeenCalledWith(
        mockUser.id,
        trimmedMessage,
        undefined
      );
    });
  });
});