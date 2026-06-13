from typing import Dict, List
from src.tools.base_tool import BaseTool

class ToolRegistry:
    """Central registry for discovering and accessing UNEX tools."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        
    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool
        print(f"[UNEX ToolRegistry] Registered tool: {tool.name}")
        
    def get_tool(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found in registry.")
        return self._tools[name]
        
    def get_all_tools(self) -> List[BaseTool]:
        return list(self._tools.values())
        
    def get_tools_schema(self) -> List[dict]:
        """Returns JSON schema for all registered tools, formatted for LLM usage."""
        schemas = []
        for tool in self._tools.values():
            schemas.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters_schema
                }
            })
        return schemas

# Global singleton instance
registry = ToolRegistry()
