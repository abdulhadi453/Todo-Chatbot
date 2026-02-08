'use client';

import React, { useEffect, useState, useRef } from 'react';
import ProtectedRoute from '../../src/components/protected-route';
import Layout from '../../src/components/layout/layout';
import TaskList from '../../src/components/task/task-list';
import AddTaskForm from '../../src/components/task/add-task-form';
import { TodoTask } from '../../src/types/task';
import { apiClient } from '../../src/services/api-client';
import { Card, CardContent, CardHeader, CardTitle } from '../../src/components/ui/card';
import { Calendar, Flag, Hash, CheckCircle, BarChart3, TrendingUp, Users, HighlighterIcon } from 'lucide-react';

const DashboardPage = () => {
  const handleTaskAdded = (task: TodoTask) => {
    // Optionally update the task list or show a success message
    console.log('Task added:', task);
  };

  const handleTaskUpdated = (task: TodoTask) => {
    // Handle task updates
    console.log('Task updated:', task);
  };

  const [tasks, setTasks] = useState<TodoTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleTaskDeleted = (taskId: string) => {
    // Handle task deletion
    console.log('Task deleted:', taskId);
    // Refresh the task list after deletion
    fetchTasks();
  };

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

  // Calculate stats from tasks
  const completedTasks = tasks.filter(t => t.completed).length;
  const categories = tasks.filter(t => t.category).length;
  const highPriorityTasks = tasks.filter(t => t.priority === 'high' && !t.completed).length;
  const overdueTasks = tasks.filter(t => t.dueDate && new Date(t.dueDate) < new Date() && !t.completed).length;
  const completedToday = tasks.filter(t =>
    t.completed &&
    t.updatedAt &&
    new Date(t.updatedAt).toDateString() === new Date().toDateString()
  ).length;
  const productivity = completedTasks * 4.87 

  useEffect(() => {
    fetchTasks();
  }, []);

  return (
    <ProtectedRoute>
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header Section */}
          <div className="mb-10">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6 mb-8">
              <div>
                <h1 className="text-3xl md:text-4xl font-bold text-foreground">
                  Dashboard
                </h1>
                <p className="text-muted-foreground text-lg mt-2">Manage your tasks efficiently</p>
              </div>

              <div className="flex items-center gap-4">
                <div className="bg-muted p-3 rounded-lg border">
                  <BarChart3 className="h-6 w-6 text-primary" />
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">Productivity</p>
                  <p className="text-xl font-bold text-foreground">+{productivity}%</p>
                </div>
              </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card className="border bg-card shadow-sm">
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="bg-primary/10 p-2 rounded-lg">
                    <CheckCircle className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Completed</p>
                    <p className="text-xl font-bold text-foreground">{completedTasks}</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="border bg-card shadow-sm">
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="bg-warning/10 p-2 rounded-lg">
                    <Flag className="h-6 w-6 text-warning" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">High Priority</p>
                    <p className="text-xl font-bold text-foreground">{highPriorityTasks}</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="border bg-card shadow-sm">
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="bg-destructive/10 p-2 rounded-lg">
                    <Calendar className="h-6 w-6 text-destructive" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Overdue</p>
                    <p className="text-xl font-bold text-foreground">{overdueTasks}</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="border bg-card shadow-sm">
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="bg-success/10 p-2 rounded-lg">
                    <TrendingUp className="h-6 w-6 text-success" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Completed Today</p>
                    <p className="text-xl font-bold text-foreground">{completedToday}</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
            {/* Main Content - Task List */}
            <div className="lg:col-span-3">
              <Card className="border bg-card shadow-sm">
                <CardHeader className="pb-4">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-0">
                    <CardTitle className="text-2xl font-bold text-foreground">
                      Your Tasks
                    </CardTitle>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <CheckCircle className="h-4 w-4 text-success" />
                        <span>Completed</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Flag className="h-4 w-4 text-warning" />
                        <span>Active</span>
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <TaskList
                    onTaskUpdate={handleTaskUpdated}
                    onTaskDelete={handleTaskDeleted}
                    onTaskCreated={fetchTasks}
                  />
                </CardContent>
              </Card>
            </div>

            {/* Sidebar - Add Task Form and Quick Stats */}
            <div className="space-y-6">
              {/* Add Task Form */}
              <Card className="border bg-card shadow-sm">
                <CardHeader className="pb-4">
                  <CardTitle className="text-xl flex items-center gap-2 font-bold text-foreground">
                    <Flag className="h-5 w-5 text-primary" />
                    Add New Task
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <AddTaskForm
                    onTaskAdded={handleTaskAdded}
                    onTaskCreated={fetchTasks}
                  />
                </CardContent>
              </Card>

              {/* Quick Stats */}
              <Card className="border bg-card shadow-sm">
                <CardHeader className="pb-4">
                  <CardTitle className="text-xl flex items-center gap-2 font-bold text-foreground">
                    <BarChart3 className="h-5 w-5 text-primary" />
                    Quick Stats
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 rounded-lg bg-muted">
                      <div className="flex items-center gap-2">
                        <Flag className="h-4 w-4 text-destructive" />
                        <span className="text-sm font-medium text-foreground">High Priority</span>
                      </div>
                      <span className="text-lg font-bold text-destructive">{highPriorityTasks}</span>
                    </div>
                    <div className="flex items-center justify-between p-3 rounded-lg bg-muted">
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4 text-warning" />
                        <span className="text-sm font-medium text-foreground">Overdue</span>
                      </div>
                      <span className="text-lg font-bold text-warning">{overdueTasks}</span>
                    </div>
                    <div className="flex items-center justify-between p-3 rounded-lg bg-muted">
                      <div className="flex items-center gap-2">
                        <Hash className="h-4 w-4 text-accent" />
                        <span className="text-sm font-medium text-foreground">Categories</span>
                      </div>
                      <span className="text-lg font-bold text-accent">{categories}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Productivity Tips */}
              <Card className="border bg-card shadow-sm">
                <CardHeader className="pb-4">
                  <CardTitle className="text-xl flex items-center gap-2 font-bold text-foreground">
                    <CheckCircle className="h-5 w-5 text-success" />
                    Productivity Tips
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="text-sm text-foreground space-y-3">
                    <li className="flex items-start gap-2">
                      <div className="mt-1.5 h-2 w-2 rounded-full bg-primary shrink-0" />
                      <span>Click the checkbox to mark tasks as complete</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="mt-1.5 h-2 w-2 rounded-full bg-primary shrink-0" />
                      <span>Use categories to organize your tasks</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="mt-1.5 h-2 w-2 rounded-full bg-primary shrink-0" />
                      <span>Set priorities to focus on important tasks</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="mt-1.5 h-2 w-2 rounded-full bg-primary shrink-0" />
                      <span>Add due dates to stay on schedule</span>
                    </li>
                  </ul>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </Layout>
    </ProtectedRoute>
  );
};

export default DashboardPage;