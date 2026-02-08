'use client';

import React from 'react';
import { TodoTask } from '../../types/task';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';
import { Check, X, Calendar, Hash, Flag, AlertCircle, Clock } from 'lucide-react';

interface TaskItemProps {
  task: TodoTask;
  onToggle: (task: TodoTask) => void;
  onDelete: (taskId: string) => void;
}

const getPriorityColor = (priority: string) => {
  switch (priority.toLowerCase()) {
    case 'high':
      return 'bg-destructive/20 text-destructive-foreground border-destructive/30';
    case 'medium':
      return 'bg-warning/20 text-warning-foreground border-warning/30';
    case 'low':
      return 'bg-success/20 text-success-foreground border-success/30';
    default:
      return 'bg-secondary text-secondary-foreground border-secondary/30';
  }
};

const TaskItem = ({ task, onToggle, onDelete }: TaskItemProps) => {
  const handleToggle = () => {
    onToggle(task);
  };

  const handleDelete = () => {
    onDelete(task.id);
  };

  // Determine if the task is overdue
  const isOverdue = task.dueDate && new Date(task.dueDate) < new Date() && !task.completed;

  return (
    <Card
      className={`group hover:shadow-2xl transition-all duration-500 border-l-4 ${
        task.completed
          ? 'border-l-green-500/70 bg-linear-to-r from-green-50/20 to-emerald-50/20 dark:from-green-950/10 dark:to-emerald-950/10 opacity-80'
          : isOverdue
            ? 'border-l-destructive/70 bg-linear-to-r from-destructive/5 to-red-50/30 dark:from-destructive/10 dark:to-red-950/10'
            : 'border-l-primary/50 hover:border-l-primary bg-linear-to-r from-card/80 to-muted/30'
      } backdrop-blur-sm`}
      role="listitem"
      aria-labelledby={`task-title-${task.id}`}
    >
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-4 flex-1">
            <button
              onClick={handleToggle}
              className={`mt-1 shrink-0 hover:bg-green-500 hover:cursor-pointer h-8 w-8 rounded-full pl-0.5 border-2 flex items-center justify-center transition-all duration-300 ${
                task.completed
                  ? 'bg-linear-to-r from-success to-emerald-500 border-success text-white shadow-lg'
                  : 'border-input hover:border-primary hover:shadow-md'
              }`}
              aria-checked={task.completed}
              role="checkbox"
              tabIndex={0}
              aria-describedby={`task-desc-${task.id}`}
              title={task.completed ? "Mark as incomplete" : "Mark as complete"}
            >&#10004;
              {task.completed ? <Check className="h-4 w-4" /> : <div className="w-2 h-2 bg-transparent" />}
            </button>

            <div className="flex-1 min-w-0">
              <h3
                id={`task-title-${task.id}`}
                className={`text-lg font-semibold transition-all ${
                  task.completed
                    ? 'line-through text-muted-foreground'
                    : isOverdue
                      ? 'text-destructive font-bold'
                      : 'text-foreground'
                }`}
              >
                {task.title}
              </h3>

              {task.description && (
                <p
                  id={`task-desc-${task.id}`}
                  className={`mt-1 text-sm transition-all ${
                    task.completed
                      ? 'line-through text-muted-foreground'
                      : isOverdue
                        ? 'text-destructive'
                        : 'text-muted-foreground'
                  }`}
                >
                  {task.description}
                </p>
              )}

              <div className="mt-3 flex flex-wrap gap-2" role="group" aria-label="Task details">
                {task.category && (
                  <span
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-secondary/60 text-secondary-foreground border border-secondary/30 backdrop-blur-sm"
                    aria-label={`Category: ${task.category}`}
                  >
                    <Hash className="h-3 w-3" />
                    {task.category}
                  </span>
                )}

                {task.priority && (
                  <span
                    className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border backdrop-blur-sm ${getPriorityColor(task.priority)}`}
                    aria-label={`Priority: ${task.priority}`}
                  >
                    <Flag className="h-3 w-3" />
                    {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
                  </span>
                )}

                {task.completed && (
                  <span
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-success/20 text-success-foreground border border-success/30 backdrop-blur-sm"
                    aria-label="Completed"
                  >
                    <Check className="h-3 w-3" />
                    Completed
                  </span>
                )}
                {task.dueDate && (
                  <span
                    className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border backdrop-blur-sm ${
                      isOverdue
                        ? 'bg-destructive/20 text-destructive-foreground border-destructive/30'
                        : 'bg-accent/20 text-accent-foreground border-accent/30'
                    }`}
                    aria-label={`Due date: ${new Date(task.dueDate).toLocaleDateString()}`}
                  >
                    {isOverdue ? <AlertCircle className="h-3 w-3" /> : <Calendar className="h-3 w-3" />}
                    {new Date(task.dueDate).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>
          </div>

          <Button
            variant="ghost"
            size="sm"
            onClick={handleDelete}
            className="ml-2 opacity-60 hover:opacity-100 transition-opacity text-destructive hover:text-destructive-foreground focus:outline-none focus:ring-2 focus:ring-destructive rounded-full h-8 w-8 flex items-center justify-center hover:bg-red-500"
            aria-label={`Delete task: ${task.title}`}
          >
            &#10006;
            <X className="h-4 w-4 hover:text-red-600" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default TaskItem;