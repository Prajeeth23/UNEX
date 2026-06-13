# UNEX Architecture Guide

UNEX uses a strictly modular architecture designed for offline inference.

## The Modules
1. **Core AI (`src/llm/`, `src/agent/`)**: LangGraph orchestrates Qwen models via Ollama. Tool calling is forced using Strict JSON schemas because Qwen lacks native function calling.
2. **Perception (`src/vision/`)**: Utilizing `mss` for 50ms screen captures and `PaddleOCR` for offline text extraction, the Vision System feeds visual data to `qwen2.5vl:7b`.
3. **Education (`src/education/`)**: A hybrid pipeline using PyMuPDF and Pydantic schemas to auto-grade and parse academic question papers.
4. **Memory & RAG (`src/memory/`, `src/rag/`)**: Persistent context is stored in SQLite (structured) and Qdrant (semantic vectors).
5. **Security (`src/security/`)**: Every tool call passes through an ActionValidator. Medium/High risk actions require Voice Confirmation from the user.
6. **Automation (`src/automation/`)**: apscheduler and watchdog enable asynchronous task execution without blocking the LangGraph workflow.

## Startup Flow
`bootstrap.py` -> `healthcheck.py` -> If Fail -> `recovery.py` -> If Fail -> `Settings(SafeMode)`.
