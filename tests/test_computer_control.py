import pytest
from src.tools.tool_registry import registry
from src.tools.tool_result import ToolResult
import asyncio

def test_system_info_tool():
    tool = registry.get_tool("get_system_info")
    assert tool is not None
    
    result = asyncio.run(tool.execute())
    assert isinstance(result, ToolResult)
    assert result.success is True
    assert "cpu_usage" in result.data
    assert "ram_usage" in result.data

def test_list_windows_tool():
    tool = registry.get_tool("list_windows")
    assert tool is not None
    
    result = asyncio.run(tool.execute())
    assert isinstance(result, ToolResult)
    assert result.success is True
    assert "open_windows" in result.data
    assert isinstance(result.data["open_windows"], list)
    
def test_app_discovery():
    from src.tools.application_catalog import ApplicationCatalog
    catalog = ApplicationCatalog()
    # On a normal windows machine, there should be at least a few apps discovered
    # If CI/CD, this might be empty depending on environment.
    assert isinstance(catalog.apps, dict)
