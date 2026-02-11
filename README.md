# Full-Stack Todo Application

## 🚀 Features

- **Frontend**: Next.js 14 with App Router, TypeScript, Tailwind CSS
- **Backend**: FastAPI with JWT authentication and SQLModel
- **Database**: Neon PostgreSQL with user-scoped data
- **Authentication**: Secure JWT-based auth with token refresh
- **Task Management**: Full CRUD operations (create, read, update, delete, toggle completion)
- **AI Chatbot**: Interactive AI assistant for task management (Phase III)
- **Advanced AI Features**: Natural language processing, tool calling, context-aware responses
- **Agent Integration**: OpenAI Agent SDK with MCP (Model Context Protocol) server
- **Responsive UI**: Works on desktop and mobile devices
- **Security**: Cross-user access prevention and secure token handling

## 🛠️ Tech Stack

### Frontend
- Next.js 14 with App Router
- TypeScript
- Tailwind CSS
- Axios for API calls

### Backend
- Python 3.13+ with FastAPI
- SQLModel for database modeling
- JWT for authentication
- Neon PostgreSQL for data storage

## 📋 Prerequisites

- Node.js 18+ (for frontend)
- Python 3.13+ (for backend)
- Pip package manager
- Access to Neon PostgreSQL database

## 🚀 Setup & Installation

### Backend Setup

1. **Navigate to the project directory**
   ```bash
   cd Full-Stack-Todo-App
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install backend dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Configure backend environment variables**

   Create a `.env` file in the backend root:
   ```env
   # JWT Configuration
   JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7

   # Database Configuration (from your Neon PostgreSQL setup)
   DATABASE_URL=postgresql://neondb_owner:your_password@ep-xxxxxx.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require

   # OpenAI API Configuration (for AI agent functionality)
   OPENAI_API_KEY=your-openai-api-key-here
   ```

5. **Run the backend server**
   ```bash
   cd backend
   python run_server.py
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to the frontend directory**
   ```bash
   cd frontend
   ```

2. **Install frontend dependencies**
   ```bash
   npm install
   ```

3. **Configure frontend environment variables**

   Create a `.env.local` file in the frontend root:
   ```env
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```

4. **Run the frontend development server**
   ```bash
   npm run dev
   ```

5. **Access the application**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### AI Agent Setup (Optional)

To enable the AI assistant functionality:

1. **Obtain an OpenAI API key**
   - Sign up at [OpenAI](https://platform.openai.com/) and create an API key
   - Add the API key to your backend `.env` file as shown above

2. **The AI agent is automatically integrated** into the application when the OpenAI API key is configured
   - The agent is accessible through the chat interface
   - It can perform natural language processing for todo operations
   - It supports tool calling for list, add, update, and delete operations

## 📡 API Endpoints

The backend API provides the following endpoints:

### Authentication Endpoints
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Authenticate and get tokens
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user info

### Todo Endpoints (require authentication)
- `GET /api/{user_id}/tasks` - Get all tasks for a user
- `POST /api/{user_id}/tasks` - Create a new task for a user
- `GET /api/{user_id}/tasks/{id}` - Get a specific task
- `PUT /api/{user_id}/tasks/{id}` - Update a specific task
- `DELETE /api/{user_id}/tasks/{id}` - Delete a specific task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle task completion status

### Chat Endpoints (require authentication)
- `POST /api/{user_id}/chat` - Send message and get AI response
- `GET /api/{user_id}/conversations` - Get user's conversations
- `GET /api/{user_id}/conversations/{conversation_id}` - Get specific conversation
- `DELETE /api/{user_id}/conversations/{conversation_id}` - Delete conversation

## 🧪 Running Tests

### Backend Tests
```bash
# Install test dependencies
pip install pytest httpx

# Run auth unit tests
python -m pytest backend/tests/auth/

# Run auth integration tests
python -m pytest backend/tests/integration/

# Run all tests
python -m pytest backend/tests/
```

## 🔐 Security Best Practices

- Use strong, unique JWT secret keys in production
- Ensure user_id in JWT matches the user_id in URL parameters
- Sanitize all user inputs to prevent injection attacks
- Set secure HTTP-only cookies for tokens when possible

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT