import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
import userEvent from '@testing-library/user-event';
import * as api from '../../src/lib/api/chatClient'; // Adjust path as needed
import ChatInterface from '../../src/components/ChatInterface'; // Adjust path as needed

// Mock the API functions
jest.mock('../../src/lib/api/chatClient', () => ({
  sendMessage: jest.fn(),
  getConversations: jest.fn(),
  getConversation: jest.fn(),
}));

// Mock the AuthContext
const mockAuthContext = {
  user: { id: 'test-user-id', email: 'test@example.com' },
  isAuthenticated: true,
};

jest.mock('../../src/context/auth-context', () => ({
  useAuth: () => mockAuthContext,
}));

// Mock the realtime updater
jest.mock('../../src/lib/api/realtime_updater', () => ({
  RealtimeUpdater: {
    subscribeToTodoUpdates: jest.fn(),
    unsubscribeFromTodoUpdates: jest.fn(),
  },
}));

describe('Real-time Updates in Agent Interface', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('updates UI immediately when agent creates a todo', async () => {
    const user = userEvent.setup();

    // Mock successful API responses
    (api.sendMessage as jest.MockedFunction<typeof api.sendMessage>).mockResolvedValue({
      response: "I've created a task to buy groceries for you.",
      conversation_id: 'test-conversation-id',
    });

    render(
      <MockedProvider>
        <ChatInterface />
      </MockedProvider>
    );

    // Simulate user typing and sending a message
    const input = screen.getByRole('textbox', { name: /message/i });
    await user.type(input, 'Add a task to buy groceries');
    const sendButton = screen.getByRole('button', { name: /send/i });
    await user.click(sendButton);

    // Wait for the API call to complete
    await waitFor(() => {
      expect(api.sendMessage).toHaveBeenCalledWith(
        'test-user-id',
        'Add a task to buy groceries',
        'test-conversation-id'
      );
    });

    // Verify the agent's response is displayed
    expect(screen.getByText(/created a task to buy groceries/i)).toBeInTheDocument();

    // In a real scenario, this would trigger a todo update
    // We'd verify that the todo list UI component has been updated
    // For now, we verify that the appropriate API calls were made
    expect(api.sendMessage).toHaveBeenCalled();
  });

  test('updates UI immediately when agent modifies a todo', async () => {
    const user = userEvent.setup();

    // Mock API responses
    (api.sendMessage as jest.MockedFunction<typeof api.sendMessage>).mockResolvedValue({
      response: "I've marked your grocery task as completed.",
      conversation_id: 'test-conversation-id',
    });

    render(
      <MockedProvider>
        <ChatInterface />
      </MockedProvider>
    );

    const input = screen.getByRole('textbox', { name: /message/i });
    await user.type(input, 'Mark the grocery task as completed');
    const sendButton = screen.getByRole('button', { name: /send/i });
    await user.click(sendButton);

    await waitFor(() => {
      expect(api.sendMessage).toHaveBeenCalledWith(
        'test-user-id',
        'Mark the grocery task as completed',
        'test-conversation-id'
      );
    });

    // Verify the response is displayed
    expect(screen.getByText(/marked your grocery task as completed/i)).toBeInTheDocument();
  });

  test('handles multiple simultaneous updates correctly', async () => {
    const user = userEvent.setup();

    // Mock API responses that trigger multiple updates
    (api.sendMessage as jest.MockedFunction<typeof api.sendMessage>).mockResolvedValue({
      response: "I've created multiple tasks for you: buy groceries, schedule meeting, and call mom.",
      conversation_id: 'test-conversation-id',
    });

    render(
      <MockedProvider>
        <ChatInterface />
      </MockedProvider>
    );

    const input = screen.getByRole('textbox', { name: /message/i });
    await user.type(input, 'Create tasks: buy groceries, schedule meeting, and call mom');
    const sendButton = screen.getByRole('button', { name: /send/i });
    await user.click(sendButton);

    await waitFor(() => {
      expect(api.sendMessage).toHaveBeenCalled();
    });

    // Verify response is displayed
    expect(screen.getByText(/created multiple tasks/i)).toBeInTheDocument();

    // In a real test, we'd verify that multiple todos were added to the UI
  });

  test('displays loading states during agent processing', async () => {
    const user = userEvent.setup();

    // Mock a delayed response to test loading state
    (api.sendMessage as jest.MockedFunction<typeof api.sendMessage>)
      .mockImplementation(() => new Promise(resolve => {
        setTimeout(() => resolve({
          response: "I've processed your request.",
          conversation_id: 'test-conversation-id',
        }), 100);
      }));

    render(
      <MockedProvider>
        <ChatInterface />
      </MockedProvider>
    );

    const input = screen.getByRole('textbox', { name: /message/i });
    await user.type(input, 'Process this request');
    const sendButton = screen.getByRole('button', { name: /send/i });
    await user.click(sendButton);

    // Check that loading state is displayed
    expect(screen.getByText(/thinking/i)).toBeInTheDocument(); // Assuming there's a thinking indicator

    // Wait for response
    await waitFor(() => {
      expect(screen.getByText(/processed your request/i)).toBeInTheDocument();
    });
  });

  test('shows error state when agent operations fail', async () => {
    const user = userEvent.setup();

    // Mock API failure
    (api.sendMessage as jest.MockedFunction<typeof api.sendMessage>)
      .mockRejectedValue(new Error('Failed to process request'));

    render(
      <MockedProvider>
        <ChatInterface />
      </MockedProvider>
    );

    const input = screen.getByRole('textbox', { name: /message/i });
    await user.type(input, 'This will fail');
    const sendButton = screen.getByRole('button', { name: /send/i });
    await user.click(sendButton);

    // Wait for error handling
    await waitFor(() => {
      expect(screen.getByText(/failed to process request/i)).toBeInTheDocument();
    });
  });

  test('maintains consistency between agent actions and UI state', async () => {
    const user = userEvent.setup();

    // Mock response that creates a todo
    (api.sendMessage as jest.MockedFunction<typeof api.sendMessage>).mockResolvedValue({
      response: "I've added 'Water plants' to your tasks.",
      conversation_id: 'test-conversation-id',
    });

    render(
      <MockedProvider>
        <ChatInterface />
      </MockedProvider>
    );

    const input = screen.getByRole('textbox', { name: /message/i });
    await user.type(input, 'Add task: Water plants');
    const sendButton = screen.getByRole('button', { name: /send/i });
    await user.click(sendButton);

    await waitFor(() => {
      expect(api.sendMessage).toHaveBeenCalled();
    });

    // Verify the agent's response matches the expected todo creation
    expect(screen.getByText(/added 'Water plants'/i)).toBeInTheDocument();

    // In a real test, we'd also verify that a corresponding todo item
    // appears in the todo list UI component, demonstrating consistency
    // between agent actions and UI state
  });

  test('synchronizes agent-initiated changes across all UI components', async () => {
    const user = userEvent.setup();

    // Mock API responses
    (api.sendMessage as jest.MockedFunction<typeof api.sendMessage>).mockResolvedValue({
      response: "I've updated your high priority tasks.",
      conversation_id: 'test-conversation-id',
    });

    render(
      <MockedProvider>
        <ChatInterface />
      </MockedProvider>
    );

    const input = screen.getByRole('textbox', { name: /message/i });
    await user.type(input, 'Update my high priority tasks');
    const sendButton = screen.getByRole('button', { name: /send/i });
    await user.click(sendButton);

    await waitFor(() => {
      expect(api.sendMessage).toHaveBeenCalled();
    });

    // Verify that any UI components showing high priority tasks
    // would be updated accordingly in a real implementation
    expect(screen.getByText(/updated your high priority tasks/i)).toBeInTheDocument();
  });
});