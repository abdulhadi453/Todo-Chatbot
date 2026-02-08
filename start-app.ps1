# PowerShell script to start the full-stack application
# save as start-app.ps1

Write-Host "Starting Todo Application..." -ForegroundColor Green

# Function to stop existing processes on ports
function Stop-ExistingProcesses {
    Write-Host "Checking for existing processes on ports 8000 and 3000..." -ForegroundColor Yellow

    # Stop any processes on port 8000 (backend)
    $port8000 = netstat -ano | findstr ":8000 "
    if ($port8000) {
        $pid = ($port8000 -split '\s+')[-1]
        Write-Host "Stopping process $pid on port 8000..." -ForegroundColor Yellow
        Stop-Process -Id $pid -Force
    }

    # Stop any processes on port 3000 (frontend)
    $port3000 = netstat -ano | findstr ":3000 "
    if ($port3000) {
        $pid = ($port3000 -split '\s+')[-1]
        Write-Host "Stopping process $pid on port 3000..." -ForegroundColor Yellow
        Stop-Process -Id $pid -Force
    }
}

# Stop existing processes
Stop-ExistingProcesses

Start-Sleep -Seconds 2

# Start backend in a new PowerShell window
Write-Host "Starting backend server on port 8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-Command", "Set-Location '$PSScriptRoot\backend'; python run_server.py"

Start-Sleep -Seconds 5

# Start frontend in a new PowerShell window
Write-Host "Starting frontend server on port 3000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-Command", "Set-Location '$PSScriptRoot\frontend'; npm run dev"

Write-Host "Application started successfully!" -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C in each terminal to stop the servers." -ForegroundColor Yellow