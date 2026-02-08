import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include JWT token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor to handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        // If the error is 401 and not already tried refreshing
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (!refreshToken) {
              throw new Error('No refresh token available');
            }

            // Call refresh endpoint
            const refreshResponse = await axios.post(`${API_BASE_URL}/auth/refresh`, {
              refresh_token: refreshToken,
            });

            const { access_token, refresh_token: newRefreshToken } = refreshResponse.data;

            // Update tokens in storage
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', newRefreshToken);

            // Retry original request with new token
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            return this.client(originalRequest);
          } catch (refreshError) {
            // If refresh fails, clear tokens and redirect to login
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/signin';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Authentication endpoints
  register(userData: { name: string; email: string; password: string }) {
    return this.client.post('/auth/register', userData);
  }

  login(credentials: { email: string; password: string }) {
    return this.client.post('/auth/login', credentials);
  }

  refresh(refreshToken: string) {
    return this.client.post('/auth/refresh', { refresh_token: refreshToken });
  }

  getMe() {
    return this.client.get('/auth/me');
  }

  // Task endpoints
  getTasks() {
    return this.client.get('/api/tasks');
  }

  createTask(taskData: { title: string; description?: string; category?: string; priority?: 'low' | 'medium' | 'high'; dueDate?: string }) {
    return this.client.post('/api/tasks', taskData);
  }

  getTask(taskId: string) {
    return this.client.get(`/api/tasks/${taskId}`);
  }

  updateTask(taskId: string, taskData: { title?: string; description?: string; category?: string; priority?: 'low' | 'medium' | 'high'; dueDate?: string; completed?: boolean }) {
    return this.client.put(`/api/tasks/${taskId}`, taskData);
  }

  deleteTask(taskId: string) {
    return this.client.delete(`/api/tasks/${taskId}`);
  }

  toggleTaskCompletion(taskId: string, completed: boolean) {
    return this.client.patch(`/api/tasks/${taskId}/complete`, { completed });
  }
}

export const apiClient = new ApiClient();