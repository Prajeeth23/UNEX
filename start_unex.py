"""UNEX OS - Master Startup & Web Server Launcher."""
import asyncio
import sys
import os
import uvicorn

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.startup.bootstrap import bootstrap_unex

def main():
    print("=" * 60)
    print("        UNEX OS - UNIFIED MISSION CONTROL LAUNCHER       ")
    print("=" * 60)
    
    # 1. Run Pre-flight Bootstrap Checks
    is_ready = asyncio.run(bootstrap_unex())
    if not is_ready:
        print("[WARNING] UNEX running with degraded features / Safe Mode enabled.")

    print("\n" + "=" * 60)
    print("  🚀 UNEX OS Dashboard: http://localhost:8000/dashboard/")
    print("  📖 API Documentation: http://localhost:8000/docs")
    print("=" * 60 + "\n")

    # 2. Launch Uvicorn Server
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    main()
