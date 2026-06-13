import json
from src.vision.vision_models import VisionModelProvider

class ChartAnalyzer:
    def __init__(self, provider: VisionModelProvider):
        self.provider = provider
        
    async def analyze(self, base64_img: str) -> dict:
        prompt = "Analyze this chart/graph. Return a JSON object with keys: 'chart_type' (e.g., Bar, Pie, Line), 'labels' (array of strings), 'extracted_values' (array of numbers/strings), 'summary' (a brief text summary of the trend/data)."
        sys_prompt = "You are a data analyst. Output ONLY valid JSON."
        
        res = await self.provider.analyze_image(base64_img, prompt, sys_prompt)
        try:
            start = res.find('{')
            end = res.rfind('}') + 1
            if start != -1 and end != 0:
                return json.loads(res[start:end])
        except Exception:
            pass
            
        return {"chart_type": "Unknown", "labels": [], "extracted_values": [], "summary": "Failed to parse chart data.", "raw": res}
