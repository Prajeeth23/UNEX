import json
from src.vision.vision_models import VisionModelProvider

class UIDetector:
    def __init__(self, provider: VisionModelProvider):
        self.provider = provider
        
    async def analyze(self, base64_img: str) -> dict:
        prompt = "Analyze this screenshot. Return a JSON object with keys: 'buttons', 'inputs', 'dialogs', 'warnings'. List the visible text or label for each detected element."
        sys_prompt = "You are a UI analysis expert. Output ONLY valid JSON."
        
        res = await self.provider.analyze_image(base64_img, prompt, sys_prompt)
        
        try:
            # Basic parsing of JSON block
            start = res.find('{')
            end = res.rfind('}') + 1
            if start != -1 and end != 0:
                return json.loads(res[start:end])
        except Exception:
            pass
            
        return {"buttons": [], "inputs": [], "dialogs": [], "warnings": [], "raw": res}
