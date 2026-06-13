$ErrorActionPreference = "Stop"

Write-Host "=========================================="
Write-Host " UNEX - Local Setup Script"
Write-Host "=========================================="

# 1. Install Ollama if not installed
Write-Host "`n[1] Checking for Ollama installation..."
$ollamaInstalled = Get-Command "ollama" -ErrorAction SilentlyContinue

if (-not $ollamaInstalled) {
    Write-Host "Ollama not found. Downloading and installing..."
    $ollamaInstallerUrl = "https://ollama.com/download/OllamaSetup.exe"
    $installerPath = "$env:TEMP\OllamaSetup.exe"
    
    Invoke-WebRequest -Uri $ollamaInstallerUrl -OutFile $installerPath
    Write-Host "Running Ollama installer... Please follow any prompts."
    Start-Process -FilePath $installerPath -Wait
    
    # Verify installation
    $ollamaInstalled = Get-Command "ollama" -ErrorAction SilentlyContinue
    if (-not $ollamaInstalled) {
        Write-Error "Failed to verify Ollama installation. Please install it manually and run this script again."
        exit 1
    }
} else {
    Write-Host "Ollama is already installed."
}

# 2. Pull Required Models
Write-Host "`n[2] Pulling local models via Ollama..."
$models = @("qwen3:8b", "qwen2.5vl:7b")

foreach ($model in $models) {
    Write-Host "Checking for model: $model"
    # Execute ollama list and check if model exists. 
    # If not, pull it.
    $modelExists = ollama list | Select-String $model
    
    if (-not $modelExists) {
        Write-Host "Pulling $model (this may take a while)..."
        ollama pull $model
    } else {
        Write-Host "Model $model is already present."
    }
}

# 3. Setup Python Virtual Environment
Write-Host "`n[3] Setting up Python virtual environment..."
if (-not (Test-Path "$PSScriptRoot\..\venv")) {
    Write-Host "Creating venv..."
    py -m venv "$PSScriptRoot\..\venv"
} else {
    Write-Host "Virtual environment already exists."
}

Write-Host "Installing Python dependencies..."
& "$PSScriptRoot\..\venv\Scripts\pip.exe" install -r "$PSScriptRoot\..\requirements.txt"

Write-Host "`n=========================================="
Write-Host " Setup Complete! You are ready to run UNEX."
Write-Host "=========================================="
