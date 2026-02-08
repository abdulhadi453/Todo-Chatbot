# Data Model: Next.js Frontend Web Application

**Feature**: Next.js Frontend Web Application
**Date**: 2026-01-15
**Author**: Claude Sonnet 4.5

## Frontend Data Structures

### User Entity
Represents an authenticated user with properties for session management

**Fields**:
- `id`: string - Unique identifier for the user
- `email`: string - User's email address for authentication
- `name`: string (optional) - User's display name

**Validation**:
- Email must be a valid email format
- ID must be non-empty string

### TodoTask Entity
Represents a task with properties that align with backend structure

**Fields**:
- `id`: number - Unique identifier for the task
- `user_id`: string - Foreign key linking to user
- `description`: string - Text description of the task
- `is_completed`: boolean - Completion status of the task
- `created_at`: string - ISO timestamp of creation
- `updated_at`: string - ISO timestamp of last update

**Validation**:
- Description must be 1-500 characters
- is_completed must be boolean
- user_id must match authenticated user
- created_at and updated_at are server-managed

## State Transitions

### Task State Transitions
- `pending` → `completed`: When user marks task as complete
- `completed` → `pending`: When user unmarks task as complete

### Session State Transitions
- `unauthenticated` → `loading` → `authenticated`: During login process
- `authenticated` → `expired` → `unauthenticated`: When JWT token expires

## Relationships
- User (1) has many TodoTasks (N) - via user_id foreign key
- Each TodoTask belongs to exactly one User