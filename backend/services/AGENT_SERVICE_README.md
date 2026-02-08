# OpenAI Agent Service Implementation

## Overview

The OpenAI Agent Service (`openai_agent_service.py`) provides AI-powered assistance for todo management through natural language interaction. It integrates OpenAI's function calling capabilities with the todo tools to enable conversational task management.

## Architecture

### Components

1. **OpenAIAgentService**: Main service class extending `AgentService`
   - Manages OpenAI API integration
   - Handles tool registration and execution
   - Maintains conversation context
   - Provides fallback to stub AI when needed

2. **TodoTools**: Tool implementations for agent actions
   - `list_todos`: Retrieve user's tasks with filtering
   - `add_todo`: Create new tasks
   - `update_todo`: Modify existing tasks
   - `delete_todo`: Remove tasks
   - `get_user_context`: Retrieve user preferences and activity

3. **AgentConfig**: Configuration management
   - API keys and model settings
   - Timeout and rate limiting
   - Security and logging settings

## Key Features

### 1. Natural Language Processing
- Users can interact with their todos using conversational language
- Agent understands intent and executes appropriate actions
- Examples:
  - "Show me my incomplete tasks"
  - "Add a task to buy groceries"
  - "Mark task #123 as complete"
  - "Delete the shopping task"

### 2. Function Calling (Tool Use)
- OpenAI's function calling enables structured tool execution
- Tools are automatically invoked based on user intent
- Results are integrated into natural conversation flow

### 3. Conversation Management
- Multi-turn conversations with context retention
- Session-based message history
- User-specific conversation isolation

### 4. Error Handling & Fallback
- Graceful degradation to stub AI on API failures
- Timeout handling (configurable, default 30s)
- Retry logic for transient errors
- User-friendly error messages

### 5. Security
- User authentication via JWT tokens
- Session ownership validation
- Input sanitization and validation
- Tool execution authorization

## Configuration

### Environment Variables

Required in `.env` file:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-...your-key...
AGENT_MODEL_NAME=gpt-4-turbo-preview
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=1000
AGENT_TIMEOUT_SECONDS=30

# Fallback Configuration
USE_STUB_AGENT=false  # Set to true to use stub AI instead of OpenAI

# Rate Limiting
RATE_LIMIT_MAX_REQUESTS=30
RATE_LIMIT_WINDOW_MINUTES=1

# Message Limits
MAX_MESSAGE_LENGTH=10000
MAX_CONVERSATION_HISTORY=50
```

### Agent Configuration

Settings managed in `backend/config/agent_config.py`:

```python
class AgentConfig:
    OPENAI_API_KEY: str          # Required for OpenAI integration
    AGENT_MODEL_NAME: str        # GPT model to use
    AGENT_TEMPERATURE: float     # Response randomness (0-1)
    AGENT_MAX_TOKENS: int        # Maximum response length
    AGENT_TIMEOUT_SECONDS: int   # API timeout duration
```

## Usage

### Basic Usage

```python
from backend.services.openai_agent_service import OpenAIAgentService
from sqlmodel import Session

# Initialize service
agent_service = OpenAIAgentService(
    session=db_session,
    use_stub=False  # Use real OpenAI
)

# Process user message
result = agent_service.process_message(
    user_id="user-uuid-here",
    message="Show me my todos",
    session_id="optional-session-uuid"
)

