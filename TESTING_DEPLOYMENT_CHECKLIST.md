# Testing & Deployment Checklist - OpenAI Agent Service

## Pre-Deployment Testing

### 1. Environment Setup
- [ ] Python 3.10+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with all required variables
- [ ] OpenAI API key configured (or stub mode enabled)
- [ ] Database connection tested
- [ ] JWT secret key configured

### 2. Unit Tests
```bash
cd backend
pytest tests/test_openai_agent_service.py -v
```

- [ ] All tests pass
- [ ] No warnings or errors
- [ ] Coverage > 80%

#### Key Test Areas
- [ ] Service initialization (with/without API key)
- [ ] Tool definitions validation
- [ ] Tool execution (list, add, update, delete)
- [ ] Message processing
- [ ] Conversation management
- [ ] Error handling
- [ ] Input validation

### 3. Integration Tests

#### A. Database Tests
- [ ] Agent sessions created successfully
- [ ] Messages stored correctly
- [ ] Session retrieval works
- [ ] Message history correct
- [ ] Session deletion cascades to messages
- [ ] User isolation enforced

#### B. API Endpoint Tests
```bash
# Test each endpoint
pytest tests/ -v -k agent
```

- [ ] POST /api/{user_id}/chat
  - [ ] Creates new session
  - [ ] Uses existing session
  - [ ] Validates JWT token
  - [ ] Rejects invalid user_id
  - [ ] Returns proper response format

- [ ] GET /api/{user_id}/conversations
  - [ ] Lists user's conversations
  - [ ] Ordered by updated_at DESC
  - [ ] Includes message count

- [ ] GET /api/{user_id}/conversations/{id}
  - [ ] Returns conversation details
  - [ ] Includes full message history
  - [ ] Enforces ownership

- [ ] DELETE /api/{user_id}/conversations/{id}
  - [ ] Deletes conversation
  - [ ] Deletes all messages
  - [ ] Enforces ownership

### 4. Tool Execution Tests

#### List Todos
- [ ] Lists all todos
- [ ] Filters by completed status
- [ ] Pagination works
- [ ] Returns correct format
- [ ] Handles empty list

#### Add Todo
- [ ] Creates new todo
- [ ] Validates title required
- [ ] Validates title length (max 200)
- [ ] Validates description length (max 1000)
- [ ] Returns created todo
- [ ] Associates with correct user

#### Update Todo
- [ ] Updates title
- [ ] Updates description
- [ ] Updates completed status
- [ ] Validates ownership
- [ ] Handles non-existent todo
- [ ] Validates input

#### Delete Todo
- [ ] Deletes todo
- [ ] Validates ownership
- [ ] Handles non-existent todo
- [ ] Returns success confirmation

#### Get User Context
- [ ] Returns user preferences
- [ ] Returns activity summary
- [ ] Returns common patterns
- [ ] Handles new users

### 5. OpenAI Integration Tests

#### With Real API (if API key available)
- [ ] Natural language parsing works
- [ ] Tool calling works correctly
- [ ] Multiple tools in one conversation
- [ ] Conversation context maintained
- [ ] Response quality acceptable
- [ ] Token usage reasonable

#### Test Queries
- [ ] "Show me my todos"
- [ ] "Add a task to buy milk"
- [ ] "Mark the milk task as complete"
- [ ] "Delete all completed tasks"
- [ ] "What tasks do I have left?"
- [ ] "Tell me about my recent activity"

#### With Stub AI
- [ ] Fallback works when no API key
- [ ] Fallback works on API timeout
- [ ] Fallback works on API error
- [ ] Response still generated
- [ ] Error logged appropriately

### 6. Error Handling Tests

#### Input Validation
- [ ] Empty message rejected
- [ ] Oversized message rejected (>10K chars)
- [ ] Invalid user_id format rejected
- [ ] Invalid session_id format rejected
- [ ] Missing required fields rejected

#### Authentication Errors
- [ ] Missing JWT token → 401
- [ ] Invalid JWT token → 401
- [ ] Expired JWT token → 401
- [ ] Wrong user_id → 403
- [ ] Session ownership enforced

#### API Errors
- [ ] Timeout handled gracefully
- [ ] Connection error handled
- [ ] Rate limit handled
- [ ] Invalid API key handled
- [ ] OpenAI errors logged

#### Database Errors
- [ ] Connection failure handled
- [ ] Query errors caught
- [ ] Transaction rollback works
- [ ] Constraint violations handled

### 7. Security Tests

#### Authentication
- [ ] JWT validation works
- [ ] Expired tokens rejected
- [ ] Malformed tokens rejected
- [ ] Token signature verified

#### Authorization
- [ ] User can only access own sessions
- [ ] User can only access own todos
- [ ] User cannot access other user's data
- [ ] Session ownership enforced
- [ ] Tool execution scoped to user

#### Input Security
- [ ] SQL injection prevented
- [ ] XSS prevented
- [ ] Command injection prevented
- [ ] Path traversal prevented
- [ ] Excessive resource usage prevented

### 8. Performance Tests

#### Response Time
- [ ] Chat endpoint < 5s (with OpenAI)
- [ ] Chat endpoint < 1s (with stub)
- [ ] List conversations < 200ms
- [ ] Get conversation < 500ms
- [ ] Delete conversation < 200ms

#### Scalability
- [ ] 10 concurrent users handled
- [ ] 100 messages per session handled
- [ ] Database queries optimized
- [ ] Connection pooling works
- [ ] Memory usage reasonable

#### Load Testing (Optional)
```bash
# Use tools like Apache Bench or Locust
ab -n 100 -c 10 http://localhost:8000/api/USER_ID/conversations
```

### 9. Configuration Tests

