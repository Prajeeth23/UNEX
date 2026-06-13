<#
.SYNOPSIS
UNEX v1.0 Release Candidate Installer
.DESCRIPTION
Sets up the UNEX local AI environment, validates Python/Ollama, pulls required LLMs, and initializes the databases.
#>

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "       UNEX v1.0 INSTALLER            " -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# 1. Check Python
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Python is not installed or not in PATH." -ForegroundColor Red
    Exit
}
Write-Host "[OK] Found $pythonVersion" -ForegroundColor Green

# 2. Virtual Environment
Write-Host "[INFO] Creating Virtual Environment..."
python -m venv venv
.\venv\Scripts\Activate.ps1
Write-Host "[OK] Activated venv." -ForegroundColor Green

# 3. Dependencies
Write-Host "[INFO] Installing Dependencies..."
pip install -r requirements.txt
Write-Host "[OK] Dependencies installed." -ForegroundColor Green

# 4. Check Ollama
$ollamaVersion = ollama --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNING] Ollama is not installed. Please install from ollama.com" -ForegroundColor Yellow
} else {
    Write-Host "[OK] Found Ollama." -ForegroundColor Green
    
    # Optional Flag for pulling models
    if ($args -contains "-PullModels") {
        Write-Host "[INFO] Pulling qwen3:8b..."
        ollama pull qwen3:8b
        Write-Host "[INFO] Pulling qwen2.5vl:7b..."
        ollama pull qwen2.5vl:7b
        Write-Host "[INFO] Pulling nomic-embed-text..."
        ollama pull nomic-embed-text
    } else {
        Write-Host "[INFO] Skipping large model downloads. Run with -PullModels to download."
    }
}

# 5. Database Initialization
Write-Host "[INFO] Initializing SQLite Database..."
alembic upgrade head
Write-Host "[OK] Database ready." -ForegroundColor Green

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "   UNEX is ready for Production!      " -ForegroundColor Cyan
Write-Host " To start: python src\startup\bootstrap.py"
Write-Host "======================================" -ForegroundColor Cyan
