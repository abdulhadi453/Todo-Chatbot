# Data Model: Phase III AI Todo Chatbot – Chatbot Core Integration

**Feature**: 006-ai-chatbot
**Created**: 2026-02-06
**Status**: Complete

## Entity Definitions

### Conversation
**Description**: Represents a collection of messages between a user and the AI assistant
- **id**: UUID (Primary Key) - Unique identifier for the conversation
- **user_id**: UUID (Foreign Key) - Links to the user who owns this conversation
- **title**: String (Optional) - Auto-generated or user-defined title for the conversation
- **created_at**: DateTime - Timestamp when the conversation was initiated
- **updated_at**: DateTime - Timestamp of the last activity in the conversation
- **is_active**: Boolean - Indicates if the conversation is currently active

**Relationships**:
- One-to-Many: User has many Conversations
- One-to-Many: Conversation has many Messages

**Validation Rules**:
- user_id must reference an existing user
- created_at must be before or equal to updated_at
- title length limited to 200 characters
- Each conversation belongs to exactly one user

### Message
**Description**: Represents an individual message in a conversation
- **id**: UUID (Primary Key) - Unique identifier for the message
- **conversation_id**: UUID (Foreign Key) - Links to the conversation this message belongs to
- **user_id**: UUID (Foreign Key) - Links to the user who sent this message
- **role**: String (Enum: 'user', 'assistant', 'system') - Specifies the sender type
- **content**: Text - The actual message content
- **timestamp**: DateTime - When the message was sent/created
- **parent_message_id**: UUID (Optional, Foreign Key) - References parent message in thread (for future threading support)
- **metadata**: JSON (Optional) - Additional data about the message

**Relationships**:
- Many-to-One: Message belongs to one Conversation
- Many-to-One: Message belongs to one User

**Validation Rules**:
- conversation_id must reference an existing conversation
- user_id must reference an existing user
- role must be one of 'user', 'assistant', or 'system'
- content must not be empty
- timestamp must be current or past
- Messages must belong to conversations owned by the same user

### User (Existing Entity - Extended)
**Description**: Represents authenticated users with JWT-based authentication (from Phase II)
- **id**: UUID (Primary Key) - Unique identifier for the user
- **email**: String - User's email address
- **password_hash**: String - Hashed password for authentication
- **created_at**: DateTime - When the user account was created
- **updated_at**: DateTime - Last update to the user account
- **is_active**: Boolean - Whether the user account is active

**Relationships**:
- One-to-Many: User has many Conversations
- One-to-Many: User has many Messages

## State Transitions

### Conversation States
1. **Created**: Conversation is initiated but may be empty
2. **Active**: At least one message exists, and conversation is ongoing
3. **Inactive**: No recent activity (based on configurable timeout)
4. **Deleted**: Conversation marked for deletion (soft delete)

### Message States
1. **Sent**: Message transmitted from user
2. **Processing**: Message being processed by AI service (transient)
3. **Received**: AI response received and saved to database
4. **Errored**: Processing failed (with error details in metadata)

## Database Indexes

### Primary Indexes
- Conversation.id: Primary B-tree index
- Message.id: Primary B-tree index
- User.id: Primary B-tree index

### Secondary Indexes
- Conversation.user_id: B-tree index for user-specific queries
- Message.conversation_id: B-tree index for conversation filtering
- Message.user_id: B-tree index for user authorization checks
- Message.timestamp: B-tree index for chronological ordering
- Conversation.updated_at: B-tree index for recent conversations retrieval

## Constraints

### Referential Integrity
- FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE
- FOREIGN KEY (conversation_id) REFERENCES Conversation(id) ON DELETE CASCADE
- FOREIGN KEY (parent_message_id) REFERENCES Message(id) ON DELETE SET NULL

### Data Validation
- CHECK (timestamp <= NOW()) for message timestamps
- CHECK (created_at <= updated_at) for conversation timestamps
- NOT NULL constraints on required fields
- UNIQUE constraints where needed

## API Considerations

### Query Patterns
- Get user's conversations: WHERE user_id = ? ORDER BY updated_at DESC
- Get conversation messages: WHERE conversation_id = ? ORDER BY timestamp ASC
- Search in user's conversations: WHERE user_id = ? AND content ILIKE ?

### Performance Optimizations
- Limit message history retrieval (pagination or recent-only)
- Use database views for complex conversation statistics
- Consider read replicas for heavy query patterns
- Cache frequently accessed conversations if needed

## Security Considerations

### Access Control
- All queries must be user-scoped using user_id
- Foreign key constraints prevent cross-user data access
- Row-level security for multi-user isolation
- Authentication verification required for all operations

### Data Protection
- Encryption at rest for sensitive message content
- Secure audit logging for access patterns
- GDPR compliance for data deletion requests
- PII protection and anonymization where possible