import json
from src.vision.vision_models import VisionModelProvider

class TableExtractor:
    def __init__(self, provider: VisionModelProvider):
        self.provider = provider
        
    async def extract(self, base64_img: str) -> list:
        prompt = "Extract the table from this image. Return a JSON array of objects, where each object represents a row. The keys should be the column headers."
        sys_prompt = "You are a precise data entry expert. Output ONLY valid JSON."
        
        res = await self.provider.analyze_image(base64_img, prompt, sys_prompt)
        try:
            start = res.find('[')
            end = res.rfind(']') + 1
            if start != -1 and end != 0:
                return json.loads(res[start:end])
        except Exception:
            pass
            
        return []
