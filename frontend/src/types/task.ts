export interface TodoTask {
  id: string; // Changed to string to match typical UUID format
  title: string; // Added title field
  description?: string;
  completed: boolean; // Changed to completed to match UI expectations
  category?: string;
  priority?: 'low' | 'medium' | 'high';
  dueDate?: string;
  createdAt: string;
  updatedAt: string;
  userId: string; // Changed from user_id to userId for consistency
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
  category?: string;
  priority?: 'low' | 'medium' | 'high';
  dueDate?: string;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  category?: string;
  priority?: 'low' | 'medium' | 'high';
  dueDate?: string;
  completed?: boolean;
}

export interface ToggleTaskCompletionResponse {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  category?: string;
  priority?: 'low' | 'medium' | 'high';
  dueDate?: string;
  createdAt: string;
  updatedAt: string;
  userId: string;
}