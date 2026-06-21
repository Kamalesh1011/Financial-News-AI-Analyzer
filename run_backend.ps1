Write-Host "Starting Financial News AI Analyzer Backend..." -ForegroundColor Cyan
Write-Host ""

# Check if venv exists
if (Test-Path "D:\dubai_project2\venv\Scripts\python.exe") {
    Write-Host "Using virtual environment..." -ForegroundColor Green
    $python = "D:\dubai_project2\venv\Scripts\python.exe"
} else {
    Write-Host "Using system Python..." -ForegroundColor Yellow
    $python = "python"
}

# Check if .env exists
if (-not (Test-Path "D:\dubai_project2\.env")) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "Please create .env from .env.example" -ForegroundColor Yellow
    exit 1
}

Write-Host "Starting FastAPI server on http://localhost:8001" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

& $python -m uvicorn src.api.routes:app --host 0.0.0.0 --port 8001 --reload
