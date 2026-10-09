"""UNEX OS - Native Desktop GUI Window Launcher.
Launches the Mission Control Dashboard in standalone App Mode (Chromium PWA container)
with zero URL address bars, zero tabs, and dedicated window styling.
"""
import os
import subprocess
import threading
import time
import webbrowser
import logging

logger = logging.getLogger("UNEX.GUI")

def launch_gui_window():
    """Spawns the standalone desktop GUI window in a background daemon thread."""
    def _runner():
        time.sleep(1.0)
        
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        url = "http://localhost:8000/dashboard/"
        
        project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        profile_dir = os.path.join(project_dir, ".unex_gui_profile")
        os.makedirs(profile_dir, exist_ok=True)

        browser_exe = None
        if os.path.exists(chrome_path):
            browser_exe = chrome_path
        elif os.path.exists(edge_path):
            browser_exe = edge_path

        if browser_exe:
            cmd = [
                browser_exe,
                f"--app={url}",
                "--window-size=1440,920",
                f"--user-data-dir={profile_dir}",
                "--no-first-run",
                "--no-default-browser-check"
            ]
            try:
                logger.info(f"Launching standalone GUI app via {browser_exe}")
                subprocess.Popen(cmd)
                return
            except Exception as e:
                logger.warning(f"Failed to launch App Mode ({e}), falling back to default browser.")

        # Fallback
        webbrowser.open(url)

    thread = threading.Thread(target=_runner, daemon=True, name="UNEX-GUI-Launcher")
    thread.start()
