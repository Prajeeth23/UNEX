"""UNEX OS - Background Daemon & Process Manager for Windows."""
import os
import sys
import time
import subprocess
import signal
import psutil
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PID_FILE = PROJECT_ROOT / "unex_daemon.pid"
LOG_FILE = PROJECT_ROOT / "unex_daemon.log"

def is_running(pid: int) -> bool:
    try:
        proc = psutil.Process(pid)
        return proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False

def get_daemon_pid() -> int | None:
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            if is_running(pid):
                return pid
            else:
                PID_FILE.unlink(missing_ok=True)
        except Exception:
            PID_FILE.unlink(missing_ok=True)
    return None

def start_daemon():
    existing_pid = get_daemon_pid()
    if existing_pid:
        print(f"[UNEX Daemon] Already running under PID {existing_pid}")
        return

    python_exe = sys.executable
    script_path = str(PROJECT_ROOT / "start_unex.py")

    print("[UNEX Daemon] Launching UNEX OS background service...")
    with open(LOG_FILE, "a", encoding="utf-8") as log_out:
        # Launch detached background process on Windows
        proc = subprocess.Popen(
            [python_exe, script_path],
            cwd=str(PROJECT_ROOT),
            stdout=log_out,
            stderr=log_out,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
    
    PID_FILE.write_text(str(proc.pid))
    print(f"[UNEX Daemon] Successfully started with PID {proc.pid}")
    print(f"[UNEX Daemon] Dashboard URL: http://localhost:8000/dashboard/")
    print(f"[UNEX Daemon] Log file: {LOG_FILE}")

def stop_daemon():
    pid = get_daemon_pid()
    if not pid:
        print("[UNEX Daemon] No active daemon found.")
        return

    print(f"[UNEX Daemon] Stopping process {pid} and child processes...")
    try:
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            try:
                child.terminate()
            except Exception:
                pass
        parent.terminate()
        gone, alive = psutil.wait_procs([parent], timeout=5)
        for p in alive:
            p.kill()
    except Exception as e:
        print(f"[UNEX Daemon] Error during stop: {e}")
    finally:
        PID_FILE.unlink(missing_ok=True)
        print("[UNEX Daemon] Stopped successfully.")

def status_daemon():
    pid = get_daemon_pid()
    if pid:
        proc = psutil.Process(pid)
        mem = proc.memory_info().rss / (1024 * 1024)
        print(f"[UNEX Daemon] ONLINE (PID: {pid}, Memory: {mem:.1f} MB)")
        print(f"[UNEX Daemon] Dashboard: http://localhost:8000/dashboard/")
    else:
        print("[UNEX Daemon] OFFLINE")

def main():
    parser = argparse.ArgumentParser(description="UNEX Background Daemon Controller")
    parser.add_argument("action", choices=["start", "stop", "restart", "status"], default="status", nargs="?")
    args = parser.parse_args()

    if args.action == "start":
        start_daemon()
    elif args.action == "stop":
        stop_daemon()
    elif args.action == "restart":
        stop_daemon()
        time.sleep(1)
        start_daemon()
    elif args.action == "status":
        status_daemon()

if __name__ == "__main__":
    main()
