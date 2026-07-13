# Quick Chat Debug Guide

## Step 1: Test if you're logged in

Open browser console on your frontend and run:
```javascript
console.log('Token:', localStorage.getItem('access_token'));
console.log('User:', localStorage.getItem('user'));
```

If token is `null`, you need to log in first.

## Step 2: Check what error you're getting

1. Open `http://localhost:3000/chat`
2. Open DevTools (F12) → Console tab
3. Try to send a message
4. Look for red error messages

Common errors:
- **401 Unauthorized** → You're not logged in or token expired
- **403 Forbidden** → User ID mismatch
- **Network Error** → Backend not running or CORS issue
- **500 Internal Server Error** → Backend error (check backend terminal)

## Step 3: Test backend directly

Open a new terminal and run:
```bash
# First, get a user ID from your database or use a test UUID
# Test if endpoint responds (will fail auth, but shows it's alive)
curl -X POST http://localhost:8000/api/123e4567-e89b-12d3-a456-426614174000/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"test\"}"

# Should return: {"detail":"Not authenticated"}
# This confirms the endpoint exists and is working
```

## Step 4: Check backend is using correct router

Your backend should be using `agent_router` from `backend/routers/agent.py`.

File: `backend/src/main.py` should have:
```python
from backend.routers.agent import router as agent_router
app.include_router(agent_router)
```

✅ This is already correct in your setup.

## Most Common Issue: Authentication

Your chat endpoint requires a valid JWT token. Make sure:
1. You're logged in at `http://localhost:3000/login`
2. Token is stored in localStorage as `access_token`
3. Token hasn't expired (30 minutes)

## Quick Fix: Check Frontend is Sending Token

Add this debug line to `frontend/src/lib/api/chatClient.ts` line 42:
```typescript
this.api.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    console.log('🔐 Sending request with token:', token ? 'EXISTS' : 'MISSING'); // ADD THIS
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
```

This will show in console if token is being sent.

## What Should Happen (Success Flow)

1. User logs in → Token saved to localStorage
2. User opens `/chat` page
3. User types message and clicks send
4. Frontend sends: `POST /api/{user_id}/chat` with Authorization header
5. Backend validates token
6. OpenAI processes message
7. Response streams back to frontend
8. Message appears in chat

## Still Not Working?

Share with me:
1. The exact error message from browser console
2. Any errors in backend terminal
3. Output of Step 1 (whether token exists)
