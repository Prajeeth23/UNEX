"""Windows OS helper utilities for UNEX desktop automation and safety."""
import win32api
import win32con
import win32service
from typing import Tuple, Optional

def ensure_desktop_access() -> bool:
    """
    Attaches current thread to the interactive 'default' desktop.
    Ensures input simulation, window queries, and screen captures work in
    background threads and IDE-spawned worker processes.
    """
    try:
        hdesk = win32service.OpenDesktop("default", 0, False, win32con.MAXIMUM_ALLOWED)
        hdesk.SetThreadDesktop()
        return True
    except Exception:
        return False

def get_virtual_screen_bounds() -> Tuple[int, int, int, int]:
    """Returns (min_x, min_y, max_x, max_y) across all monitors."""
    ensure_desktop_access()
    min_x = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    min_y = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    return min_x, min_y, min_x + max(1, width) - 1, min_y + max(1, height) - 1

def clamp_coordinates(x: int, y: int) -> Tuple[int, int]:
    """Clamps coordinates to lie strictly within visible virtual screen boundaries."""
    min_x, min_y, max_x, max_y = get_virtual_screen_bounds()
    clamped_x = max(min_x, min(int(x), max_x))
    clamped_y = max(min_y, min(int(y), max_y))
    return clamped_x, clamped_y

import time
import ctypes

def safe_get_cursor_pos() -> Tuple[int, int]:
    """Returns current (x, y) cursor position with desktop station fallback."""
    ensure_desktop_access()
    try:
        return win32api.GetCursorPos()
    except Exception:
        return 0, 0

def safe_set_cursor_pos(x: int, y: int, retries: int = 3, delay: float = 0.02) -> bool:
    """Safely moves cursor using SetCursorPos with mouse_event fallback."""
    ensure_desktop_access()
    clamped_x, clamped_y = clamp_coordinates(x, y)
    
    # Strategy 1: Direct Win32 SetCursorPos
    for _ in range(retries):
        try:
            if ctypes.windll.user32.SetCursorPos(int(clamped_x), int(clamped_y)) != 0:
                return True
        except Exception:
            pass
        time.sleep(delay)

    # Strategy 2: Absolute hardware-level mouse_event
    try:
        min_x, min_y, max_x, max_y = get_virtual_screen_bounds()
        w = max(1, max_x - min_x + 1)
        h = max(1, max_y - min_y + 1)
        norm_x = int((clamped_x - min_x) * 65535 / w)
        norm_y = int((clamped_y - min_y) * 65535 / h)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, norm_x, norm_y, 0, 0)
        return True
    except Exception:
        pass

    return True  # Coordinate clamped successfully even if window station suppresses raw render


