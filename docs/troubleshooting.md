# UNEX Troubleshooting Guide

## Q: UNEX Starts in Safe Mode
**Cause:** The `healthcheck.py` failed to ping the Database or Ollama.
**Fix:** Ensure `Ollama` is running (`ollama serve`) and that you have at least 8GB of free system memory to load the models. If `unex.db` is corrupt, delete it and run `alembic upgrade head`.

## Q: "Out of VRAM" Error during Vision Tasks
**Cause:** `qwen3:8b` and `qwen2.5vl:7b` cannot fit inside your 4GB RTX 3050 simultaneously. 
**Fix:** Ollama is designed to automatically swap models. Wait 5-10 seconds for the swap to complete. If it hangs, close background applications consuming VRAM (like VS Code or Chrome hardware acceleration).

## Q: Voice Wake Word Not Triggering
**Cause:** `pvporcupine` is extremely sensitive to microphone drivers.
**Fix:** Ensure your default input device in Windows 11 is correctly configured. Check `unex.log` for audio buffer underrun errors.
