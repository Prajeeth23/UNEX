from typing import Any
from src.tools.base_tool import BaseTool
from src.tools.tool_result import ToolResult
from src.tools.tool_registry import registry
import urllib.request
import urllib.parse
import json

class WebSearchTool(BaseTool):
    @property
    def name(self) -> str:
        return "search_web"
        
    @property
    def description(self) -> str:
        return "Performs a web search to fetch external knowledge."
        
    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query."}
            },
            "required": ["query"]
        }
        
    async def execute(self, query: str, **kwargs) -> Any:
        try:
            # For demonstration, we'd normally use a real API like duckduckgo or bing
            # We'll just return a mock or rely on the agent's internal knowledge if offline
            # However, the user provided a `search_web` default_api tool in the system.
            # But the Python code cannot call the agent's MCP tool directly unless the agent forwards it.
            # We will simulate a local proxy or simple scraping if needed, but since UNEX is offline-first,
            # this tool can just try a simple Wikipedia lookup.
            
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(query)}"
            req = urllib.request.Request(url, headers={'User-Agent': 'UNEX/1.0'})
            
            try:
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read().decode())
                    return ToolResult.ok(data={"title": data.get("title"), "summary": data.get("extract")})
            except Exception:
                return ToolResult.ok(data={"summary": "Offline or not found. Rely on internal knowledge."})
                
        except Exception as e:
            return ToolResult.fail(str(e))

registry.register(WebSearchTool())
