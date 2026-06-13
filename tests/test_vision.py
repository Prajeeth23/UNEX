import pytest
import os
from PIL import Image
from src.vision.image_loader import ImageLoader
from src.vision.desktop_context import DesktopContext
from src.vision.multimodal_router import MultimodalRouter
import asyncio

def create_dummy_image(filepath: str):
    img = Image.new('RGB', (100, 100), color = 'red')
    img.save(filepath)

def test_image_loader(tmp_path):
    img_path = os.path.join(tmp_path, "test.png")
    create_dummy_image(img_path)
    
    b64 = ImageLoader.load_base64_from_file(img_path)
    assert isinstance(b64, str)
    assert len(b64) > 100 # Should be a reasonably long base64 string
    
def test_desktop_context():
    # This might return None if running headless in CI, but on a desktop it should return dict
    info = DesktopContext.get_active_window_info()
    if info is not None:
        assert "title" in info
        assert "width" in info
        
class MockVisionProvider:
    async def analyze_image(self, base64_image: str, prompt: str, system_prompt: str = "") -> str:
        # Mock responses based on prompt
        if "Classify" in prompt:
            return "UI"
        elif "buttons" in prompt:
            return '{"buttons": ["Submit"], "inputs": ["Email"], "dialogs": [], "warnings": []}'
        return "{}"
        
def test_multimodal_router():
    router = MultimodalRouter(MockVisionProvider())
    
    # Passing a dummy image
    result = asyncio.run(router.process_image("dummy_base64"))
    
    assert result["classification"] == "UI"
    assert "analysis" in result
    assert "buttons" in result["analysis"]
    assert result["analysis"]["buttons"] == ["Submit"]
