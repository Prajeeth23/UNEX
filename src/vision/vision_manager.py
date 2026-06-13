import asyncio
from src.vision.vision_models import VisionModelProvider
from src.vision.multimodal_router import MultimodalRouter
from src.vision.screen_capture import ScreenCapture
from src.vision.image_loader import ImageLoader
from src.vision.screenshot_manager import ScreenshotManager
from src.vision.ocr_engine import OCREngine
from typing import Dict, Any

class VisionManager:
    """Master controller for UNEX Multimodal Vision."""
    
    def __init__(self):
        self.provider = VisionModelProvider()
        self.router = MultimodalRouter(self.provider)
        self.memory = ScreenshotManager()
        self.ocr = OCREngine()
        
    async def analyze_screen(self, region: str = "fullscreen") -> Dict[str, Any]:
        """Captures the screen, saves memory, and analyzes it."""
        print(f"[VisionManager] Capturing screen ({region})...")
        if region == "active":
            img = ScreenCapture.capture_active_window()
        else:
            img = ScreenCapture.capture_fullscreen()
            
        # Save to memory
        filepath = self.memory.save_screenshot(img)
        print(f"[VisionManager] Saved screenshot to {filepath}")
        
        # Load base64
        base64_img = ImageLoader.load_base64_from_pil(img)
        
        # Run multimodal router
        analysis = await self.router.process_image(base64_img)
        return analysis
        
    async def analyze_image_file(self, filepath: str, explicit_type: str = None) -> Dict[str, Any]:
        """Analyzes an image from disk."""
        base64_img = ImageLoader.load_base64_from_file(filepath)
        analysis = await self.router.process_image(base64_img, explicit_type)
        return analysis
        
    def extract_text_from_screen(self) -> str:
        """Fast OCR on the current screen (bypasses LLM)."""
        img = ScreenCapture.capture_fullscreen()
        return self.ocr.extract_text(img)
