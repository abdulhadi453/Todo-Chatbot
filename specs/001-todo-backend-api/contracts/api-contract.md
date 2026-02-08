# API Contract: Todo Backend API & Database

## Overview
This document defines the REST API contract for the Todo backend service, specifying endpoints, request/response formats, and error handling.

## Base URL
```
/api/{user_id}/
```

## Common Headers
- `Content-Type`: `application/json`
- `Accept`: `application/json`

## Endpoints

### 1. List User's Tasks
**Endpoint**: `GET /api/{user_id}/tasks`

**Description**: Retrieve all todo tasks for the specified user

**Path Parameters**:
- `user_id` (string, required): The ID of the user whose tasks to retrieve

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

### 2. Create New Task
**Endpoint**: `POST /api/{user_id}/tasks`

**Description**: Create a new todo task for the specified user

**Path Parameters**:
- `user_id` (string, required): The ID of the user to create the task for

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

### 3. Get Specific Task
**Endpoint**: `GET /api/{user_id}/tasks/{id}`

**Description**: Retrieve a specific todo task by its ID

**Path Parameters**:
- `user_id` (string, required): The ID of the user
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

- `404 Not Found`: Task not found for the user

### 4. Update Task
**Endpoint**: `PUT /api/{user_id}/tasks/{id}`

**Description**: Update an existing todo task

**Path Parameters**:
- `user_id` (string, required): The ID of the user
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
- `404 Not Found`: Task not found for the user

### 5. Delete Task
**Endpoint**: `DELETE /api/{user_id}/tasks/{id}`

**Description**: Delete a specific todo task

**Path Parameters**:
- `user_id` (string, required): The ID of the user
- `id` (integer, required): The ID of the task

**Request**:
- No request body required

**Response**:
- `204 No Content`: Task successfully deleted

- `404 Not Found`: Task not found for the user

### 6. Toggle Task Completion
**Endpoint**: `PATCH /api/{user_id}/tasks/{id}/complete`

**Description**: Toggle the completion status of a task

**Path Parameters**:
- `user_id` (string, required): The ID of the user
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
- `404 Not Found`: Requested resource not found
- `500 Internal Server Error`: Server error occurred

## Security & Access Control
- All endpoints enforce user_id scoping
- Users can only access their own tasks
- Cross-user access attempts return 404 (not found)