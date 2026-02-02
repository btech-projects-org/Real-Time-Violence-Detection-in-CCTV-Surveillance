# Start Backend Server
# This script activates the virtual environment and starts the FastAPI backend

$venvPath = ".venv\Scripts\Activate.ps1"
$backendPath = "backend\main.py"

Write-Host "🚀 Starting Backend Server..." -ForegroundColor Cyan

# Activate virtual environment
& $venvPath

# Start the backend server
Write-Host "📡 Starting FastAPI server on http://localhost:8000" -ForegroundColor Green
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
