import json
from typing import Dict, List, Optional
import aiohttp
from src.llm.provider import LLMProvider
from src.config.defaults import Defaults

class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434", default_model: Optional[str] = None):
        self.base_url = base_url
        self.default_model = default_model or Defaults.LLM_MODEL

    @property
    def host(self) -> str:
        return self.base_url

    def generate(self, prompt: str, **kwargs) -> str:
        # Synchronous wrapper could use requests, but sticking to async since we prefer async architecture
        raise NotImplementedError("Use agenerate instead for async architecture")

    def generate_chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        raise NotImplementedError("Use agenerate_chat instead")

    async def agenerate(self, prompt: str, model: Optional[str] = None, **kwargs) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model or self.default_model,
            "prompt": prompt,
            "stream": False,
            **kwargs
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("response", "")

    async def agenerate_chat(self, messages: List[Dict[str, str]], model: Optional[str] = None, **kwargs) -> str:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "stream": False,
            **kwargs
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                message = data.get("message", {})
                
                # Check for native tool calls in Ollama
                if "tool_calls" in message and message["tool_calls"]:
                    # Convert to the format expected by ToolManager
                    formatted_calls = []
                    for tc in message["tool_calls"]:
                        fn = tc.get("function", {})
                        formatted_calls.append({
                            "name": fn.get("name"),
                            "arguments": fn.get("arguments", {})
                        })
                    return f"```json\n{json.dumps(formatted_calls)}\n```"
                    
                return message.get("content", "")
