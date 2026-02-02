# Verification Script
# This script checks all requirements and dependencies

Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  System Requirements Verification" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$allChecks = $true

# 1. Check Python Virtual Environment
Write-Host "1. Checking Python Virtual Environment..." -ForegroundColor White
if (Test-Path ".venv\Scripts\python.exe") {
    $pythonVersion = & .venv\Scripts\python.exe --version
    Write-Host "   ✅ Virtual environment exists: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "   ❌ Virtual environment not found!" -ForegroundColor Red
    $allChecks = $false
}

# 2. Check Python Packages
Write-Host "2. Checking Python Packages..." -ForegroundColor White
$requiredPackages = @(
    "fastapi",
    "uvicorn",
    "motor",
    "pymongo",
    "opencv-python",
    "google-generativeai",
    "python-dotenv",
    "websockets"
)

$installedPackages = & .venv\Scripts\pip.exe list --format=freeze

foreach ($package in $requiredPackages) {
    if ($installedPackages -match "^$package") {
        Write-Host "   ✅ $package installed" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $package NOT installed" -ForegroundColor Red
        $allChecks = $false
    }
}

# 3. Check Frontend Dependencies
Write-Host "3. Checking Frontend Dependencies..." -ForegroundColor White
if (Test-Path "frontend\node_modules") {
    $packageCount = (Get-ChildItem "frontend\node_modules" -Directory).Count
    Write-Host "   ✅ node_modules exists ($packageCount packages)" -ForegroundColor Green
} else {
    Write-Host "   ❌ node_modules not found!" -ForegroundColor Red
    $allChecks = $false
}

# 4. Check Configuration Files
Write-Host "4. Checking Configuration Files..." -ForegroundColor White

if (Test-Path ".env") {
    Write-Host "   ✅ .env file exists" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  .env file not found (using defaults)" -ForegroundColor Yellow
}

if (Test-Path "requirements.txt") {
    Write-Host "   ✅ requirements.txt exists" -ForegroundColor Green
} else {
    Write-Host "   ❌ requirements.txt not found!" -ForegroundColor Red
    $allChecks = $false
}

if (Test-Path "frontend\package.json") {
    Write-Host "   ✅ package.json exists" -ForegroundColor Green
} else {
    Write-Host "   ❌ package.json not found!" -ForegroundColor Red
    $allChecks = $false
}

# 5. Check Project Structure
Write-Host "5. Checking Project Structure..." -ForegroundColor White

$requiredDirs = @("backend", "frontend", "alerts")
foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Host "   ✅ $dir/ directory exists" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $dir/ directory not found!" -ForegroundColor Red
        $allChecks = $false
    }
}

$backendFiles = @("backend\__init__.py", "backend\main.py", "backend\detection_engine.py", 
                  "backend\database.py", "backend\video_processor.py")
foreach ($file in $backendFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file exists" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file not found!" -ForegroundColor Red
        $allChecks = $false
    }
}

# 6. Check Node.js and npm
Write-Host "6. Checking Node.js Environment..." -ForegroundColor White
try {
    $nodeVersion = node --version
    $npmVersion = npm --version
    Write-Host "   ✅ Node.js: $nodeVersion" -ForegroundColor Green
    Write-Host "   ✅ npm: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Node.js or npm not found!" -ForegroundColor Red
    $allChecks = $false
}

# 7. Port Availability Check
Write-Host "7. Checking Port Availability..." -ForegroundColor White

$ports = @(8000, 5173)
foreach ($port in $ports) {
    $connection = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($connection) {
        Write-Host "   ⚠️  Port $port is already in use" -ForegroundColor Yellow
    } else {
        Write-Host "   ✅ Port $port is available" -ForegroundColor Green
    }
}

# Final Summary
Write-Host ""
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
if ($allChecks) {
    Write-Host "  ✅ ALL CHECKS PASSED!" -ForegroundColor Green
    Write-Host "  System is ready to run!" -ForegroundColor Green
} else {
    Write-Host "  ❌ SOME CHECKS FAILED!" -ForegroundColor Red
    Write-Host "  Please fix the issues above before running." -ForegroundColor Yellow
}
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($allChecks) {
    Write-Host "To start the application, run:" -ForegroundColor Cyan
    Write-Host "  .\start-all.ps1" -ForegroundColor White
    Write-Host ""
}
