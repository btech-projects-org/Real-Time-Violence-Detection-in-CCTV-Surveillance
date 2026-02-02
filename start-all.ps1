# Combined Startup Script
# This script starts both backend and frontend in parallel

Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Real-Time Violence Detection System - Startup" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Check virtual environment
if (Test-Path ".venv\Scripts\python.exe") {
    Write-Host "✅ Virtual environment found" -ForegroundColor Green
} else {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    exit 1
}

# Check frontend node_modules
if (Test-Path "frontend\node_modules") {
    Write-Host "✅ Frontend dependencies found" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend dependencies not found!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Starting servers in separate windows..." -ForegroundColor Cyan
Write-Host ""

# Start Backend in new PowerShell window
Write-Host "🚀 Starting Backend Server (Port 8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\.venv\Scripts\Activate.ps1; Write-Host '📡 Backend Server Starting...' -ForegroundColor Green; python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

# Wait a moment for backend to initialize
Start-Sleep -Seconds 3

# Start Frontend in new PowerShell window
Write-Host "🎨 Starting Frontend Server (Port 5173)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; Write-Host '🌐 Frontend Server Starting...' -ForegroundColor Green; npm run dev"

Write-Host ""
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Servers Started!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📡 Backend API:     http://localhost:8000" -ForegroundColor White
Write-Host "📚 API Docs:        http://localhost:8000/docs" -ForegroundColor White
Write-Host "🌐 Frontend:        http://localhost:5173" -ForegroundColor White
Write-Host "🔌 WebSocket:       ws://localhost:8000/ws" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C in each window to stop the servers" -ForegroundColor Yellow
Write-Host ""
