'use client';

import React, { useState } from 'react';
import { TodoTask } from '../../types/task';
import { apiClient } from '../../services/api-client';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card, CardContent } from '../ui/card';
import { CalendarIcon, Hash, FlagTriangleRight } from 'lucide-react';

interface FormData {
  title: string;
  description?: string;
  category?: string;
  priority?: 'low' | 'medium' | 'high';
  dueDate?: string;
}

interface AddTaskFormProps {
  onTaskAdded?: (task: TodoTask) => void;
  onTaskCreated?: () => void; // Callback to trigger refresh in parent
}

const AddTaskForm = ({ onTaskAdded, onTaskCreated }: AddTaskFormProps) => {
  const [formData, setFormData] = useState<FormData>({
    title: '',
    description: '',
    category: '',
    priority: 'medium',
    dueDate: ''
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    setIsLoading(true);
    try {
      const response = await apiClient.createTask({
        title: formData.title,
        description: formData.description || undefined,
        category: formData.category || undefined,
        priority: formData.priority,
        dueDate: formData.dueDate || undefined
      });

      setFormData({
        title: '',
        description: '',
        category: '',
        priority: 'medium',
        dueDate: ''
      });

      if (onTaskAdded) {
        onTaskAdded(response.data);
      }

      // Trigger refresh in parent component
      if (onTaskCreated) {
        onTaskCreated();
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create task. Please try again.';
      setErrors({ submit: errorMessage });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <CardContent className="pt-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-1">
            <Input
              label="Task Title"
              type="text"
              className="px-2 border border-black placeholder:text-neutral-400"
              name="title"
              value={formData.title}
              onChange={handleChange}
              error={errors.title}
              placeholder="What needs to be done?"
              required
            />
          </div>

          <div className="space-y-1">
            <label htmlFor="description" className="block text-sm font-medium mb-2 text-foreground">
              Description
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              className="flex border-black min-h-25 w-full rounded-md border bg-background px-3 py-2 text-m placeholder:text-shadow-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
              placeholder="Add details about the task..."
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-1.5">
            <div className="space-y-2">
              <label htmlFor="category" className="text-sm font-medium mb-2 text-foreground flex items-center gap-2">
                <Hash className="inline h-4 w-4 text-primary" />
                Category
              </label>
              <input
                type="text"
                id="category"
                name="category"
                value={formData.category}
                onChange={handleChange}
                className="flex h-12 border-black w-full rounded-md border bg-background px-1.5 py-2 text-sm placeholder:text-shadow-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                placeholder="Work, Home"
              />
            </div>

            <div className="space-y-1">
              <label htmlFor="priority" className="text-sm font-medium mb-2 text-foreground flex items-center gap-2">
                <FlagTriangleRight className="inline  h-4 w-4 text-warning" />
                Priority
              </label>
              <select
                id="priority"
                name="priority"
                value={formData.priority}
                onChange={handleChange}
                className="flex h-12 w-full hover:cursor-pointer border-black rounded-md border bg-background px-2 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>

            <div className="space-y-1">
              <label htmlFor="dueDate" className="text-sm font-medium mb-2 text-foreground flex items-center gap-2">
                <CalendarIcon className="inline h-4 w-4 text-success" />
                Due Date
              </label>
              <input
                type="date"
                id="dueDate"
                name="dueDate"
                value={formData.dueDate}
                onChange={handleChange}
                className="flex h-12 w-full hover:cursor-pointer rounded-md border border-input bg-background px-1.5 py-2 text-sm text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              />
            </div>
          </div>

          {errors.submit && (
            <div className="text-destructive text-sm bg-destructive/10 p-3 rounded-md border border-destructive/20">
              <span className="font-medium">Error:</span> {errors.submit}
            </div>
          )}

          <Button
            type="submit"
            className="w-full"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Adding task...
              </>
            ) : (
              'Add Task'
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default AddTaskForm;