# Response structure
{
    "session_id": "uuid",
    "message_id": "uuid",
    "response": "Here are your todos: ...",
    "timestamp": "2024-01-01T00:00:00",
    "tool_calls": [...],      # Tools invoked
    "tool_results": [...]     # Tool execution results
}
```

### API Endpoints

#### 1. Send Message (Chat)
```http
POST /api/{user_id}/chat
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
    "message": "Add a task to review code",
    "conversation_id": "optional-uuid",
    "model_preferences": {}
}
```

Response:
```json
{
    "conversation_id": "uuid",
    "response": "I've added a new task 'Review code' to your todo list.",
    "timestamp": "2024-01-01T00:00:00Z",
    "message_id": "uuid",
    "conversation_title": "Chat: Add a task to review code",
    "tool_calls": [
        {
            "id": "call_123",
            "name": "add_todo",
            "arguments": {"user_id": "...", "title": "Review code"}
        }
    ],
    "tool_results": [
        {
            "tool_call_id": "call_123",
            "name": "add_todo",
            "result": {"success": true, "todo": {...}}
        }
    ]
}
```

#### 2. List Conversations
```http
GET /api/{user_id}/conversations
Authorization: Bearer <jwt-token>
```

Response:
```json
[
    {
        "id": "uuid",
        "title": "Chat: 2024-01-01",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "message_count": 10
    }
]
```

#### 3. Get Conversation Details
```http
GET /api/{user_id}/conversations/{conversation_id}
Authorization: Bearer <jwt-token>
```

#### 4. Delete Conversation
```http
DELETE /api/{user_id}/conversations/{conversation_id}
Authorization: Bearer <jwt-token>
```

## Tool Definitions

### 1. list_todos
**Purpose**: Retrieve user's todo items with filtering and pagination

**Parameters**:
- `user_id` (required): User identifier
- `limit` (optional): Max items to return (default: 10)
- `offset` (optional): Pagination offset (default: 0)
- `completed` (optional): Filter by status (true/false/null for all)

**Example Tool Call**:
```json
{
    "name": "list_todos",
    "arguments": {
        "user_id": "user-uuid",
        "limit": 5,
        "completed": false
    }
}
```

### 2. add_todo
**Purpose**: Create a new todo item

**Parameters**:
- `user_id` (required): User identifier
- `title` (required): Task title (max 200 chars)
- `description` (optional): Task description (max 1000 chars)

**Example Tool Call**:
```json
{
    "name": "add_todo",
    "arguments": {
        "user_id": "user-uuid",
        "title": "Buy groceries",
        "description": "Milk, eggs, bread"
    }
}
```

### 3. update_todo
**Purpose**: Modify an existing todo item

**Parameters**:
- `user_id` (required): User identifier
- `todo_id` (required): Todo identifier
- `title` (optional): New title
- `description` (optional): New description
- `completed` (optional): New completion status

**Example Tool Call**:
```json
{
    "name": "update_todo",
    "arguments": {
        "user_id": "user-uuid",
        "todo_id": "todo-uuid",
        "completed": true
    }
}
```

### 4. delete_todo
**Purpose**: Remove a todo item permanently

**Parameters**:
- `user_id` (required): User identifier
- `todo_id` (required): Todo identifier

### 5. get_user_context
**Purpose**: Retrieve user preferences and activity patterns

**Parameters**:
- `user_id` (required): User identifier

**Returns**:
- Recent activity summary
- Common todo patterns
- User preferences

## Implementation Details

### Conversation Flow

1. **User sends message** → Frontend → Backend API
2. **Authentication** → JWT token validation
3. **Session management** → Get or create conversation session
4. **Message processing**:
   - Build conversation history from database
   - Add system prompt with agent instructions
   - Send to OpenAI with tools definition
5. **Tool execution**:
   - Parse tool calls from OpenAI response
   - Execute tools via TodoTools
   - Send results back to OpenAI
6. **Response generation**:
   - Get final response incorporating tool results
   - Store messages in database
   - Return formatted response

### Error Handling Strategy

1. **Input Validation**:
   - Message length limits
   - UUID format validation
   - Required field checks

2. **API Errors**:
   - Timeout → Fallback to stub AI
   - Connection error → Fallback to stub AI
   - Rate limit → User-friendly error message
   - Invalid API key → Fallback to stub AI

3. **Tool Execution Errors**:
   - Validation errors → Return error in tool result
   - Database errors → Return error in tool result
   - Unauthorized access → Return error in tool result

4. **Graceful Degradation**:
   - All errors fall back to stub AI
   - User always receives a response
   - Errors logged for debugging

### Security Considerations

1. **Authentication**:
   - JWT token required for all endpoints
   - Token contains user ID for authorization

2. **Authorization**:
   - User ID in URL must match token
   - Session ownership validated
   - Tool execution scoped to user

3. **Input Sanitization**:
   - Message length limits enforced
   - SQL injection prevention via SQLModel
   - XSS prevention via content validation

4. **Rate Limiting**:
   - Configurable per-user limits
   - Prevents API abuse
   - DOS protection

## Testing

### Unit Tests

Test tool execution:
```python
def test_list_todos():
    agent_service = OpenAIAgentService(session, use_stub=True)
    result = agent_service.todo_tools.list_todos(
        user_id="test-user",
        limit=10
    )
    assert "todos" in result
    assert "pagination" in result
```

### Integration Tests

Test end-to-end flow:
```python
def test_agent_chat():
    response = client.post(
        f"/api/{user_id}/chat",
        json={"message": "Show my tasks"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "response" in response.json()
```

### Manual Testing

1. Start backend server
2. Set `OPENAI_API_KEY` in `.env`
3. Use frontend or API client to test:
   - "List my todos"
   - "Add a task to test the agent"
   - "Mark the test task as complete"
   - "Delete all completed tasks"

## Performance Considerations

1. **Response Time**:
   - OpenAI API: 1-5 seconds typical
   - Stub AI: <1 second
   - Tool execution: <100ms per tool

2. **Conversation History**:
   - Limited to 20 most recent messages
   - Prevents token limit issues
   - Reduces API costs

3. **Database Queries**:
   - Indexed on session_id and user_id
   - Efficient pagination
   - Connection pooling enabled

4. **Caching** (future enhancement):
   - Cache user context
   - Cache common queries
   - Reduce API calls

## Troubleshooting

### Issue: "OPENAI_API_KEY not set" warning
**Solution**: Add `OPENAI_API_KEY` to `.env` file

### Issue: API timeout errors
**Solution**: Increase `AGENT_TIMEOUT_SECONDS` in config

### Issue: Rate limit exceeded
**Solution**: Wait or increase rate limits in OpenAI dashboard

### Issue: Tools not executing
**Solution**: Check tool definitions match function signatures

### Issue: Stub AI being used unexpectedly
**Solution**: Verify `USE_STUB_AGENT=false` and API key is valid

## Future Enhancements

1. **Streaming Responses**: Real-time message streaming
2. **Multi-modal Support**: Image and file attachments
3. **Advanced Tools**: Reminders, notes, calendar integration
4. **Context Awareness**: Better personalization
5. **Analytics**: Usage tracking and insights
6. **Voice Input**: Speech-to-text integration

## Dependencies

- `openai>=1.58.1`: OpenAI API client
- `sqlmodel>=0.0.22`: Database ORM
- `fastapi>=0.115.0`: Web framework
- `pyjwt>=2.8.0`: JWT authentication

## License

Part of the Evolution-of-Todo Phase III project.
