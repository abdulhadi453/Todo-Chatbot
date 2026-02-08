# Quickstart Guide: AI Agent + MCP Integration (Todo AI Assistant)

**Feature**: 008-ai-assistant-integration
**Created**: 2026-02-06
**Status**: Complete

## Overview
This guide provides essential information to implement the AI-powered Todo Assistant using OpenAI Agents SDK and MCP (Model Context Protocol) server. The implementation integrates with the existing Phase-2 Todo application while maintaining full backward compatibility.

## Prerequisites
- Python 3.9+ with FastAPI for backend development
- Node.js 18+ with Next.js 16+ for frontend development
- Neon Serverless PostgreSQL database
- OpenAI API key for agent functionality
- Better Auth for authentication (from Phase II)
- SQLModel for database operations

## Implementation Steps

### 1. MCP Server Setup
1. Create the MCP server package in `/backend/mcp/`
2. Implement tool providers for todo CRUD operations
3. Configure authentication and authorization for tools
4. Set up communication between MCP server and main backend
5. Test MCP server connectivity and tool execution

### 2. Agent Integration
1. Implement the AgentService in `/backend/services/agent_service.py`
2. Define agent tools that map to todo operations
3. Connect agent to MCP server for secure database access
4. Implement conversation management and session handling
5. Add proper error handling for agent operations

### 3. Backend API Endpoints
1. Create the agent chat endpoint `/api/{user_id}/agent/chat` in `/backend/routers/agent.py`
2. Implement JWT validation for multi-user isolation
3. Add rate limiting and security measures
4. Implement streaming response functionality for chat interface
5. Connect to agent service for processing

### 4. Frontend Integration
1. Add ChatKit UI component for conversational interface
2. Implement authentication context integration
3. Connect frontend to backend agent API endpoints
4. Handle real-time updates when agent modifies todos
5. Implement error handling and loading states

### 5. Testing & Validation
1. Test agent responses to natural language commands
2. Verify multi-user data isolation
3. Confirm all todo operations work through agent
4. Validate error handling scenarios
5. Ensure backward compatibility with Phase-II features

## Configuration Requirements

### Environment Variables
```
OPENAI_API_KEY=sk-...
MCP_SERVER_URL=http://localhost:8080
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=postgresql://...
AGENT_MODEL=gpt-4-turbo-preview  # or other compatible model
```

### Security Configuration
- JWT token validation must verify user_id matches authenticated user
- Agent tools must only allow operations on user's own data
- MCP server must validate all incoming requests
- Rate limiting applied to prevent abuse of agent services

### Performance Tuning
- Agent timeout configuration (recommended: 30 seconds)
- Conversation history length limits
- Database connection pooling for MCP server
- Caching for frequently accessed context data

## Key Components

### Agent Tools
- `list_todos`: Retrieve user's todo items
- `add_todo`: Create new todo item
- `update_todo`: Modify existing todo item
- `delete_todo`: Remove todo item
- `get_user_context`: Retrieve user-specific information

### Data Flow
1. User sends message through ChatKit UI
2. Frontend authenticates with JWT and sends to backend
3. Backend validates JWT and forwards to agent service
4. Agent determines appropriate tools and calls MCP server
5. MCP server executes secure database operations
6. Agent generates response and streams back to frontend
7. Frontend updates UI to reflect any changes

## Testing Strategy
- Unit tests for individual agent tools
- Integration tests for agent-MCP-backend flow
- End-to-end tests for complete user journeys
- Security tests for multi-user isolation
- Performance tests for response times
- Regression tests for Phase-II functionality

## Troubleshooting Common Issues
- Agent not calling tools: Verify MCP server connectivity and tool definitions
- Authentication failures: Check JWT token format and validation
- Slow responses: Monitor OpenAI API quota and consider caching
- Database access errors: Verify MCP server permissions and connection
- UI synchronization: Confirm WebSocket connections and event handling