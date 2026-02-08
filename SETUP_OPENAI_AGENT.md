# OpenAI Agent Service - Setup Guide

## Quick Start

This guide will help you set up and run the OpenAI Agent service for the Todo application.

## Prerequisites

1. Python 3.10+
2. OpenAI API account with API key
3. PostgreSQL database (Neon Serverless)
4. Existing Phase III codebase

## Installation Steps

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install the new `openai==1.58.1` package along with existing dependencies.

### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and add your OpenAI API key:

```env
# Required: Your OpenAI API key
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Optional: Model configuration
AGENT_MODEL_NAME=gpt-4-turbo-preview
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=1000
AGENT_TIMEOUT_SECONDS=30

# Optional: Use stub AI for testing without OpenAI
USE_STUB_AGENT=false
```

### 3. Verify Database Models

Ensure the following database tables exist:
- `agent_sessions`
- `agent_messages`
- `tasks` (from Phase II)

If migrations are needed, run:

```bash
cd backend
alembic upgrade head
```

### 4. Start the Backend Server

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Test the Agent Service

#### Option A: Using the Frontend
1. Start the frontend application
2. Navigate to the chat interface
3. Send a message like "Show me my todos"

#### Option B: Using curl

```bash
# First, get a JWT token by logging in
TOKEN="your-jwt-token-here"
USER_ID="your-user-id-here"

# Send a chat message
curl -X POST "http://localhost:8000/api/$USER_ID/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me my todos"
  }'
```

#### Option C: Using Python

```python
import requests

# Login first to get token
login_response = requests.post(
    "http://localhost:8000/auth/login",
    json={"email": "user@example.com", "password": "password"}
)
token = login_response.json()["access_token"]
user_id = login_response.json()["user_id"]

# Send chat message
chat_response = requests.post(
    f"http://localhost:8000/api/{user_id}/chat",
    headers={"Authorization": f"Bearer {token}"},
    json={"message": "List my incomplete tasks"}
)

print(chat_response.json())
```

## Configuration Options

### Using Stub AI (for testing without OpenAI)

Set in `.env`:
```env
USE_STUB_AGENT=true
```

This will use the mock AI responder instead of calling OpenAI, useful for:
- Local development without API costs
- Testing without internet connection
- Integration tests

### Model Selection

Available models (as of 2024):
- `gpt-4-turbo-preview` (recommended, best quality)
- `gpt-4` (high quality, slower)
- `gpt-3.5-turbo` (faster, lower cost)

Set in `.env`:
```env
AGENT_MODEL_NAME=gpt-4-turbo-preview
```

### Temperature Setting

Controls response randomness (0-1):
- `0.0`: Deterministic, focused responses
- `0.7`: Balanced (recommended)
- `1.0`: More creative, varied responses

```env
AGENT_TEMPERATURE=0.7
```

## Testing

### Run Unit Tests

```bash
cd backend
pytest tests/test_openai_agent_service.py -v
```

### Run Integration Tests

```bash
cd backend
pytest tests/ -v -k agent
```

### Manual Testing Checklist

- [ ] Create new conversation
- [ ] List todos
- [ ] Add a todo via chat
- [ ] Update a todo via chat
- [ ] Mark todo as complete via chat
- [ ] Delete a todo via chat
- [ ] Retrieve conversation history
- [ ] Delete conversation
- [ ] Test with invalid inputs
- [ ] Test with missing API key (should fallback to stub)
- [ ] Test with API timeout (should handle gracefully)

## Troubleshooting

### Issue: "OPENAI_API_KEY not set" Warning

**Cause**: Environment variable not configured

**Solution**:
1. Check `.env` file exists in `backend/` directory
2. Verify `OPENAI_API_KEY=sk-...` is present
3. Restart the backend server

### Issue: "429 Rate Limit Exceeded"

**Cause**: Too many API requests to OpenAI

**Solution**:
1. Wait a few minutes before retrying
2. Upgrade OpenAI API plan for higher limits
3. Implement request throttling
4. Use `USE_STUB_AGENT=true` for development

### Issue: "Session not found or access denied"

**Cause**: Session ID doesn't exist or belongs to different user

**Solution**:
1. Omit `conversation_id` to create new session
2. Verify user owns the session
3. Check JWT token is valid

### Issue: Tools Not Executing

**Cause**: Function calling not working correctly

**Solution**:
1. Verify model supports function calling (GPT-4, GPT-3.5-turbo do)
2. Check tool definitions match function signatures
3. Review logs for tool execution errors
4. Test individual tools directly

