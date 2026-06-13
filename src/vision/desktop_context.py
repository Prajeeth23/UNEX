import pygetwindow as gw
import psutil
from typing import Dict, Any, Optional

class DesktopContext:
    """Provides awareness of the currently active desktop state."""
    
    @staticmethod
    def get_active_window_info() -> Optional[Dict[str, Any]]:
        try:
            active_win = gw.getActiveWindow()
            if not active_win:
                return None
                
            info = {
                "title": active_win.title,
                "left": active_win.left,
                "top": active_win.top,
                "width": active_win.width,
                "height": active_win.height,
                "is_maximized": active_win.isMaximized
            }
            
            # We can try to guess the process name from the title heuristics, 
            # or in a more advanced Windows setup, use win32gui to get the PID.
            # For simplicity, we just provide the window properties.
            return info
        except Exception as e:
            print(f"[DesktopContext] Error getting active window: {e}")
            return None
            
    @staticmethod
    def get_context_summary() -> str:
        win_info = DesktopContext.get_active_window_info()
        if not win_info:
            return "No active window detected."
            
        return f"Active Window: '{win_info['title']}' (Size: {win_info['width']}x{win_info['height']})"
