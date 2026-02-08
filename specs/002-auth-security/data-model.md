# Data Model: Authentication & API Security

## Overview
This document defines the authentication-related data models and extensions to existing models for the security implementation.

## Authentication Entities

### User (Extension to existing model)
**Description**: Represents a registered user account with authentication credentials and security information

**Fields**:
- `id` (String/UUID): Primary key, unique identifier for the user
- `email` (String): User's email address, required for authentication
- `password_hash` (String): Hashed password for authentication
- `name` (String): User's display name
- `created_at` (DateTime): Account creation timestamp
- `updated_at` (DateTime): Account update timestamp
- `email_verified` (Boolean): Whether email has been verified
- `disabled` (Boolean): Whether account is disabled

**Relationships**:
- Has many TodoTask records (via user_id foreign key)

### JWT Token
**Description**: Represents an encrypted authentication token containing user identity and security information

**Structure** (for reference, not stored in database):
- `sub` (Subject): User ID
- `email` (String): User email
- `exp` (Expiration): Token expiration timestamp
- `iat` (Issued At): Token creation timestamp
- `jti` (JWT ID): Unique token identifier for potential revocation

**Validation Rules**:
- Token must not be expired
- Signature must be valid
- User ID in token must match requested resource owner
- Token must be properly formatted

## Authentication Sessions (Conceptual)
**Description**: Represents a user's active authentication state with valid token

**Attributes**:
- `user_id` (String): Associated user
- `token` (JWT): Current valid token
- `expires_at` (DateTime): Token expiration time
- `last_accessed` (DateTime): Last activity timestamp

## Security Constraints

### Token Validation
- All API requests must include valid JWT in Authorization header
- Token signature must be verified using shared secret
- Token must not be expired
- User ID in token must match user ID in URL parameter

### User Identity Matching
- For any request to `/api/{user_id}/...`, the `user_id` must match the subject in the JWT token
- Cross-user access attempts must be rejected with 403 Forbidden

### Error Handling
- Invalid tokens → 401 Unauthorized
- Expired tokens → 401 Unauthorized
- Mismatched user IDs → 403 Forbidden
- Missing tokens → 401 Unauthorized

## Integration with Existing Models

### TodoTask (No changes to structure)
**Fields**:
- `id` (Integer): Primary key
- `description` (String): Task description
- `completed` (Boolean): Completion status
- `user_id` (String): Foreign key reference to User (unchanged)
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Update timestamp

**Security Enhancement**:
- All operations on TodoTask must validate that the user_id in the JWT matches the user_id in the resource
- Cross-user access attempts must be prevented

## API Security Model

### Protected Endpoints
- `GET /api/{user_id}/tasks` - Requires valid JWT with matching user_id
- `POST /api/{user_id}/tasks` - Requires valid JWT with matching user_id
- `GET /api/{user_id}/tasks/{id}` - Requires valid JWT with matching user_id
- `PUT /api/{user_id}/tasks/{id}` - Requires valid JWT with matching user_id
- `DELETE /api/{user_id}/tasks/{id}` - Requires valid JWT with matching user_id
- `PATCH /api/{user_id}/tasks/{id}/complete` - Requires valid JWT with matching user_id

### Authentication Endpoints
- `POST /auth/register` - Creates new user account
- `POST /auth/login` - Authenticates user and returns JWT
- `POST /auth/logout` - Invalidates current session (optional)
- `GET /auth/me` - Returns current user info (protected)

## Database Schema Extensions

```sql
-- Users table (extension of existing structure)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    email_verified BOOLEAN DEFAULT FALSE,
    disabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for security and performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_disabled ON users(disabled);

-- Refresh tokens table (for session management)
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
```

## Security Validation Rules

### Request Processing
1. Extract Authorization header
2. Validate header format ("Bearer <token>")
3. Verify JWT signature
4. Check token expiration
5. Extract user identity from token
6. Compare user_id in token with user_id in URL
7. Allow or deny access based on validation

### Authorization Matrix
| User Context | Target Resource | Access Decision |
|--------------|-----------------|-----------------|
| User A | User A's data | ALLOW |
| User A | User B's data | DENY |
| Anonymous | Any data | DENY |
| Invalid Token | Any data | DENY |
| Expired Token | Any data | DENY |