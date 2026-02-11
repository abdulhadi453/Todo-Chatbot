/**
 * RealtimeUpdater - Handles real-time updates when agent modifies todos.
 * Uses event sourcing or polling to keep the UI synchronized with backend changes.
 */

import { useEffect, useState } from 'react';
import { TodoTask } from '@/types/task';

interface RealtimeUpdateCallback {
  onTodoAdded?: (todo: TodoTask) => void;
  onTodoUpdated?: (todo: TodoTask) => void;
  onTodoDeleted?: (todoId: string) => void;
  onError?: (error: Error) => void;
}

class RealtimeUpdater {
  private static instance: RealtimeUpdater;
  private listeners: Map<string, RealtimeUpdateCallback> = new Map();
  private pollingInterval: number = 5000; // 5 seconds
  private pollingTimer: NodeJS.Timeout | null = null;
  private isPolling: boolean = false;
  private lastSyncTimestamp: number = Date.now();

  // Singleton pattern
  public static getInstance(): RealtimeUpdater {
    if (!RealtimeUpdater.instance) {
      RealtimeUpdater.instance = new RealtimeUpdater();
    }
    return RealtimeUpdater.instance;
  }

  /**
   * Subscribe to real-time updates for a specific user
   */
  subscribe(userId: string, callbacks: RealtimeUpdateCallback): void {
    this.listeners.set(userId, callbacks);

    // Start polling if not already started
    if (!this.isPolling) {
      this.startPolling();
    }
  }

  /**
   * Unsubscribe from real-time updates for a specific user
   */
  unsubscribe(userId: string): void {
    this.listeners.delete(userId);

    // Stop polling if no listeners remain
    if (this.listeners.size === 0) {
      this.stopPolling();
    }
  }

  /**
   * Start polling for updates
   */
  private startPolling(): void {
    if (this.isPolling) return;

    this.isPolling = true;
    this.pollingTimer = setInterval(async () => {
      await this.checkForUpdates();
    }, this.pollingInterval);
  }

  /**
   * Stop polling for updates
   */
  private stopPolling(): void {
    if (this.pollingTimer) {
      clearInterval(this.pollingTimer);
      this.pollingTimer = null;
      this.isPolling = false;
    }
  }

  /**
   * Check for updates from the backend
   */
  private async checkForUpdates(): Promise<void> {
    // Only proceed if we have listeners
    if (this.listeners.size === 0) {
      return;
    }

    for (const [userId, callbacks] of this.listeners.entries()) {
      try {
        // Fetch recent changes since last sync
        const recentTodos = await this.fetchRecentTodos(userId, this.lastSyncTimestamp);

        // Process each change
        for (const todo of recentTodos) {
          // Determine the type of change based on the todo's state
          if (this.isNewTodo(todo)) {
            callbacks.onTodoAdded?.(todo);
          } else if (this.isUpdatedTodo(todo)) {
            callbacks.onTodoUpdated?.(todo);
          }
        }

        this.lastSyncTimestamp = Date.now();
      } catch (error) {
        console.error(`Error checking for updates for user ${userId}:`, error);
        // Notify of error if callback exists
        callbacks.onError?.(error as Error);
      }
    }
  }

  /**
   * Fetch recent todos from the backend
   */
  private async fetchRecentTodos(userId: string, since: number): Promise<TodoTask[]> {
    // In a real implementation, this would make an API call
    // For now, we'll simulate with a mock implementation

    // Simulating API call delay
    await new Promise(resolve => setTimeout(resolve, 100));

    // Return empty array for demo - in real app this would fetch actual data
    return [];
  }

  /**
   * Check if a todo is new based on its creation timestamp
   */
  private isNewTodo(todo: TodoTask): boolean {
    // In a real implementation, compare creation time with last sync
    return false;
  }

  /**
   * Check if a todo has been updated based on its modification timestamp
   */
  private isUpdatedTodo(todo: TodoTask): boolean {
    // In a real implementation, compare update time with last sync
    return false;
  }

  /**
   * Force a sync check
   */
  public async forceSync(): Promise<void> {
    await this.checkForUpdates();
  }

  /**
   * Destroy the instance (for cleanup)
   */
  destroy(): void {
    this.stopPolling();
    this.listeners.clear();
  }
}

// Hook for React components to use real-time updates
export const useRealtimeTodos = (userId: string, callbacks?: RealtimeUpdateCallback) => {
  const [todos, setTodos] = useState<TodoTask[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const updater = RealtimeUpdater.getInstance();

    if (callbacks) {
      updater.subscribe(userId, {
        ...callbacks,
        onTodoAdded: (todo) => {
          setTodos(prev => [...prev, todo]);
          callbacks.onTodoAdded?.(todo);
        },
        onTodoUpdated: (todo) => {
          setTodos(prev => prev.map(t => t.id === todo.id ? todo : t));
          callbacks.onTodoUpdated?.(todo);
        },
        onTodoDeleted: (todoId) => {
          setTodos(prev => prev.filter(t => t.id !== todoId));
          callbacks.onTodoDeleted?.(todoId);
        },
        onError: (err) => {
          setError(err);
          callbacks.onError?.(err);
        }
      });
    }

    // Cleanup on unmount
    return () => {
      updater.unsubscribe(userId);
    };
  }, [userId, callbacks]);

  return { todos, loading, error, forceSync: RealtimeUpdater.getInstance().forceSync };
};

// Direct API for manual control
export const realtimeUpdater = RealtimeUpdater.getInstance();

export default RealtimeUpdater;