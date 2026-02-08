'use client';

import React, { useEffect, useState } from 'react';
import { TodoTask } from '../../types/task';
import { apiClient } from '../../services/api-client';
import TaskItem from './task-item';
import { Card } from '../ui/card';
import { Loader2, Calendar, Flag, Hash } from 'lucide-react';

interface TaskListProps {
  onTaskUpdate?: (task: TodoTask) => void;
  onTaskDelete?: (taskId: string) => void;
  onTaskCreated?: () => void;
}

const TaskList = ({ onTaskUpdate, onTaskDelete, onTaskCreated }: TaskListProps) => {
  const [tasks, setTasks] = useState<TodoTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');
  const [sortBy, setSortBy] = useState<'date' | 'priority' | 'title'>('date');
  const overdueTasks = tasks.filter(t => t.dueDate && new Date(t.dueDate) < new Date() && !t.completed).length;

  useEffect(() => {
    fetchTasks();
  }, []);

  // Refetch tasks when a new task is created (via parent callback)
  useEffect(() => {
    if (onTaskCreated) {
      fetchTasks();
    }
  }, [onTaskCreated]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getTasks();
      setTasks(response.data);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch tasks';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleTaskToggle = async (task: TodoTask) => {
    try {
      await apiClient.toggleTaskCompletion(task.id, !task.completed);
      // Refresh the task list to get updated data
      fetchTasks();

      if (onTaskUpdate) {
        // Update the task with the new completion status
        const updatedTask = { ...task, completed: !task.completed };
        onTaskUpdate(updatedTask);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update task';
      setError(errorMessage);
    }
  };

  const handleTaskDelete = async (taskId: string) => {
    try {
      await apiClient.deleteTask(taskId);
      setTasks(prevTasks => prevTasks.filter(task => task.id !== taskId));

      if (onTaskDelete) {
        onTaskDelete(taskId);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete task';
      setError(errorMessage);
    }
  };

  // Apply filters and sorting
  const filteredAndSortedTasks = tasks
    .filter(task => {
      if (filter === 'active') return !task.completed;
      if (filter === 'completed') return task.completed;
      return true;
    })
    .sort((a, b) => {
      if (sortBy === 'priority') {
        const priorityOrder = { high: 3, medium: 2, low: 1 };
        return (priorityOrder[b.priority as keyof typeof priorityOrder] || 0) -
               (priorityOrder[a.priority as keyof typeof priorityOrder] || 0);
      } else if (sortBy === 'title') {
        return a.title.localeCompare(b.title);
      } else { // sortBy === 'date'
        if (a.dueDate && b.dueDate) {
          return new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime();
        } else if (a.dueDate) {
          return -1;
        } else if (b.dueDate) {
          return 1;
        }
        return 0;
      }
    });

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="relative">
          <Loader2 className="h-12 w-12 animate-spin text-primary" />
          <div className="absolute inset-0 rounded-full bg-primary/20 blur-xl animate-pulse"></div>
        </div>
        <p className="mt-4 text-muted-foreground font-medium">Loading your tasks...</p>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="p-6 border-0 bg-linear-to-br from-destructive/10 to-red-500/10 backdrop-blur-xl shadow-2xl border-destructive/20">
        <div className="flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-destructive" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          <span className="text-destructive font-semibold">Error:</span>
        </div>
        <p className="mt-2 text-destructive">{error}</p>
        <button
          onClick={fetchTasks}
          className="mt-4 px-4 py-2 bg-linear-to-br from-destructive to-destructive/80 text-destructive-foreground rounded-lg hover:from-destructive/90 hover:to-destructive/70 transition-all"
        >
          Retry
        </button>
      </Card>
    );
  }

  if (filteredAndSortedTasks.length === 0) {
    return (
      <div className="text-center py-20">
        <div className="mx-auto w-40 h-40 rounded-full bg-linear-to-br from-primary/20 to-accent/20 flex items-center justify-center mb-8 relative">
          <div className="absolute inset-0 rounded-full bg-linear-to-br from-primary/10 to-accent/10 blur-xl animate-pulse"></div>
          <svg xmlns="http://www.w3.org/2000/svg" className="h-20 w-20 text-primary/60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <h3 className="text-3xl font-black bg-linear-to-br from-primary to-accent bg-clip-text text-transparent mb-3">No tasks found</h3>
        <p className="text-muted-foreground text-xl mb-8">Get started by adding a new task to your list</p>

        {/* Filter/Sort controls for empty state */}
        <div className="flex flex-wrap justify-center gap-4">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as 'all' | 'active' | 'completed')}
            className="px-4 py-3 rounded-xl border-0 bg-white/10 backdrop-blur-sm text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary transition-all border-border/30"
          >
            <option value="all" className="bg-card">All Tasks</option>
            <option value="active" className="bg-card">Active</option>
            <option value="completed" className="bg-card">Completed</option>
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'date' | 'priority' | 'title')}
            className="px-4 py-3 rounded-xl border-0 bg-white/10 backdrop-blur-sm text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary transition-all border-border/30"
          >
            <option value="date" className="bg-card">Sort by Date</option>
            <option value="priority" className="bg-card">Sort by Priority</option>
            <option value="title" className="bg-card">Sort by Title</option>
          </select>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 transition-all duration-300">
      {/* Filter and sort controls */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-5 bg-linear-to-br from-card/50 to-muted/30 backdrop-blur-xl rounded-xl border border-border/30">
        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
              filter === 'all'
                ? 'bg-linear-to-br from-primary to-accent text-primary-foreground shadow-lg hover:shadow-xl'
                : 'bg-white/10 text-foreground hover:bg-white/20'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('active')}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
              filter === 'active'
                ? 'bg-linear-to-br from-primary to-accent text-primary-foreground shadow-lg hover:shadow-xl'
                : 'bg-white/10 text-foreground hover:bg-white/20'
            }`}
          >
            Active
          </button>
          <button
            onClick={() => setFilter('completed')}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
              filter === 'completed'
                ? 'bg-linear-to-br from-primary to-accent text-primary-foreground shadow-lg hover:shadow-xl'
                : 'bg-white/10 text-foreground hover:bg-white/20'
            }`}
          >
            Completed
          </button>
        </div>

        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as 'date' | 'priority' | 'title')}
          className="px-4 py-2 rounded-xl border-0 bg-white/10 backdrop-blur-sm text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary transition-all border-border/30"
        >
          <option value="date" className="bg-card">Sort by Date</option>
          <option value="priority" className="bg-card">Sort by Priority</option>
          <option value="title" className="bg-card">Sort by Title</option>
        </select>
      </div>

      {/* Stats bar */}
      {/* <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-gradient-to-b from-card/40 to-muted/20 backdrop-blur rounded-xl border border-border/30">
        <div className="flex items-center gap-3 p-3 bg-white/5 rounded-lg backdrop-blur-sm border border-border/20">
          <div className="p-2 rounded-lg bg-destructive/20 backdrop-blur-sm">
            <Flag className="h-5 w-5 text-destructive" />
          </div>
          <div>
            <p className="text-sm text-muted-foreground">High Priority</p>
            <p className="text-lg font-bold text-foreground">{tasks.filter(t => t.priority === 'high' && !t.completed).length}</p>
          </div>
        </div>
        <div className="flex items-center gap-3 p-3 bg-white/5 rounded-lg backdrop-blur-sm border border-border/20">
          <div className="p-2 rounded-lg bg-warning/20 backdrop-blur-sm">
            <Calendar className="h-5 w-5 text-warning" />
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Overdue</p>
            <p className="text-lg font-bold text-foreground">{tasks.filter(t => t.dueDate && new Date(t.dueDate) < new Date() && !t.completed).length}</p>
          </div>
        </div>
        <div className="flex items-center gap-3 p-3 bg-white/5 rounded-lg backdrop-blur-sm border border-border/20">
          <div className="p-2 rounded-lg bg-accent/20 backdrop-blur-sm">
            <Hash className="h-5 w-5 text-accent" />
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Categorized</p>
            <p className="text-lg font-bold text-foreground">{tasks.filter(t => t.category).length}</p>
          </div>
        </div>
      </div> */}

      {/* Task list */}
      <div className="space-y-4">
        {filteredAndSortedTasks.map(task => (
          <TaskItem
            key={task.id}
            task={task}
            onToggle={handleTaskToggle}
            onDelete={handleTaskDelete}
          />
        ))}
      </div>
    </div>
  );
};

export default TaskList;