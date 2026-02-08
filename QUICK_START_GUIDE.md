# Quick Start Guide - OpenAI Agent Service

## 5-Minute Setup

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Configure Environment
Create `backend/.env` file:
```env
OPENAI_API_KEY=sk-your-key-here
DATABASE_URL=postgresql://user:pass@host/db
JWT_SECRET_KEY=your-secret-key
```

### Step 3: Run Backend
```bash
uvicorn main:app --reload
```

### Step 4: Test
```bash
# Using curl (replace USER_ID and TOKEN)
curl -X POST "http://localhost:8000/api/USER_ID/chat" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me my todos"}'
```

## Example Queries

Try these natural language queries:

```
"What tasks do I have?"
"Add a task to buy groceries"
"Mark the first task as complete"
"Delete completed tasks"
"What have I been working on?"
```

## Stub AI Mode (No API Key)

For testing without OpenAI:

```env
USE_STUB_AGENT=true
```

## Files Overview

| File | Purpose |
|------|---------|
| `backend/services/openai_agent_service.py` | Main service implementation |
| `backend/routers/agent.py` | API endpoints |
| `backend/services/todo_tools.py` | Tool implementations |
| `backend/config/agent_config.py` | Configuration |
| `backend/tests/test_openai_agent_service.py` | Tests |

## Key Features

1. Natural language todo management
2. Conversation history
3. Tool calling (5 tools)
4. Error handling with fallback
5. JWT authentication
6. Session management

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/{user_id}/chat` | Send message |
| GET | `/api/{user_id}/conversations` | List conversations |
| GET | `/api/{user_id}/conversations/{id}` | Get conversation |
| DELETE | `/api/{user_id}/conversations/{id}` | Delete conversation |

## Troubleshooting

**Issue**: "OPENAI_API_KEY not set"
- Add key to `.env` file
- Or set `USE_STUB_AGENT=true`

**Issue**: Database connection error
- Verify `DATABASE_URL` in `.env`
- Check database is running

**Issue**: 403 Forbidden
- Verify JWT token is valid
- Check user_id matches token

## Next Steps

1. Review `AGENT_SERVICE_README.md` for details
2. Check `SETUP_OPENAI_AGENT.md` for full setup
3. Run tests: `pytest tests/test_openai_agent_service.py`
4. Monitor costs in OpenAI dashboard

## Support

- Technical docs: `backend/services/AGENT_SERVICE_README.md`
- Architecture: `AGENT_ARCHITECTURE.md`
- Full setup: `SETUP_OPENAI_AGENT.md`
- Implementation: `T013_IMPLEMENTATION_SUMMARY.md`
