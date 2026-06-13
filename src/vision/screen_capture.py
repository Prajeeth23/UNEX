import mss
import mss.tools
from PIL import Image
import os
import tempfile

class ScreenCapture:
    """High-speed screen capturing utility."""
    
    @staticmethod
    def capture_fullscreen() -> Image.Image:
        """Captures the primary monitor."""
        with mss.mss() as sct:
            monitor = sct.monitors[1] # Primary monitor
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            return img
            
    @staticmethod
    def capture_region(left: int, top: int, width: int, height: int) -> Image.Image:
        """Captures a specific bounding box."""
        with mss.mss() as sct:
            region = {"top": top, "left": left, "width": width, "height": height}
            sct_img = sct.grab(region)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            return img
            
    @staticmethod
    def capture_active_window() -> Image.Image:
        """Captures only the currently active window."""
        from src.vision.desktop_context import DesktopContext
        
        info = DesktopContext.get_active_window_info()
        if not info:
            # Fallback to fullscreen if no active window found
            return ScreenCapture.capture_fullscreen()
            
        return ScreenCapture.capture_region(
            info['left'], info['top'], info['width'], info['height']
        )
