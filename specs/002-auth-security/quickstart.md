# Quickstart Guide: Authentication & API Security

## Overview
This guide explains how to set up and use the authentication and authorization features for the Todo Backend API.

## Prerequisites
- Completed setup from previous Todo Backend API feature
- Python 3.13+
- Node.js 18+ (for frontend authentication)
- Pip package manager
- Git

## Frontend Setup (Next.js + Better Auth)

### 1. Install Better Auth
```bash
npm install better-auth
# or
yarn add better-auth
```

### 2. Configure Better Auth
Create `frontend/src/auth/auth-config.ts`:
```typescript
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  app: {
    name: "Todo App",
    baseUrl: process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000",
  },
  socialProviders: {
    // Configure social providers if needed
  },
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
  },
  advanced: {
    sessionToken: "jwt",
    refreshToken: true,
  },
});
```

### 3. Set up Auth Provider
Create `frontend/src/auth/auth-provider.tsx`:
```tsx
"use client";

import { AuthProvider as BetterAuthProvider } from "better-auth/react";
import { auth } from "./auth-config";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  return <BetterAuthProvider client={auth}>{children}</BetterAuthProvider>;
}
```

## Backend Setup (FastAPI + JWT)

### 1. Install Additional Dependencies
Add to `backend/requirements.txt`:
```
PyJWT==2.8.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

### 2. Configure JWT Settings
Create `backend/config/auth.py`:
```python
import os
from datetime import timedelta

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
```

### 3. Create JWT Utilities
Create `backend/src/auth/jwt-utils.py`:
```python
from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import HTTPException, status
from backend.config.auth import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        return payload
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
```

### 4. Create Authentication Dependencies
Create `backend/src/auth/auth-dependencies.py`:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.src.auth.jwt-utils import verify_token

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return user_id

def get_user_from_token(
    user_id_from_path: str,
    current_user_id: str = Depends(get_current_user)
):
    if user_id_from_path != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )
    return current_user_id
```

## API Usage Examples

### 1. Register New User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securePassword123",
    "name": "John Doe"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securePassword123"
  }'
```

### 3. Use JWT Token for Protected Endpoints
```bash
# Save the JWT token from login response
TOKEN="your-jwt-token-from-login-response"

# Use it for protected endpoints
curl -X GET http://localhost:8000/api/user123/tasks \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Add a Task (Protected)
```bash
curl -X POST http://localhost:8000/api/user123/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description": "Buy groceries"}'
```

## Frontend Integration

### 1. API Client with Token Attachment
Create `frontend/src/services/api-client.ts`:
```typescript
class ApiClient {
  private baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

  async request(endpoint: string, options: RequestInit = {}) {
    const token = this.getToken();

    const headers = {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    };

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }

    return response.json();
  }

  private getToken(): string | null {
    // Get token from auth provider or storage
    return localStorage.getItem('auth-token');
  }
}

export const apiClient = new ApiClient();
```

### 2. Protected Route Component
Create `frontend/src/components/protected-route.tsx`:
```tsx
'use client';

import { useAuth } from 'better-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { session, isPending } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isPending && !session) {
      router.push('/signin');
    }
  }, [session, isPending, router]);

  if (isPending || !session) {
    return <div>Loading...</div>;
  }

  return <>{children}</>;
}
```

## Configuration
- JWT Secret Key: Set via JWT_SECRET_KEY environment variable
- Token Expiration: Set via ACCESS_TOKEN_EXPIRE_MINUTES environment variable
- Refresh Token Expiration: Set via REFRESH_TOKEN_EXPIRE_DAYS environment variable

## Security Best Practices
- Use strong, unique JWT secret keys in production
- Implement token rotation for enhanced security
- Set secure HTTP-only cookies for tokens when possible
- Validate token expiration on every request
- Implement rate limiting for authentication endpoints