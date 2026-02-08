# Data Model: Todo Backend API & Database

## Overview
This document defines the data model for the Todo backend API, including entities, relationships, and validation rules.

## Entities

### TodoTask
**Description**: Represents a single todo item with user association

**Fields**:
- `id` (UUID/Integer): Primary key, unique identifier for the task
- `description` (String): Text description of the task, required
- `completed` (Boolean): Completion status, default: false
- `user_id` (String): Foreign key reference to user, required for scoping
- `created_at` (DateTime): Timestamp when task was created, auto-generated
- `updated_at` (DateTime): Timestamp when task was last updated, auto-generated

**Validation Rules**:
- Description must not be empty or only whitespace
- user_id must be present and valid
- Task cannot be completed if already deleted

**Relationships**:
- Belongs to one User (via user_id foreign key)
- Each user can have multiple TodoTask records

### User (Reference)
**Description**: Represents a user account for scoping tasks

**Fields**:
- `user_id` (String): Unique identifier for the user, primary key
- `created_at` (DateTime): Account creation timestamp

**Note**: User entity is referenced via user_id parameter but not managed by this service

## State Transitions

### Task Completion
- `pending` → `completed` via PATCH /api/{user_id}/tasks/{id}/complete
- `completed` → `pending` via PATCH /api/{user_id}/tasks/{id}/complete

### Task Lifecycle
- `created` → `pending` (initial state)
- `pending` ↔ `completed` (toggle completion)
- `any_state` → `deleted` (on DELETE request)

## Database Schema

```sql
CREATE TABLE todo_tasks (
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_todo_tasks_user_id ON todo_tasks(user_id);
CREATE INDEX idx_todo_tasks_completed ON todo_tasks(completed);
```

## Constraints
- All operations must be scoped by user_id
- Tasks are isolated by user_id (no cross-user access)
- Description field cannot be null or empty
- Each task belongs to exactly one user