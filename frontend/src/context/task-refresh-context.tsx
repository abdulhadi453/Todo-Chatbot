'use client';

/**
 * TaskRefreshContext - Provides a global mechanism to trigger task list refreshes
 * when the AI agent performs CRUD operations on tasks.
 */

import React, { createContext, useContext, useCallback, useState } from 'react';

interface TaskRefreshContextType {
  /** Trigger a refresh of all task lists */
  triggerRefresh: () => void;
  /** Subscribe to refresh events */
  refreshKey: number;
}

const TaskRefreshContext = createContext<TaskRefreshContextType | undefined>(undefined);

export const TaskRefreshProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [refreshKey, setRefreshKey] = useState(0);

  const triggerRefresh = useCallback(() => {
    setRefreshKey((prev) => prev + 1);
  }, []);

  return (
    <TaskRefreshContext.Provider value={{ triggerRefresh, refreshKey }}>
      {children}
    </TaskRefreshContext.Provider>
  );
};

export const useTaskRefresh = () => {
  const context = useContext(TaskRefreshContext);
  if (!context) {
    throw new Error('useTaskRefresh must be used within a TaskRefreshProvider');
  }
  return context;
};
