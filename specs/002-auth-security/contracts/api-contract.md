# API Contract: Authentication & API Security

## Overview
This document defines the extended REST API contract for the Todo backend service with authentication and authorization, specifying endpoints, request/response formats, and security requirements.

## Authentication Headers
All protected endpoints require the following header:
- `Authorization`: `Bearer <jwt_token>`

## Authentication Endpoints (New)

### 1. User Registration
**Endpoint**: `POST /auth/register`

**Description**: Register a new user account

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "name": "John Doe"
}
```

**Response**:
- `201 Created`: User successfully registered
```json
{
  "user_id": "uuid-string",
  "email": "user@example.com",
  "name": "John Doe",
  "access_token": "jwt-token-string",
  "refresh_token": "refresh-token-string"
}
```

- `400 Bad Request`: Invalid registration data
- `409 Conflict`: Email already exists

### 2. User Login
**Endpoint**: `POST /auth/login`

**Description**: Authenticate user and return JWT token

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response**:
- `200 OK`: Authentication successful
```json
{
  "user_id": "uuid-string",
  "email": "user@example.com",
  "name": "John Doe",
  "access_token": "jwt-token-string",
  "refresh_token": "refresh-token-string"
}
```

- `400 Bad Request`: Invalid request format
- `401 Unauthorized`: Invalid credentials

### 3. Get Current User
**Endpoint**: `GET /auth/me`

**Description**: Get information about currently authenticated user

**Headers**:
- `Authorization`: `Bearer <jwt_token>`

**Response**:
- `200 OK`: User information retrieved
```json
{
  "user_id": "uuid-string",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2026-01-14T10:00:00Z"
}
```

- `401 Unauthorized`: Invalid or missing token

## Protected Todo Endpoints (Updated)

### 1. List User's Tasks
**Endpoint**: `GET /api/{user_id}/tasks`

**Description**: Retrieve all todo tasks for the specified user (must match authenticated user)

**Headers**:
- `Authorization`: `Bearer <jwt_token>`

**Path Parameters**:
- `user_id` (string, required): The ID of the user whose tasks to retrieve (must match token user_id)

**Request**:
- No request body required

**Response**:
- `200 OK`: Successfully retrieved tasks
```json
[
  {
    "id": 1,
    "description": "Sample task",
    "completed": false,
    "user_id": "user123",
    "created_at": "2026-01-14T10:00:00Z",
    "updated_at": "2026-01-14T10:00:00Z"
  }
]
```

- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: user_id in URL does not match token user_id
- `404 Not Found`: User not found

### 2. Create New Task
**Endpoint**: `POST /api/{user_id}/tasks`

**Description**: Create a new todo task for the specified user (must match authenticated user)

**Headers**:
- `Authorization`: `Bearer <jwt_token>`

**Path Parameters**:
- `user_id` (string, required): The ID of the user to create the task for (must match token user_id)

**Request Body**:
```json
{
  "description": "Task description"
}
```

**Response**:
- `201 Created`: Task successfully created
```json
{
  "id": 1,
  "description": "Task description",
  "completed": false,
  "user_id": "user123",
  "created_at": "2026-01-14T10:00:00Z",
  "updated_at": "2026-01-14T10:00:00Z"
}
```

- `400 Bad Request`: Invalid request format
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: user_id in URL does not match token user_id

### 3. Get Specific Task
**Endpoint**: `GET /api/{user_id}/tasks/{id}`

**Description**: Retrieve a specific todo task by its ID (must belong to authenticated user)

**Headers**:
- `Authorization`: `Bearer <jwt_token>`

**Path Parameters**:
- `user_id` (string, required): The ID of the user (must match token user_id)
- `id` (integer, required): The ID of the task

**Request**:
- No request body required

**Response**:
- `200 OK`: Task successfully retrieved
```json
{
  "id": 1,
  "description": "Sample task",
  "completed": false,
  "user_id": "user123",
  "created_at": "2026-01-14T10:00:00Z",
  "updated_at": "2026-01-14T10:00:00Z"
}
```

- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: user_id in URL does not match token user_id
- `404 Not Found`: Task not found for the user

### 4. Update Task
**Endpoint**: `PUT /api/{user_id}/tasks/{id}`

**Description**: Update an existing todo task (must belong to authenticated user)

**Headers**:
- `Authorization`: `Bearer <jwt_token>`

**Path Parameters**:
- `user_id` (string, required): The ID of the user (must match token user_id)
- `id` (integer, required): The ID of the task

**Request Body**:
```json
{
  "description": "Updated task description",
  "completed": true
}
```

**Response**:
- `200 OK`: Task successfully updated
```json
{
  "id": 1,
  "description": "Updated task description",
  "completed": true,
  "user_id": "user123",
  "created_at": "2026-01-14T10:00:00Z",
  "updated_at": "2026-01-14T11:00:00Z"
}
```

- `400 Bad Request`: Invalid request format
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: user_id in URL does not match token user_id
- `404 Not Found`: Task not found for the user

### 5. Delete Task
**Endpoint**: `DELETE /api/{user_id}/tasks/{id}`

**Description**: Delete a specific todo task (must belong to authenticated user)

**Headers**:
- `Authorization`: `Bearer <jwt_token>`

**Path Parameters**:
- `user_id` (string, required): The ID of the user (must match token user_id)
- `id` (integer, required): The ID of the task

**Request**:
- No request body required

**Response**:
- `204 No Content`: Task successfully deleted

- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: user_id in URL does not match token user_id
- `404 Not Found`: Task not found for the user

### 6. Toggle Task Completion
**Endpoint**: `PATCH /api/{user_id}/tasks/{id}/complete`

**Description**: Toggle the completion status of a task (must belong to authenticated user)

**Headers**:
- `Authorization`: `Bearer <jwt_token>`

**Path Parameters**:
- `user_id` (string, required): The ID of the user (must match token user_id)
- `id` (integer, required): The ID of the task

**Request**:
- No request body required

**Response**:
- `200 OK`: Task completion status successfully toggled
```json
{
  "id": 1,
  "description": "Sample task",
  "completed": true,
  "user_id": "user123",
  "created_at": "2026-01-14T10:00:00Z",
  "updated_at": "2026-01-14T11:00:00Z"
}
```

- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: user_id in URL does not match token user_id
- `404 Not Found`: Task not found for the user

## Error Responses

All error responses follow this format:
```json
{
  "detail": "Human-readable error message"
}
```

## Common HTTP Status Codes
- `200 OK`: Successful request with response body
- `201 Created`: Resource successfully created
- `204 No Content`: Request successful but no response body
- `400 Bad Request`: Client sent invalid request
- `401 Unauthorized`: Invalid or missing authentication token
- `403 Forbidden`: User not authorized for requested action
- `404 Not Found`: Requested resource not found
- `409 Conflict`: Request conflicts with existing resource
- `500 Internal Server Error`: Server error occurred

## Security & Access Control
- All protected endpoints require valid JWT token in Authorization header
- User ID in JWT token must match the user_id in the URL path
- Cross-user access attempts return 403 Forbidden
- Invalid/expired tokens return 401 Unauthorized
- Authentication endpoints do not require Authorization header