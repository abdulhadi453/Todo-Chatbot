# API Contract: Next.js Frontend Web Application

**Feature**: Next.js Frontend Web Application
**Date**: 2026-01-15
**Author**: Claude Sonnet 4.5

## Authentication API Contracts

### POST /auth/register
**Description**: Register a new user account
**Request**:
```json
{
  "email": "string",
  "password": "string"
}
```
**Response (200)**:
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "user": {
    "id": "string",
    "email": "string"
  }
}
```
**Errors**:
- 400: Invalid input
- 409: User already exists

### POST /auth/login
**Description**: Authenticate user and return JWT tokens
**Request**:
```json
{
  "email": "string",
  "password": "string"
}
```
**Response (200)**:
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "user": {
    "id": "string",
    "email": "string"
  }
}
```
**Errors**:
- 400: Invalid credentials
- 401: Unauthorized

### POST /auth/refresh
**Description**: Refresh access token using refresh token
**Request**:
```json
{
  "refresh_token": "string"
}
```
**Response (200)**:
```json
{
  "access_token": "string",
  "refresh_token": "string"
}
```
**Errors**:
- 400: Invalid refresh token
- 401: Unauthorized

### GET /auth/me
**Description**: Get current user information
**Headers**:
```
Authorization: Bearer <access_token>
```
**Response (200)**:
```json
{
  "id": "string",
  "email": "string"
}
```
**Errors**:
- 401: Unauthorized

## Task Management API Contracts

### GET /api/{user_id}/tasks
**Description**: Get all tasks for a specific user
**Headers**:
```
Authorization: Bearer <access_token>
```
**Path Parameters**:
- user_id: string (must match authenticated user ID)
**Response (200)**:
```json
[
  {
    "id": number,
    "user_id": "string",
    "description": "string",
    "is_completed": boolean,
    "created_at": "string",
    "updated_at": "string"
  }
]
```
**Errors**:
- 401: Unauthorized
- 403: Forbidden (user_id mismatch)
- 404: User not found

### POST /api/{user_id}/tasks
**Description**: Create a new task for a user
**Headers**:
```
Authorization: Bearer <access_token>
```
**Path Parameters**:
- user_id: string (must match authenticated user ID)
**Request**:
```json
{
  "description": "string"
}
```
**Response (201)**:
```json
{
  "id": number,
  "user_id": "string",
  "description": "string",
  "is_completed": boolean,
  "created_at": "string",
  "updated_at": "string"
}
```
**Errors**:
- 400: Invalid input
- 401: Unauthorized
- 403: Forbidden (user_id mismatch)

### GET /api/{user_id}/tasks/{id}
**Description**: Get a specific task
**Headers**:
```
Authorization: Bearer <access_token>
```
**Path Parameters**:
- user_id: string (must match authenticated user ID)
- id: number (task ID)
**Response (200)**:
```json
{
  "id": number,
  "user_id": "string",
  "description": "string",
  "is_completed": boolean,
  "created_at": "string",
  "updated_at": "string"
}
```
**Errors**:
- 401: Unauthorized
- 403: Forbidden (user_id mismatch or task not owned by user)
- 404: Task not found

### PUT /api/{user_id}/tasks/{id}
**Description**: Update a specific task
**Headers**:
```
Authorization: Bearer <access_token>
```
**Path Parameters**:
- user_id: string (must match authenticated user ID)
- id: number (task ID)
**Request**:
```json
{
  "description": "string"
}
```
**Response (200)**:
```json
{
  "id": number,
  "user_id": "string",
  "description": "string",
  "is_completed": boolean,
  "created_at": "string",
  "updated_at": "string"
}
```
**Errors**:
- 400: Invalid input
- 401: Unauthorized
- 403: Forbidden (user_id mismatch or task not owned by user)
- 404: Task not found

### DELETE /api/{user_id}/tasks/{id}
**Description**: Delete a specific task
**Headers**:
```
Authorization: Bearer <access_token>
```
**Path Parameters**:
- user_id: string (must match authenticated user ID)
- id: number (task ID)
**Response (204)**: No content
**Errors**:
- 401: Unauthorized
- 403: Forbidden (user_id mismatch or task not owned by user)
- 404: Task not found

### PATCH /api/{user_id}/tasks/{id}/complete
**Description**: Toggle task completion status
**Headers**:
```
Authorization: Bearer <access_token>
```
**Path Parameters**:
- user_id: string (must match authenticated user ID)
- id: number (task ID)
**Response (200)**:
```json
{
  "id": number,
  "user_id": "string",
  "description": "string",
  "is_completed": boolean,
  "created_at": "string",
  "updated_at": "string"
}
```
**Errors**:
- 401: Unauthorized
- 403: Forbidden (user_id mismatch or task not owned by user)
- 404: Task not found