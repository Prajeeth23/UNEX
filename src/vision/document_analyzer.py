import json
from src.vision.vision_models import VisionModelProvider

class DocumentAnalyzer:
    def __init__(self, provider: VisionModelProvider):
        self.provider = provider
        
    async def analyze(self, base64_img: str) -> dict:
        prompt = "Analyze this educational document/handwritten page. Return a JSON object with 'text_content' (extracted text), 'diagrams_detected' (boolean), 'equations_detected' (boolean), and 'summary'."
        sys_prompt = "You are a multimodal document analyzer. Output ONLY valid JSON."
        
        res = await self.provider.analyze_image(base64_img, prompt, sys_prompt)
        try:
            start = res.find('{')
            end = res.rfind('}') + 1
            if start != -1 and end != 0:
                return json.loads(res[start:end])
        except Exception:
            pass
            
        return {"text_content": "", "diagrams_detected": False, "equations_detected": False, "summary": "Failed to analyze document.", "raw": res}
