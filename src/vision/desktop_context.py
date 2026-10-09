import pygetwindow as gw
import psutil
import win32gui
import win32process
import win32api
import win32con
from typing import Dict, Any, Optional
from src.utils.win32_helper import ensure_desktop_access

class DesktopContext:
    """Provides awareness of the currently active desktop state and foreground window."""
    
    @staticmethod
    def _calculate_quadrant(left: int, top: int, width: int, height: int) -> str:
        """Determines which screen quadrant the window predominantly occupies."""
        try:
            screen_w = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            screen_h = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            if width >= screen_w * 0.85 and height >= screen_h * 0.85:
                return "fullscreen"
            
            mid_x = left + (width // 2)
            mid_y = top + (height // 2)
            half_w = screen_w // 2
            half_h = screen_h // 2
            
            if mid_x < half_w and mid_y < half_h:
                return "top-left"
            elif mid_x >= half_w and mid_y < half_h:
                return "top-right"
            elif mid_x < half_w and mid_y >= half_h:
                return "bottom-left"
            else:
                return "bottom-right"
        except Exception:
            return "unknown"

    @staticmethod
    def get_active_window_info() -> Optional[Dict[str, Any]]:
        ensure_desktop_access()
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd and hwnd != 0:
                title = win32gui.GetWindowText(hwnd) or ""
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                proc_name = "unknown"
                if pid > 0:
                    try:
                        proc_name = psutil.Process(pid).name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        proc_name = "unknown"
                        
                rect = win32gui.GetWindowRect(hwnd)
                left, top, right, bottom = rect
                width = max(0, right - left)
                height = max(0, bottom - top)
                
                placement = win32gui.GetWindowPlacement(hwnd)
                is_maximized = placement[1] == win32con.SW_SHOWMAXIMIZED
                is_minimized = placement[1] == win32con.SW_SHOWMINIMIZED
                
                quadrant = DesktopContext._calculate_quadrant(left, top, width, height)
                
                return {
                    "hwnd": hwnd,
                    "title": title,
                    "pid": pid,
                    "process_name": proc_name,
                    "left": left,
                    "top": top,
                    "right": right,
                    "bottom": bottom,
                    "width": width,
                    "height": height,
                    "is_maximized": is_maximized,
                    "is_minimized": is_minimized,
                    "quadrant": quadrant
                }
        except Exception as e:
            pass

        # Fallback to pygetwindow
        try:
            active_win = gw.getActiveWindow()
            if not active_win:
                return None
                
            width = max(0, active_win.width)
            height = max(0, active_win.height)
            return {
                "hwnd": getattr(active_win, "_hWnd", 0),
                "title": active_win.title or "",
                "pid": 0,
                "process_name": "unknown",
                "left": active_win.left,
                "top": active_win.top,
                "right": active_win.left + width,
                "bottom": active_win.top + height,
                "width": width,
                "height": height,
                "is_maximized": active_win.isMaximized,
                "is_minimized": getattr(active_win, "isMinimized", False),
                "quadrant": DesktopContext._calculate_quadrant(active_win.left, active_win.top, width, height)
            }
        except Exception as e:
            return None
            
    @staticmethod
    def get_context_summary() -> str:
        win_info = DesktopContext.get_active_window_info()
        if not win_info:
            return "No active window detected."
            
        title = win_info.get("title", "Untitled")
        proc = win_info.get("process_name", "unknown")
        pid = win_info.get("pid", 0)
        quad = win_info.get("quadrant", "unknown")
        w = win_info.get("width", 0)
        h = win_info.get("height", 0)
        return f"Active Window: '{title}' [Process: {proc}, PID: {pid}, Quadrant: {quad}, Size: {w}x{h}]"

