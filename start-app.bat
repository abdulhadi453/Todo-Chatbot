@echo off
REM Batch script to start the full-stack application
REM save as start-app.bat

echo Starting Todo Application...

REM Function to stop existing processes on ports
echo Checking for existing processes on ports 8000 and 3000...

REM Stop any processes on port 8000 (backend)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    echo Stopping process %%a on port 8000...
    taskkill /f /pid %%a 2>nul
)

REM Stop any processes on port 3000 (frontend)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do (
    echo Stopping process %%a on port 3000...
    taskkill /f /pid %%a 2>nul
)

timeout /t 2 /nobreak >nul

REM Start backend in a new command window
echo Starting backend server on port 8000...
start "Backend Server" cmd /k "cd /d %~dp0\backend && python run_server.py"

timeout /t 5 /nobreak >nul

REM Start frontend in a new command window
echo Starting frontend server on port 3000...
start "Frontend Server" cmd /k "cd /d %~dp0\frontend && npm run dev"

echo.
echo Application started successfully!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press Ctrl+C in each terminal to stop the servers.
pause