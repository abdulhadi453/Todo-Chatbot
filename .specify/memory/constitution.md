<!--
Sync Impact Report:
Version change: 1.0.0 -> 2.0.0 (Major update - adding AI functionality)
Added sections: VII. AI-First Development, VIII. MCP Server Integration, IX. Statelessness Requirement, X. AI Chatbot Features
Modified principles: I. Spec-Driven Development First (expanded), III. Backward Compatibility (updated for AI), IV. Clear Separation of Concerns (expanded for AI), V. Secure Multi-User Design (enhanced for AI), VI. RESTful API Contracts (expanded for AI chat)
Templates requiring updates:
  - .specify/templates/plan-template.md: ⚠ pending
  - .specify/templates/spec-template.md: ⚠ pending
  - .specify/templates/tasks-template.md: ⚠ pending
  - .specify/templates/commands/*.md: ⚠ pending
Follow-up TODOs: None
-->
# Phase III AI Todo Chatbot Constitution

## Core Principles

### I. Spec-Driven Development First
Every feature must start with an approved specification document. No implementation work begins without a complete, unambiguous spec that defines requirements, acceptance criteria, and constraints. Specs must be written in Markdown and follow the project's spec template structure. All AI features must follow the same Spec-Driven Development process as traditional features.

### II. Zero Manual Coding
All source code must be generated exclusively through Claude Code tools. No manual editing of source files is permitted. This ensures consistency, traceability, and adherence to architectural patterns. This applies to all AI, frontend, and backend code generation.

### III. Backward Compatibility
All Phase III implementations must maintain backward compatibility with Phase I and Phase II domain behavior. Core Todo operations (add, update, delete, list, toggle completion) must preserve their original semantics while extending functionality for AI interactions. Existing web UI features must continue to work unchanged.

### IV. Clear Separation of Concerns
The application must maintain strict separation between frontend (Next.js), AI components (OpenAI Agents), backend (FastAPI), and data layers (Neon PostgreSQL). AI functionality must be implemented through MCP server tools that interact with the existing backend services. Communication between layers must occur only through well-defined HTTP contracts and API endpoints.

### V. Secure Multi-User Design
All features must be designed for multi-user environments by default. User authentication and authorization must be enforced at all levels. No cross-user data access is permitted under any circumstances. AI agents must inherit user permissions and only access tasks belonging to the authenticated user.

### VI. RESTful API Contracts
All API endpoints must follow RESTful principles and be deterministic, versionable, and well-documented. The core API contract must include endpoints for CRUD operations on user-scoped tasks with proper HTTP method usage. Additionally, a stateless chat endpoint must be available at `POST /api/{user_id}/chat` that accepts `conversation_id` (optional) and `message` (required), and returns `conversation_id`, `response`, and `tool_calls`.

### VII. AI-First Development
All new AI features must follow **Spec-Driven Development** and **Agentic Dev Stack workflow**. All AI behavior must be stateless on the server and use MCP tools for task operations. AI agents are authorized through the existing Better Auth system. All AI features must be generated via Claude Code with no manual coding.

### VIII. MCP Server Integration
The AI functionality must be implemented using an MCP server that exposes specific tools: `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task` with clearly defined parameters and expected outputs. The MCP server must be built using the official MCP SDK and serve as the bridge between AI agents and the existing task management system.

### IX. Statelessness Requirement
The server must remain stateless for AI operations. Conversation state must be persisted in the database but not maintained in server memory. The AI system must be able to reconstruct conversation context from stored data at any time. All conversation management must occur through database interactions.

### X. AI Chatbot Features
The application must implement an AI-powered Todo Chatbot that maps natural language commands to MCP tools. The bot must support intelligent task creation, listing, updating, completing, and deleting based on user conversations. The frontend must integrate OpenAI ChatKit for seamless conversation experiences.

## Technology Stack Requirements

### Frontend
- Framework: Next.js 16+ using App Router
- Integration: OpenAI ChatKit for conversational UI
- Responsive design principles must be followed
- All user interface components must be accessible and mobile-friendly

### Backend
- Framework: Python FastAPI
- AI Framework: OpenAI Agents SDK for conversational AI
- Authentication: Better Auth with JWT token-based authentication
- All API endpoints must require valid JWT tokens in Authorization headers
- Token verification must use shared secrets and proper signature validation

### MCP Server
- SDK: Official MCP SDK
- Tools exposed: `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`
- Parameters and expected outputs must be well-documented
- Tools must integrate with existing task management system

### Database
- Database: Neon Serverless PostgreSQL
- ORM: SQLModel for data access and schema management
- All data operations must be user-scoped and include proper foreign key relationships
- Additional tables required: `Conversations` (user_id, id, created_at, updated_at) and `Messages` (user_id, id, conversation_id, role, content, created_at)

### Authentication Flow
1. User authentication via Better Auth creates sessions and issues JWT tokens
2. Frontend includes JWT tokens in Authorization: Bearer <token> headers
3. Backend verifies token signatures and extracts user identity
4. All data access must be filtered by authenticated user ID
5. Cross-user access attempts must return appropriate HTTP error codes
6. AI agents must inherit user authentication context and permissions

## Development Workflow & Quality Standards

### Feature Development Process
1. Create comprehensive Markdown specification
2. Develop architectural plan with trade-off analysis
3. Break down into testable tasks
4. Generate implementation code via Claude Code
5. Validate against acceptance criteria

### Code Quality Requirements
- All code must follow project's coding standards
- Comprehensive error handling and input validation
- Proper logging and observability
- Security best practices (no hardcoded secrets, proper authentication)
- AI-specific error handling and confirmation messaging

### Testing Requirements
- Unit tests for all business logic
- Integration tests for API endpoints
- End-to-end tests for critical user flows
- Security testing for authentication and authorization
- AI functionality testing for conversation handling

### AI-Specific Requirements
- Conversation state persistence in database
- Server statelessness verification
- MCP tool integration testing
- Natural language command mapping validation
- Multi-user security validation for AI interactions

## Governance

This constitution represents the supreme authority for all Phase III development work. All pull requests, code reviews, and implementation decisions must verify compliance with these principles.

### Amendment Process
- Constitution changes require formal documentation
- Version increments follow semantic versioning (MAJOR.MINOR.PATCH)
- All amendments must be approved through the project's governance process
- Migration plans required for breaking changes

### Compliance Requirements
- All team members must adhere to these principles
- Non-compliance must be documented and addressed
- Complexity must be justified against these principles
- Use constitution as primary reference for development guidance

**Version**: 2.0.0 | **Ratified**: 2026-02-06 | **Last Amended**: 2026-02-06