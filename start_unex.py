"""UNEX OS - Master Startup & Web Server Launcher."""
import asyncio
import sys
import os
import uvicorn

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.startup.bootstrap import bootstrap_unex
from src.gui.app_window import launch_gui_window

def is_port_in_use(port: int = 8000) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def main():
    print("=" * 60)
    print("        UNEX OS - UNIFIED MISSION CONTROL LAUNCHER       ")
    print("=" * 60)
    
    # 0. If UNEX is already running, immediately open GUI window and exit
    if is_port_in_use(8000):
        print("[*] UNEX OS is already active in the background.")
        print("[*] Launching Mission Control Desktop GUI window...")
        launch_gui_window()
        import time
        time.sleep(2)
        return

    # 1. Run Pre-flight Bootstrap Checks
    is_ready = asyncio.run(bootstrap_unex())
    if not is_ready:
        print("[WARNING] UNEX running with degraded features / Safe Mode enabled.")

    print("\n" + "=" * 60)
    print("  [*] UNEX OS Dashboard: http://localhost:8000/dashboard/")
    print("  [*] API Documentation: http://localhost:8000/docs")
    print("=" * 60 + "\n")

    # 2. Launch Uvicorn Server
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    main()
