# Todo Application - Startup Guide

## Clean Startup Workflow for Windows

The application consists of:
- **Backend**: Python FastAPI server running on port 8000
- **Frontend**: Next.js application running on port 3000
- **Database**: Neon PostgreSQL (configured in .env files)

## Quick Start

### Option 1: Using the startup script (recommended)
```powershell
# For PowerShell
.\start-app.ps1
```

```batch
# For Command Prompt
start-app.bat
```

### Option 2: Manual startup

1. **Start the backend server:**
```cmd
cd backend
python run_server.py
```

2. **In a new terminal, start the frontend:**
```cmd
cd frontend
npm run dev
```

## Troubleshooting

### If you encounter port conflicts:
- Check running processes: `netstat -ano | findstr :8000` or `:3000`
- Kill specific process: `taskkill /PID <process_id> /F`

### If you get import/module errors:
- Make sure you're running from the correct directory
- Check that all .env files are properly configured

### Database Connection:
- The application uses Neon PostgreSQL as configured in the .env files
- Make sure your Neon database credentials are correct

## Environment Configuration

- Backend .env file: `backend/.env` (now configured with Neon PostgreSQL)
- Frontend .env file: `frontend/.env.local` (created with API base URL)

## URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Backend API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health