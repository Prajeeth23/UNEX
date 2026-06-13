# UNEX User Guide

Welcome to UNEX (v1.0 RC), your Jarvis-style Local AI Operating System. 
UNEX runs entirely offline, leveraging Ollama to grant you privacy-first AI intelligence.

## Starting UNEX
To start UNEX, simply run the PowerShell installer to set up your environment, and then launch the bootstrap daemon:
```powershell
python src/startup/bootstrap.py
```
This will run all necessary health checks, verify your databases, load the Qwen models, and start the FastAPI backend.

## Voice Commands
UNEX is constantly listening for its Wake Word: **"UNEX"**.
- "UNEX, what is on my screen right now?"
- "UNEX, summarize my downloaded PDFs."
- "UNEX, open VS Code."

## Safemode
If you see UNEX start in Safe Mode, it means the Heavy AI Models (like Ollama) failed to initialize. In this mode, UNEX can only execute deterministic background tasks.

## Backups
You can trigger a manual backup of your visual memory, SQLite databases, and RAG knowledge base via:
`POST http://localhost:8000/system/backup`
