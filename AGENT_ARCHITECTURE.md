# OpenAI Agent Service - Architecture Diagram

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (Next.js)                             │
│                                                                           │
│  ┌────────────────┐         ┌─────────────────┐                         │
│  │ ChatInterface  │────────>│  API Client     │                         │
│  │  Component     │<────────│  (fetch/axios)  │                         │
│  └────────────────┘         └─────────────────┘                         │
│         │                            │                                   │
│         │ User Types Message         │ HTTP POST with JWT                │
│         v                            v                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                       │
                                       │ POST /api/{user_id}/chat
                                       │ Authorization: Bearer <JWT>
                                       │ Body: { message, conversation_id }
                                       v
┌─────────────────────────────────────────────────────────────────────────┐
│                          BACKEND (FastAPI)                               │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                     Agent Router                                   │  │
│  │                  (backend/routers/agent.py)                        │  │
│  │                                                                     │  │
│  │  1. Validate JWT Token → get_current_user_id()                    │  │
│  │  2. Verify user_id matches token                                  │  │
│  │  3. Initialize OpenAIAgentService                                 │  │
│  │  4. Call service.process_message()                                │  │
│  │  5. Return formatted response                                     │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                │                                          │
│                                v                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │              OpenAIAgentService                                    │  │
│  │         (backend/services/openai_agent_service.py)                │  │
│  │                                                                     │  │
│  │  ┌─────────────────────────────────────────────────────────────┐  │  │
│  │  │  process_message(user_id, message, session_id)              │  │  │
│  │  │                                                               │  │  │
│  │  │  1. Validate inputs (message length, UUID format)            │  │  │
│  │  │  2. Get or create AgentSession                               │  │  │
│  │  │  3. Store user message in database                           │  │  │
│  │  │  4. Build conversation history (last 20 messages)            │  │  │
│  │  │  5. Prepare OpenAI request with system prompt + tools        │  │  │
│  │  │  6. Call OpenAI API                                           │  │  │
│  │  │  7. Process tool calls (if any)                              │  │  │
│  │  │  8. Get final response                                        │  │  │
│  │  │  9. Store assistant message                                   │  │  │
│  │  │ 10. Return response + metadata                                │  │  │
│  │  └─────────────────────────────────────────────────────────────┘  │  │
│  │                                │                                    │  │
│  │                ┌───────────────┴───────────────┐                   │  │
│  │                v                               v                   │  │
│  │    ┌──────────────────────┐      ┌──────────────────────┐         │  │
│  │    │   Tool Execution     │      │   Database Access    │         │  │
│  │    │                      │      │                      │         │  │
│  │    │  _execute_tool()    │      │  - Add messages      │         │  │
│  │    │                      │      │  - Get history       │         │  │
│  │    │  Maps to:            │      │  - Update sessions   │         │  │
│  │    │  • list_todos        │      │  - Get sessions      │         │  │
│  │    │  • add_todo          │      │                      │         │  │
│  │    │  • update_todo       │      │                      │         │  │
│  │    │  • delete_todo       │      │                      │         │  │
│  │    │  • get_user_context  │      │                      │         │  │
│  │    └──────────────────────┘      └──────────────────────┘         │  │
│  │                │                               │                    │  │
│  │                v                               v                    │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                  │                               │                       │
│                  v                               v                       │
│  ┌───────────────────────────┐   ┌─────────────────────────────────┐   │
│  │      TodoTools            │   │      SQLModel/Database          │   │
│  │ (backend/services/        │   │                                  │   │
│  │  todo_tools.py)           │   │  Tables:                         │   │
│  │                           │   │  • agent_sessions                │   │
│  │  • list_todos()           │   │  • agent_messages                │   │
│  │  • add_todo()             │   │  • tasks                         │   │
│  │  • update_todo()          │   │  • users                         │   │
│  │  • delete_todo()          │   │  • user_context                  │   │
│  │  • get_user_context()     │   │                                  │   │
│  └───────────────────────────┘   └─────────────────────────────────┘   │
│                  │                               │                       │
└─────────────────────────────────────────────────────────────────────────┘
                   │                               │
                   v                               v
       ┌──────────────────────┐       ┌────────────────────────┐
       │   External APIs      │       │   PostgreSQL (Neon)    │
       │                      │       │                        │
       │  OpenAI API          │       │  Persistent Storage    │
       │  - GPT-4 Turbo       │       │  - User data           │
       │  - Function Calling  │       │  - Sessions            │
       │  - Chat Completions  │       │  - Messages            │
       └──────────────────────┘       │  - Tasks               │
                                      └────────────────────────┘
