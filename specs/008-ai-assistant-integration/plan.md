# Implementation Plan: AI Agent + MCP Integration (Todo AI Assistant)

**Feature**: 008-ai-assistant-integration
**Created**: 2026-02-06
**Status**: Draft
**Author**: Claude Sonnet 4.5

## Technical Context

This plan outlines the implementation of an AI-powered Todo Assistant that integrates with the existing Phase-2 Todo application using Agents SDK and MCP (Model Context Protocol) server. The solution will enable natural language interaction with todo management functionality through secure API bridges and real-time UI updates.

### Architecture Overview

- **Agent Layer**: OpenAI Agents SDK with custom tools for todo CRUD operations and user context
- **MCP Server**: Dedicated server exposing database operations as secure tools for the agent
- **Backend**: FastAPI with agent chat endpoint and MCP client integration
- **Frontend**: Next.js with ChatKit integration for conversational UI
- **Data Layer**: SQLModel ORM with JWT-based authentication for multi-user isolation

### Unknowns & Dependencies

- **Agent Tool Structure**: RESOLVED - Follows OpenAI Agents SDK function tool schema specification
- **MCP Server Integration**: RESOLVED - Separate MCP server communicating with backend via secure API calls
- **JWT Token Flow**: RESOLVED - JWT validated at backend, user context securely passed to agent
- **Real-time UI Updates**: RESOLVED - WebSocket-based updates combined with optimistic UI
- **Error Handling Strategy**: RESOLVED - Layered error handling with specific error types at each layer

## Constitution Check

This implementation must comply with all Phase III constitutional principles:

- **Spec-Driven Development First**: Implementation follows the approved specification
- **Zero Manual Coding**: All code generated through Claude Code tools
- **Backward Compatibility**: 100% preservation of Phase-2 functionality maintained
- **Clear Separation of Concerns**: Proper separation between agent, frontend, backend, and data layers
- **Secure Multi-User Design**: Proper authentication and authorization for all users
- **RESTful API Contracts**: Standardized response schemas applied
- **AI-First Development**: Follows agentic dev stack workflow
- **MCP Server Integration**: Proper integration with MCP tools
- **Statelessness Requirement**: Server remains stateless with DB-persisted state
- **AI Chatbot Features**: Maps natural language commands to system operations

## Gate Evaluation

✅ **Passed**: All constitutional requirements can be met with proposed architecture
✅ **Passed**: Backward compatibility with Phase-2 features is maintained
✅ **Passed**: Proposed architecture aligns with technology stack requirements
⚠️ **Needs Verification**: MCP server integration approach will be clarified during research phase
⚠️ **Needs Verification**: Agent tool schema definitions will be confirmed during research phase

## Phase 0: Outline & Research

### Research Summary

#### 1. Agent Tool Structure
Based on research, the agent tools will follow the OpenAI Functions schema specification with:
- Proper JSON Schema definitions for parameters
- Clear descriptions for agent understanding
- Secure execution environment with validation
- Integration with existing SQLModel data models

#### 2. MCP Server Architecture
The MCP server will be implemented as a separate service that:
- Exposes backend functionality via the official MCP protocol
- Communicates with the main backend via secure API calls
- Implements proper authentication and authorization checks
- Maintains isolation between agent and direct database access

#### 3. JWT Authentication Flow
The authentication flow will follow security best practices:
- JWT tokens validated at the backend API layer
- User context securely passed to the agent service
- MCP server receives user-specific requests only through authenticated backend
- Multi-user isolation maintained at every layer

#### 4. Real-time UI Updates
The UI synchronization will use a combination of:
- WebSocket connections for real-time updates
- Optimistic UI updates for immediate feedback
- Server-sent events for agent-initiated changes
- Consistency checks to handle edge cases

#### 5. Error Handling & Safe Execution
The error handling strategy will include:
- Layered error handling at agent, MCP, and backend layers
- Safe fallbacks when tools fail
- Clear error messages for users
- Comprehensive logging for debugging and monitoring