#### Environment Variables
- [ ] All required vars checked on startup
- [ ] Missing vars logged/warned
- [ ] Invalid values rejected
- [ ] Defaults used appropriately

#### Feature Flags
- [ ] USE_STUB_AGENT works
- [ ] MCP_SERVER_ENABLED respected
- [ ] LOG_TO_FILE works
- [ ] ENABLE_INPUT_SANITIZATION works

### 10. Logging & Monitoring

#### Logs
- [ ] Application logs created
- [ ] Error logs captured
- [ ] Tool execution logged
- [ ] API calls logged
- [ ] Log levels respected

#### Metrics to Monitor
- [ ] Request count
- [ ] Response time (p50, p95, p99)
- [ ] Error rate
- [ ] OpenAI API usage (tokens)
- [ ] Database query time
- [ ] Tool execution count

## Deployment Checklist

### 1. Pre-Deployment

#### Code Review
- [ ] Implementation reviewed
- [ ] Tests reviewed
- [ ] Documentation reviewed
- [ ] Security reviewed
- [ ] Performance reviewed

#### Dependencies
- [ ] requirements.txt updated
- [ ] All dependencies compatible
- [ ] Version pinning appropriate
- [ ] Security vulnerabilities checked

#### Configuration
- [ ] Production .env prepared
- [ ] Secrets secured (not in repo)
- [ ] Database URL configured
- [ ] OpenAI API key configured
- [ ] JWT secret configured

### 2. Development Environment

- [ ] Backend running locally
- [ ] Frontend connected
- [ ] Database accessible
- [ ] All tests passing
- [ ] Manual testing complete

### 3. Staging Environment

- [ ] Code deployed to staging
- [ ] Environment variables set
- [ ] Database migrations run
- [ ] Health check passing
- [ ] Integration tests run
- [ ] Frontend integration tested
- [ ] Performance acceptable

### 4. Production Deployment

#### Pre-Deploy
- [ ] Backup database
- [ ] Notify team
- [ ] Tag release in Git
- [ ] Update documentation
- [ ] Prepare rollback plan

#### Deploy Steps
- [ ] Deploy backend code
- [ ] Run database migrations
- [ ] Update environment variables
- [ ] Restart services
- [ ] Run health checks
- [ ] Test critical paths

#### Post-Deploy
- [ ] Monitor error logs
- [ ] Check API response times
- [ ] Verify OpenAI API calls working
- [ ] Test chat functionality
- [ ] Monitor resource usage
- [ ] Check user feedback

### 5. Rollback Plan

If issues occur:
- [ ] Stop accepting new requests
- [ ] Revert to previous version
- [ ] Rollback database migrations (if needed)
- [ ] Restore previous configuration
- [ ] Verify system stable
- [ ] Document issues

## Monitoring Setup

### Application Monitoring
- [ ] Error tracking configured (Sentry, etc.)
- [ ] Performance monitoring (APM)
- [ ] Uptime monitoring
- [ ] Log aggregation (ELK, etc.)

### Business Metrics
- [ ] Active conversations tracked
- [ ] Messages per day
- [ ] Tool usage statistics
- [ ] User engagement metrics
- [ ] Conversation completion rate

### Cost Monitoring
- [ ] OpenAI API usage dashboard
- [ ] Token usage per user
- [ ] Cost per conversation
- [ ] Budget alerts configured
- [ ] Usage trends analyzed

## Post-Deployment

### Week 1
- [ ] Monitor error rates daily
- [ ] Review user feedback
- [ ] Check performance metrics
- [ ] Verify cost tracking
- [ ] Document any issues

### Week 2-4
- [ ] Analyze usage patterns
- [ ] Optimize based on metrics
- [ ] Address user feedback
- [ ] Plan improvements
- [ ] Update documentation

### Ongoing
- [ ] Weekly metric reviews
- [ ] Monthly cost analysis
- [ ] Quarterly performance tuning
- [ ] Regular security audits
- [ ] Dependency updates

## Success Criteria

### Technical
- [ ] All tests passing
- [ ] Error rate < 1%
- [ ] Response time < 5s (p95)
- [ ] Uptime > 99.5%
- [ ] No critical security issues

### Business
- [ ] Users can chat successfully
- [ ] Todos managed via chat
- [ ] Conversations persistent
- [ ] User satisfaction positive
- [ ] Cost within budget

### Performance
- [ ] Handles expected load
- [ ] Database queries optimized
- [ ] API calls efficient
- [ ] Memory usage stable
- [ ] CPU usage reasonable

## Sign-off

### Development Team
- [ ] Backend developer approval
- [ ] Frontend developer approval
- [ ] QA approval
- [ ] Code review complete

### Operations Team
- [ ] Infrastructure ready
- [ ] Monitoring configured
- [ ] Backup strategy in place
- [ ] Scaling plan documented

### Product Team
- [ ] Features validated
- [ ] User stories complete
- [ ] Documentation approved
- [ ] Release notes prepared

### Security Team
- [ ] Security review complete
- [ ] Vulnerabilities addressed
- [ ] Compliance verified
- [ ] Audit trail configured

## Notes

Record any issues, observations, or lessons learned:

```
Date: _____________
Issue: _____________________________________________
Resolution: ________________________________________
Lessons: ___________________________________________
```

## Resources

- Implementation: `T013_IMPLEMENTATION_SUMMARY.md`
- Architecture: `AGENT_ARCHITECTURE.md`
- Setup: `SETUP_OPENAI_AGENT.md`
- API Docs: `backend/services/AGENT_SERVICE_README.md`
- Quick Start: `QUICK_START_GUIDE.md`

---

**Version**: 1.0.0
**Last Updated**: 2024
**Owner**: Backend Team
