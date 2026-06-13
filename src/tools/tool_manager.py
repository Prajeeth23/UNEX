import json
from typing import List, Dict, Any, Tuple
from src.tools.tool_registry import registry
from src.tools.tool_result import ToolResult
from src.security.action_validator import validator, ApprovalRequiredException

class ToolManager:
    """Manages the execution of tools requested by the LLM."""
    
    @staticmethod
    async def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        try:
            # Validate security risk before fetching tool
            try:
                validator.validate_action(tool_name, arguments)
            except ApprovalRequiredException as e:
                # Return a specific ToolResult indicating approval is required
                return ToolResult.fail(f"APPROVAL_REQUIRED:{e.risk_level.value}:{e.message}")
            except PermissionError as e:
                return ToolResult.fail(f"PERMISSION_DENIED:{str(e)}")

            tool = registry.get_tool(tool_name)
            print(f"[UNEX ToolManager] Executing {tool_name} with args: {arguments}")
            result = await tool.execute(**arguments)
            if isinstance(result, ToolResult):
                return result
            return ToolResult.ok(data=result)
        except Exception as e:
            print(f"[UNEX ToolManager] Error executing {tool_name}: {e}")
            validator.log_failure(tool_name, arguments, str(e))
            return ToolResult.fail(error=str(e))
            
    @staticmethod
    def parse_tool_calls(response_text: str) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Parses LLM output for tool calls. 
        Assuming the LLM outputs a specific format like:
        ```json
        {"name": "file_search", "arguments": {"query": "test"}}
        ```
        This is a basic parser. A more robust implementation would hook into the LLMProvider's native tool calling format.
        """
        tool_calls = []
        try:
            # Simple heuristic to find JSON blocks that look like tool calls
            start = response_text.find("```json")
            if start != -1:
                start += 7
                end = response_text.find("```", start)
                if end != -1:
                    json_str = response_text[start:end].strip()
                    data = json.loads(json_str)
                    
                    if isinstance(data, dict) and "name" in data and "arguments" in data:
                        tool_calls.append((data["name"], data["arguments"]))
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and "name" in item and "arguments" in item:
                                tool_calls.append((item["name"], item["arguments"]))
        except Exception:
            pass
            
        return tool_calls
