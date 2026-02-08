@echo off
REM Todo Backend API Startup Script for Windows

echo Starting Todo Backend API Setup...

REM Load environment variables
echo Loading environment variables...
if exist .env (
    for /f "tokens=*" %%i in (.env) do (
        set "%%i"
    )
)

REM Install dependencies
echo Installing required packages...
python -m pip install -r backend\requirements.txt

REM Start the server
echo Starting the Todo Backend API server...
python -c "from backend.config.database import create_db_and_tables; create_db_and_tables(); print('Database initialized successfully!')"
python -m uvicorn backend.src.main:app --host %API_HOST% --port %API_PORT% --reload