```

## Detailed Flow Diagram

### 1. User Sends Message Flow

```
User Types: "Show me my todos"
         │
         v
┌─────────────────────┐
│  Frontend           │
│  ChatInterface      │
│                     │
│  - Get JWT token    │
│  - Get user_id      │
│  - Build request    │
└─────────────────────┘
         │
         │ POST /api/{user_id}/chat
         │ Headers: Authorization: Bearer <JWT>
         │ Body: { message: "Show me my todos" }
         v
┌─────────────────────┐
│  Backend            │
│  Agent Router       │
│                     │
│  1. Extract JWT     │
│  2. Validate token  │────> get_current_user_id()
│  3. Verify user_id  │
│  4. Extract message │
└─────────────────────┘
         │
         v
┌────────────────────────────────────┐
│  OpenAIAgentService                │
│  process_message()                 │
│                                    │
│  1. Validate input                 │
│     - Check message not empty      │
│     - Check message length < 10K   │
│     - Validate UUID format         │
│                                    │
│  2. Session Management             │
│     - If session_id provided:      │
│       → Get existing session       │
│     - Else:                        │
│       → Create new session         │
│                                    │
│  3. Store User Message             │
│     - Create AgentMessage          │
│     - role: "user"                 │
│     - content: message text        │
│     - Save to database             │
└────────────────────────────────────┘
         │
         v
┌────────────────────────────────────┐
│  Build Conversation Context        │
│                                    │
│  1. Get last 20 messages from DB   │
│  2. Format for OpenAI:             │
│     [                              │
│       {role: "system",             │
│        content: "You are..."},     │
│       {role: "user",               │
│        content: "..."},            │
│       {role: "assistant",          │
│        content: "..."}             │
│     ]                              │
│  3. Add new user message           │
└────────────────────────────────────┘
         │
         v
┌────────────────────────────────────┐
│  Call OpenAI API                   │
│                                    │
│  client.chat.completions.create(   │
│    model="gpt-4-turbo-preview",    │
│    messages=[...],                 │
│    tools=[                         │
│      {type: "function",            │
│       function: {                  │
│         name: "list_todos",        │
│         description: "...",        │
│         parameters: {...}          │
│       }},                          │
│      ...                           │
│    ],                              │
│    tool_choice="auto",             │
│    temperature=0.7                 │
│  )                                 │
└────────────────────────────────────┘
         │
         v
┌────────────────────────────────────┐
│  Process OpenAI Response           │
│                                    │
│  IF response has tool_calls:       │
│    FOR EACH tool_call:             │
│      1. Extract tool name          │
│      2. Parse arguments (JSON)     │
│      3. Call _execute_tool()       │
│      4. Collect results            │
│                                    │
│    Send results back to OpenAI     │
│    Get final response              │
│                                    │
│  ELSE:                             │
│    Use response content directly   │
└────────────────────────────────────┘
         │
         v
┌────────────────────────────────────┐
│  Tool Execution                    │
│  _execute_tool(name, args)         │
│                                    │
│  CASE name:                        │
│    "list_todos":                   │
│      → todo_tools.list_todos()     │
│      → Query tasks table           │
│      → Return formatted list       │
│                                    │
│    "add_todo":                     │
│      → todo_tools.add_todo()       │
│      → Create Task record          │
│      → Return new task             │
│                                    │
│    "update_todo":                  │
│      → todo_tools.update_todo()    │
│      → Update Task record          │
│      → Return updated task         │
│                                    │
│    etc...                          │
└────────────────────────────────────┘
         │
         v
┌────────────────────────────────────┐
│  Store Assistant Response          │
│                                    │
│  1. Create AgentMessage            │
│     - role: "assistant"            │
│     - content: response text       │
│     - tool_calls: [...]            │
│     - tool_results: [...]          │
│                                    │
│  2. Update session timestamp       │
│  3. Commit to database             │
└────────────────────────────────────┘
         │
         v
┌────────────────────────────────────┐
│  Return Response                   │
│                                    │
│  {                                 │
│    session_id: "uuid",             │
│    message_id: "uuid",             │
│    response: "Here are your...",   │
│    timestamp: "2024-...",          │
│    tool_calls: [...],              │
│    tool_results: [...]             │
│  }                                 │
└────────────────────────────────────┘
         │
         v
┌────────────────────────────────────┐
│  Frontend Displays Response        │
│                                    │
│  - Update chat UI                  │
│  - Show user message               │
│  - Show assistant response         │
│  - Update conversation list        │
└────────────────────────────────────┘
```

## Error Handling Flow

```
Any Step Fails
     │
     v