### Issue: Slow Response Times

**Cause**: OpenAI API latency

**Solution**:
1. Reduce `AGENT_MAX_TOKENS` for faster responses
2. Limit conversation history length
3. Use faster model like `gpt-3.5-turbo`
4. Consider caching common queries

### Issue: Database Connection Errors

**Cause**: PostgreSQL connection issues

**Solution**:
1. Verify `DATABASE_URL` in `.env`
2. Check database is running
3. Verify network connectivity
4. Check connection pool settings

## API Reference

### POST /api/{user_id}/chat
Send a message to the AI agent.

**Request**:
```json
{
  "message": "Add a task to review code",
  "conversation_id": "optional-uuid"
}
```

**Response**:
```json
{
  "conversation_id": "uuid",
  "response": "I've added the task 'Review code' to your todo list.",
  "timestamp": "2024-01-01T00:00:00Z",
  "message_id": "uuid",
  "conversation_title": "Chat: Add a task...",
  "tool_calls": [...],
  "tool_results": [...]
}
```

### GET /api/{user_id}/conversations
List all conversations for the user.

**Response**:
```json
[
  {
    "id": "uuid",
    "title": "Chat: 2024-01-01",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "message_count": 10
  }
]
```

### GET /api/{user_id}/conversations/{conversation_id}
Get a specific conversation with full message history.

### DELETE /api/{user_id}/conversations/{conversation_id}
Delete a conversation and all its messages.

## Example Queries

Here are some example queries to test the agent:

### Todo Management
- "Show me my incomplete tasks"
- "Add a task to buy groceries"
- "Mark the grocery task as complete"
- "Update the grocery task description to include milk and eggs"
- "Delete all completed tasks"

### Context Queries
- "What's my recent activity?"
- "What tasks do I usually create?"
- "Show me my productivity patterns"

### Natural Language
- "I need to remember to call John tomorrow"
- "What do I need to do today?"
- "Help me organize my tasks"
- "What should I work on next?"

## Performance Tuning

### Optimize Response Time

1. **Reduce Token Usage**:
   ```env
   AGENT_MAX_TOKENS=500
   ```

2. **Limit Conversation History**:
   ```env
   MAX_CONVERSATION_HISTORY=10
   ```

3. **Use Faster Model**:
   ```env
   AGENT_MODEL_NAME=gpt-3.5-turbo
   ```

### Optimize Costs

1. **Cache Common Responses** (future enhancement)
2. **Use GPT-3.5-turbo** instead of GPT-4
3. **Implement request batching**
4. **Set lower `AGENT_MAX_TOKENS`**

### Database Optimization

1. **Add Indexes**:
   ```sql
   CREATE INDEX idx_agent_messages_session ON agent_messages(session_id);
   CREATE INDEX idx_agent_messages_user ON agent_messages(user_id);
   CREATE INDEX idx_agent_sessions_user ON agent_sessions(user_id);
   ```

2. **Connection Pooling**:
   ```env
   DATABASE_POOL_SIZE=20
   DATABASE_POOL_TIMEOUT=30
   ```

## Security Best Practices

1. **Never commit `.env` file** to version control
2. **Rotate API keys regularly**
3. **Use environment-specific keys** (dev, staging, prod)
4. **Implement rate limiting** per user
5. **Validate all inputs** before tool execution
6. **Log security events** for audit trails
7. **Use HTTPS** in production
8. **Implement request signing** for API calls

## Monitoring & Logging

### Enable Detailed Logging

```env
LOG_LEVEL=DEBUG
LOG_TO_FILE=true
LOG_FILE_PATH=logs/agent.log
```

### Monitor Key Metrics

1. **Response Time**: Track API latency
2. **Error Rate**: Monitor failed requests
3. **Token Usage**: Track costs
4. **Tool Execution**: Count tool calls
5. **User Activity**: Track active users

### Log Files

- Application logs: `logs/agent.log`
- Error logs: Check console output
- Database logs: PostgreSQL logs

## Next Steps

1. **Review Documentation**: See `AGENT_SERVICE_README.md` for detailed info
2. **Run Tests**: Execute test suite to verify installation
3. **Test Frontend**: Verify chat interface works
4. **Monitor Costs**: Track OpenAI API usage
5. **Plan Enhancements**: Consider streaming, voice input, etc.

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review logs for error details
3. Consult `AGENT_SERVICE_README.md` for architecture details
4. Check OpenAI documentation for API-specific issues

## Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Better Auth Documentation](https://betterauth.com/)
