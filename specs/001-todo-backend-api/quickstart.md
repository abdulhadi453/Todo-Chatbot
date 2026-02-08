# Quickstart Guide: Todo Backend API & Database

## Prerequisites
- Python 3.13+
- Pip package manager
- Neon PostgreSQL account and connection string
- Git (optional, for cloning)

## Setup Instructions

### 1. Clone and Navigate
```bash
git clone <repo-url>
cd <repo-directory>
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Database
Set the database connection string in your environment:
```bash
export DATABASE_URL="postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname?sslmode=require"
```

### 5. Run Database Migrations
```bash
alembic upgrade head
```

### 6. Start the Server
```bash
uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000
```

## API Usage Examples

### 1. Add a Task
```bash
curl -X POST http://localhost:8000/api/user123/tasks \
  -H "Content-Type: application/json" \
  -d '{"description": "Buy groceries"}'
```

### 2. List Tasks
```bash
curl http://localhost:8000/api/user123/tasks
```

### 3. Get Specific Task
```bash
curl http://localhost:8000/api/user123/tasks/1
```

### 4. Update Task
```bash
curl -X PUT http://localhost:8000/api/user123/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"description": "Updated task description", "completed": true}'
```

### 5. Toggle Completion
```bash
curl -X PATCH http://localhost:8000/api/user123/tasks/1/complete
```

### 6. Delete Task
```bash
curl -X DELETE http://localhost:8000/api/user123/tasks/1
```

## Configuration
- Port: 8000 (can be changed with PORT environment variable)
- Database URL: Set via DATABASE_URL environment variable
- Logging level: INFO (change via LOG_LEVEL environment variable)

## Troubleshooting
- If getting database errors, verify your Neon PostgreSQL connection string
- If endpoints return 404, ensure the user_id in the URL matches the expected format
- For CORS issues in development, check the CORS settings in main.py