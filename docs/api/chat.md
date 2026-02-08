# Chat API Documentation

This document describes the API endpoints for the AI Chatbot feature.

## Authentication

All chat endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

The user ID in the token must match the `{user_id}` parameter in the URL path.

## Endpoints

### POST `/api/{user_id}/chat`

Handle chat interactions between user and AI assistant.

#### Request Body
```json
{
  "conversation_id": "string (optional)",
  "message": "string (required)",
  "model_preferences": {
    "temperature": 0.7
  }
}
```

#### Response (200 OK)
```json
{
  "conversation_id": "string",
  "response": "string",
  "timestamp": "string (ISO 8601 datetime)",
  "message_id": "string",
  "conversation_title": "string"
}
```

#### Error Responses
- 400: Bad Request (invalid message content)
- 401: Unauthorized (invalid token)
- 403: Forbidden (user doesn't own conversation)
- 429: Too Many Requests (rate limit exceeded)
- 500: Internal Server Error

### GET `/api/{user_id}/conversations`

Retrieve all conversations for the specified user, ordered by most recent activity.

#### Response (200 OK)
```json
[
  {
    "id": "string",
    "title": "string",
    "created_at": "string (ISO 8601 datetime)",
    "updated_at": "string (ISO 8601 datetime)",
    "message_count": "integer"
  }
]
```

### GET `/api/{user_id}/conversations/{conversation_id}`

Retrieve a specific conversation and its message history.

#### Response (200 OK)
```json
{
  "conversation": {
    "id": "string",
    "title": "string",
    "created_at": "string (ISO 8601 datetime)",
    "updated_at": "string (ISO 8601 datetime)"
  },
  "messages": [
    {
      "id": "string",
      "role": "string (user|assistant)",
      "content": "string",
      "timestamp": "string (ISO 8601 datetime)"
    }
  ]
}
```

### DELETE `/api/{user_id}/conversations/{conversation_id}`

Delete a specific conversation and all its messages.

#### Response (200 OK)
```json
{
  "message": "Conversation deleted successfully"
}
```

## Security

- All endpoints validate JWT tokens and ensure users can only access their own conversations
- Rate limiting prevents abuse (default: 30 requests per minute)
- Input validation ensures message length doesn't exceed limits
- Cross-origin requests are controlled by CORS configuration