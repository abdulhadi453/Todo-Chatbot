# Data Model: AI Agent + MCP Integration (Todo AI Assistant)

**Feature**: 008-ai-assistant-integration
**Created**: 2026-02-06
**Status**: Complete

## Entity Definitions

### AgentSession
**Description**: Represents a session between a user and the AI agent, tracking conversation state
- **id**: UUID (Primary Key) - Unique identifier for the session
- **user_id**: UUID (Foreign Key) - Links to the authenticated user
- **created_at**: DateTime - Timestamp when session was created
- **updated_at**: DateTime - Timestamp of last activity
- **metadata**: JSON (Optional) - Additional session-specific data

**Relationships**:
- Many-to-One: User has many AgentSessions
- One-to-Many: AgentSession has many AgentMessages

**Validation Rules**:
- user_id must reference an existing user
- created_at must be before or equal to updated_at
- Metadata follows JSON schema validation

### AgentMessage
**Description**: Represents a message in an agent conversation (user input or AI response)
- **id**: UUID (Primary Key) - Unique identifier for the message
- **session_id**: UUID (Foreign Key) - Links to the session this message belongs to
- **role**: String (Enum: 'user', 'assistant', 'tool') - Specifies the message origin
- **content**: Text - The actual message content
- **timestamp**: DateTime - When the message was created
- **tool_calls**: JSON (Optional) - Details of any tool calls made in the message
- **tool_call_results**: JSON (Optional) - Results from tool executions

**Relationships**:
- Many-to-One: AgentMessage belongs to one AgentSession
- Many-to-One: AgentMessage may have relations to other entities through tool operations

**Validation Rules**:
- session_id must reference an existing AgentSession
- role must be one of 'user', 'assistant', or 'tool'
- Content must not be empty
- Timestamp must be current or past
- Tool calls and results must follow OpenAI's schema when present

### AgentTool
**Description**: Defines a tool available to the agent for performing operations
- **id**: UUID (Primary Key) - Unique identifier for the tool
- **name**: String (Unique) - Name of the tool (used in function calls)
- **description**: Text - Purpose and usage description of the tool
- **schema**: JSON - JSON Schema definition of tool parameters
- **created_at**: DateTime - When the tool was registered
- **enabled**: Boolean - Whether the tool is currently available

**Relationships**:
- One-to-Many: AgentTool may be used in many ToolExecutions (conceptual)

**Validation Rules**:
- Name must be unique across all tools
- Schema must follow JSON Schema specification
- Description must be provided and not empty
- Enabled status determines if tool can be used

### ToolExecutionLog
**Description**: Logs all tool executions for monitoring and debugging
- **id**: UUID (Primary Key) - Unique identifier for the log entry
- **session_id**: UUID (Foreign Key) - Session during which tool was executed
- **user_id**: UUID (Foreign Key) - User who initiated the tool call
- **tool_name**: String - Name of the tool executed
- **parameters**: JSON - Parameters passed to the tool
- **result**: JSON (Optional) - Result of the tool execution
- **error**: Text (Optional) - Error message if tool execution failed
- **timestamp**: DateTime - When the execution occurred
- **status**: String (Enum: 'success', 'error', 'cancelled') - Outcome of execution

**Relationships**:
- Many-to-One: ToolExecutionLog belongs to one AgentSession
- Many-to-One: ToolExecutionLog belongs to one User

**Validation Rules**:
- session_id must reference an existing AgentSession
- user_id must reference an existing User
- tool_name must be a valid registered tool
- Either result or error must be provided (but not both for success)
- Status must be one of the allowed values

### UserContext
**Description**: Additional user-specific context available to the agent
- **user_id**: UUID (Foreign Key, Primary Key) - Reference to user
- **preferences**: JSON - User preferences for agent interactions
- **usage_stats**: JSON - Statistics about agent usage by the user
- **last_accessed**: DateTime - Last time agent accessed user context
- **updated_at**: DateTime - Last update to context

**Relationships**:
- One-to-One: User has one UserContext
- The UserContext extends the existing User entity

**Validation Rules**:
- user_id must reference an existing User (relationship requirement)
- Preferences must follow valid JSON structure
- Usage stats follow predefined schema
- Last accessed must be current or past

## State Transitions

### AgentSession States
1. **Created**: Session initiated when user starts agent interaction
2. **Active**: Session receiving messages and processing requests
3. **Paused**: Session temporarily inactive (timeout or user request)
4. **Ended**: Session concluded, no further messages accepted
5. **Archived**: Session data preserved but not actively used

### ToolExecution States
1. **Initiated**: Tool call sent from agent to backend
2. **Processing**: Backend executing the requested operation
3. **Completed**: Tool operation finished successfully
4. **Failed**: Tool operation encountered an error
5. **Cancelled**: Tool operation stopped before completion

## Constraints

### Referential Integrity
- FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
- FOREIGN KEY (session_id) REFERENCES agent_sessions(id) ON DELETE CASCADE
- FOREIGN KEY (tool_name) REFERENCES agent_tools(name) ON DELETE SET NULL

### Data Validation
- CHECK (timestamp <= NOW()) for message and log timestamps
- CHECK (created_at <= updated_at) for session timestamps
- NOT NULL constraints on required fields
- UNIQUE constraints on tool names to prevent conflicts
- JSON schema validation for dynamic content fields

### Security Constraints
- User context is only accessible by the owning user
- Tool executions are logged with user identification
- Agent sessions are tied to authenticated users only
- Cross-user access to sessions is prevented via database constraints

## API Considerations

### Query Patterns
- Get user's recent agent sessions: WHERE user_id = ? ORDER BY updated_at DESC LIMIT ?
- Get messages for a session: WHERE session_id = ? ORDER BY timestamp ASC
- Search agent messages: WHERE content ILIKE ? AND user_id = ?
- Get tool execution logs for debugging: WHERE user_id = ? AND timestamp > ? ORDER BY timestamp DESC

### Performance Optimizations
- Indexes on user_id for user-specific queries
- Indexes on session_id for session-specific queries
- Composite indexes on timestamp + user_id for time-based queries
- Partitioning of message tables by date if needed for scale