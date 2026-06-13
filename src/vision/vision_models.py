import aiohttp
import json
import os
from typing import Dict, Any

class VisionModelProvider:
    """Dedicated provider for multimodal Ollama models (e.g., qwen2.5vl:7b)."""
    
    def __init__(self):
        self.host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        # We specify qwen2.5vl as the default vision model
        self.model = os.getenv("VISION_MODEL", "qwen2.5vl:7b")
        
    async def analyze_image(self, base64_image: str, prompt: str, system_prompt: str = "") -> str:
        url = f"{self.host}/api/generate"
        
        # Ollama expects 'images' as a list of base64 strings in the request
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "images": [base64_image],
            "stream": False,
            "options": {
                "temperature": 0.1, # Keep it deterministic for JSON outputs
                "num_ctx": 4096
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=60) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", "").strip()
                    else:
                        error_text = await response.text()
                        print(f"[VisionModel] API Error: {response.status} - {error_text}")
                        return ""
        except Exception as e:
            print(f"[VisionModel] Connection Error: {e}")
            return ""