┌─────────────────────┐
│  Error Detection    │
│                     │
│  Types:             │
│  • ValidationError  │
│  • APITimeoutError  │
│  • APIConnError     │
│  • OpenAIError      │
│  • Exception        │
└─────────────────────┘
     │
     ├──> ValidationError ──> Return 400 with message
     │
     ├──> APITimeoutError ──┐
     │                      │
     ├──> APIConnError ─────┤
     │                      │
     ├──> OpenAIError ──────┤
     │                      v
     │              ┌────────────────────┐
     │              │  Fallback to Stub  │
     │              │                    │
     │              │  1. Log error      │
     │              │  2. Call stub_ai   │
     │              │  3. Store response │
     │              │  4. Return with    │
     │              │     using_stub:true│
     │              └────────────────────┘
     │
     └──> Other Exception ──> Return 500 with error
```

## Data Flow

### Message Storage

```
User Message → AgentMessage Table
                    │
                    ├─ id: UUID
                    ├─ session_id: UUID (FK)
                    ├─ user_id: UUID (FK)
                    ├─ role: "user"
                    ├─ content: "message text"
                    ├─ timestamp: datetime
                    ├─ tool_calls: null
                    └─ tool_call_results: null

Assistant Response → AgentMessage Table
                         │
                         ├─ id: UUID
                         ├─ session_id: UUID (same)
                         ├─ user_id: UUID (same)
                         ├─ role: "assistant"
                         ├─ content: "response text"
                         ├─ timestamp: datetime
                         ├─ tool_calls: [{...}]
                         └─ tool_call_results: [{...}]
```

### Session Management

```
AgentSession Table
     │
     ├─ id: UUID (PK)
     ├─ user_id: UUID (FK to users)
     ├─ title: "Chat: first message..."
     ├─ created_at: datetime
     ├─ updated_at: datetime (updates on new message)
     └─ messages: [] (relationship to AgentMessage)
```

## Tool Integration Architecture

```
OpenAI Agent
     │
     │ Decides to use tool
     v
Tool Call:
{
  "name": "list_todos",
  "arguments": {
    "user_id": "...",
    "completed": false
  }
}
     │
     v
_execute_tool()
     │
     ├─> Tool name lookup in tool_functions dict
     │
     v
TodoTools.list_todos(user_id, completed=False)
     │
     ├─> Query database via SQLModel
     │       SELECT * FROM tasks
     │       WHERE user_id = ? AND completed = ?
     │
     v
Return Result:
{
  "todos": [
    {
      "id": "...",
      "title": "Buy groceries",
      "completed": false,
      "created_at": "..."
    }
  ],
  "pagination": {
    "limit": 10,
    "offset": 0,
    "total": 5,
    "has_more": false
  }
}
     │
     v
Back to OpenAI with tool result
     │
     v
OpenAI generates natural language response:
"You have 5 incomplete tasks. Here they are:
1. Buy groceries
2. ..."
```

## Security Architecture

```
Request
   │
   v
┌──────────────────────┐
│  JWT Validation      │
│                      │
│  1. Extract token    │
│  2. Verify signature │
│  3. Check expiration │
│  4. Extract user_id  │
└──────────────────────┘
   │
   v
┌──────────────────────┐
│  Authorization       │
│                      │
│  1. URL user_id ==   │
│     token user_id?   │
│  2. Session access?  │
│  3. Tool permissions?│
└──────────────────────┘
   │
   v
┌──────────────────────┐
│  Input Validation    │
│                      │
│  1. Message length   │
│  2. UUID format      │
│  3. Required fields  │
│  4. SQL injection    │
└──────────────────────┘
   │
   v
Process Request
```

## Configuration Management

```
Environment Variables (.env)
          │
          v
┌─────────────────────────┐
│  AgentConfig Class      │
│  (agent_config.py)      │
│                         │
│  Loads and validates:   │
│  • OPENAI_API_KEY       │
│  • AGENT_MODEL_NAME     │
│  • AGENT_TEMPERATURE    │
│  • AGENT_MAX_TOKENS     │
│  • etc.                 │
└─────────────────────────┘
          │
          v
Used by OpenAIAgentService
```

## Summary

This architecture provides:
1. Clear separation of concerns
2. Multiple layers of error handling
3. Secure authentication and authorization
4. Efficient database operations
5. Extensible tool system
6. Graceful degradation
7. Production-ready reliability
