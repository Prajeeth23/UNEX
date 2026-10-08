import pytest
import asyncio
from src.tools.tool_manager import ToolManager

# A mock voice command parsing simulator to test End-to-End tool execution
class VoiceSimulator:
    def __init__(self):
        self.tool_manager = ToolManager()
        
    async def simulate_command(self, intent_tool_name: str, **params):
        tool = self.tool_manager.get_tool(intent_tool_name)
        if not tool:
            return {"status": "error", "error": f"Tool {intent_tool_name} not found"}
        return await tool.execute(**params)

def test_e2e_tool_resolution():
    sim = VoiceSimulator()
    tool = sim.tool_manager.get_tool("system_info")
    assert tool is not None
    assert tool.name in ["system_info", "get_system_info"]
    
def test_e2e_safe_mode_degradation():
    from src.config.settings import settings
    # Force safe mode
    settings.enable_safe_mode()
    assert settings.llm_model is None
    
    # We should still be able to run safe deterministic tools
    sim = VoiceSimulator()
    result = asyncio.run(sim.simulate_command("system_info"))
    assert result.success is True