## Phase 1: Design & Contracts

### Agent Architecture Design

#### Agent Layer
- **AgentService**: Main service to manage agent lifecycle and tool registration
- **ToolDefinitions**: Schema definitions for todo operations (`list_todos`, `add_todo`, `update_todo`, `delete_todo`, `get_user_context`)
- **ToolExecutor**: Secure execution environment for agent tools with validation and authorization
- **ConversationManager**: Manages agent session state and message history

#### MCP Server Design
- **MCPServer**: Dedicated service implementing MCP specification
- **ToolProviders**: Specific implementations for todo operations
- **SecurityLayer**: Validates requests and enforces user access controls
- **DBAdapters**: Interfaces between MCP tools and SQLModel operations

### Backend Architecture

#### API Layer
- `/agent/chat`: Streaming endpoint for agent interactions with JWT validation
- `/mcp/`: MCP server endpoint for tool access (potentially separate service)

#### Service Layer
- `AgentService`: Orchestrates agent operations
- `TodoService`: Handles todo-specific business logic with security checks
- `MCPService`: Manages MCP server communication

### Frontend Architecture

#### Components
- `ChatInterface`: Main ChatKit integration component
- `TodoStreamHandler`: Manages real-time updates to todo list from agent actions
- `AuthHandler`: Ensures JWT tokens are properly attached to requests

### Data Flow Map

1. **User Input**: Chat message received in frontend
2. **Authentication**: JWT token validated in backend
3. **Agent Processing**: Message sent to OpenAI Agent for interpretation
4. **Tool Selection**: Agent determines appropriate tool(s) to call
5. **MCP Communication**: Secure communication to MCP server for DB operations
6. **Database Operation**: Secure DB operation performed with user context
7. **Response Generation**: Agent receives DB result and generates response
8. **Streaming Response**: Response streamed back to frontend
9. **UI Update**: Frontend updates todo list to reflect changes

### Security Layer

- JWT token validation at entry points
- User context enforcement in all agent operations
- Tool call authorization and validation
- Input sanitization for all agent interactions
- Rate limiting for agent endpoints

### Integration with Existing Architecture

- Maintain compatibility with existing Phase-2 Todo functionality
- Leverage existing authentication and database infrastructure
- Extend API contracts without breaking changes
- Preserve existing data models while adding agent capabilities

## Phase 2: Implementation Strategy

### Implementation Order

1. **Foundation Layer**: Create base agent and MCP server infrastructure
2. **Tool Definitions**: Define and implement agent tools for todo operations
3. **MCP Server**: Implement secure MCP server with authentication
4. **Backend Integration**: Connect agent to backend via MCP
5. **Frontend Integration**: Add ChatKit UI and connect to backend
6. **Real-time Updates**: Implement UI synchronization for agent changes
7. **Security Hardening**: Add comprehensive validation and authorization
8. **Testing & Validation**: Verify all components work together

### Quality Validation Criteria

- All agent tools execute deterministically and safely
- Multi-user data isolation maintained throughout
- Agent cannot affect existing Phase-2 functionality
- Frontend UX remains consistent with existing UI
- Tool calls are properly logged and monitored
- Error conditions are handled gracefully with user-friendly messages

### Testing Strategy

- **Unit Tests**: Individual tool functionality and validation
- **Integration Tests**: Agent-to-MCP-to-backend communication
- **Security Tests**: Authentication, authorization, and multi-user isolation
- **End-to-End Tests**: Complete user journey from chat input to todo update
- **Performance Tests**: Agent response times and concurrent user handling

## Risk Mitigation

- **Agent Safety**: Implement strict validation and authorization for all tool calls
- **Data Consistency**: Ensure ACID properties of database operations initiated by agents
- **Authentication Flow**: Maintain secure JWT token handling throughout the system
- **System Stability**: Prevent agent errors from affecting existing functionality
- **Performance**: Implement proper rate limiting and caching for agent operations