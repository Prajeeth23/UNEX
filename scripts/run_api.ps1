$ErrorActionPreference = "Stop"

Write-Host "=========================================="
Write-Host " Starting UNEX API"
Write-Host "=========================================="

$pythonExe = "$PSScriptRoot\..\venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Error "Python virtual environment not found. Please run setup.ps1 first."
    exit 1
}

# Set PYTHONPATH to the project root
$env:PYTHONPATH = "$PSScriptRoot\.."

Write-Host "Starting Uvicorn server on http://localhost:8000..."
& $pythonExe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
