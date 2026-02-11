# AI Agent API Documentation

This document describes the API endpoints for the AI Agent functionality in the Todo application.

## Base URL
All agent endpoints are prefixed with `/api/{user_id}/` where `{user_id}` is the authenticated user's ID.

## Authentication
All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

## Endpoints

### POST /api/{user_id}/chat
Send a message to the AI agent and receive a response.

#### Request
```json
{
  "message": "string",
  "conversation_id": "string (optional)",
  "stream": "boolean (optional, default: false)"
}
```

#### Response
```json
{
  "response": "string",
  "conversation_id": "string",
  "timestamp": "ISO 8601 datetime"
}
```

#### Example Request
```bash
curl -X POST "http://localhost:8000/api/123e4567-e89b-12d3-a456-426614174000/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <jwt_token>" \
  -d '{
    "message": "Add a task to buy groceries",
    "conversation_id": "conv_abc123"
  }'
```

#### Example Response
```json
{
  "response": "I've added a task to buy groceries to your list.",
  "conversation_id": "conv_abc123",
  "timestamp": "2026-02-10T10:30:00Z"
}
```

### GET /api/{user_id}/conversations
Retrieve a list of the user's agent conversations.

#### Query Parameters
- `limit`: integer (default: 10)
- `offset`: integer (default: 0)
- `sort_by`: string (default: "created_at")

#### Response
```json
[
  {
    "id": "string",
    "title": "string",
    "created_at": "ISO 8601 datetime",
    "updated_at": "ISO 8601 datetime",
    "message_count": "integer"
  }
]
```

### GET /api/{user_id}/conversations/{conversation_id}
Retrieve a specific conversation and its messages.

#### Response
```json
{
  "id": "string",
  "title": "string",
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime",
  "messages": [
    {
      "id": "string",
      "role": "string ('user' or 'assistant')",
      "content": "string",
      "timestamp": "ISO 8601 datetime"
    }
  ]
}
```

### DELETE /api/{user_id}/conversations/{conversation_id}
Delete a specific conversation.

#### Response
```json
{
  "success": true,
  "message": "string"
}
```

### POST /api/{user_id}/chat/tools/execute
Execute a specific tool for the AI agent.

#### Request
```json
{
  "tool_name": "string",
  "arguments": {
    "user_id": "string",
    // Additional tool-specific arguments
  }
}
```

#### Response
```json
{
  "result": "mixed (depends on tool)",
  "success": "boolean"
}
```

## Available Agent Tools

The AI agent can use the following tools to interact with the todo system:

### list_todos
List the user's todo items.

#### Arguments
- `user_id`: string (required)
- `limit`: integer (optional, default: 10)
- `offset`: integer (optional, default: 0)
- `completed`: boolean (optional, filter by completion status)

### add_todo
Add a new todo item for the user.

#### Arguments
- `user_id`: string (required)
- `title`: string (required)
- `description`: string (optional)

### update_todo
Update an existing todo item.

#### Arguments
- `user_id`: string (required)
- `todo_id`: string (required)
- `title`: string (optional)
- `description`: string (optional)
- `completed`: boolean (optional)

### delete_todo
Delete an existing todo item.

#### Arguments
- `user_id`: string (required)
- `todo_id`: string (required)

### create_reminder
Create a reminder for a todo item.

#### Arguments
- `user_id`: string (required)
- `todo_id`: string (required)
- `reminder_time`: string (ISO 8601 datetime)
- `message`: string (optional)

### add_note_attachment
Add a note or attachment to a todo item.

#### Arguments
- `user_id`: string (required)
- `todo_id`: string (required)
- `note_content`: string (required)
- `attachment_url`: string (optional)

### get_user_context
Get context information about the user.

#### Arguments
- `user_id`: string (required)

## Error Responses

All endpoints follow standard HTTP error response patterns:

### 400 Bad Request
```json
{
  "detail": "string"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Access forbidden"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "An unexpected error occurred"
}
```

## Rate Limiting

API endpoints are subject to rate limiting to prevent abuse. Exceeding the rate limit will result in a 429 Too Many Requests response.

## Security Considerations

- User data is isolated by user ID in JWT tokens
- All sensitive operations require authentication
- Input validation is performed on all tool arguments
- PII is not stored in plain text in conversation history