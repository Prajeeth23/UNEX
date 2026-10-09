import pytest
import asyncio
from src.tools.tool_registry import registry
from src.tools.tool_result import ToolResult
from src.vision.desktop_context import DesktopContext
from src.security.risk_classifier import RiskClassifier
from src.security.permissions import RiskLevel

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

def test_get_active_window_tool():
    tool = registry.get_tool("get_active_window")
    assert tool is not None
    
    result = asyncio.run(tool.execute())
    assert isinstance(result, ToolResult)
    assert result.success is True
    assert "active_window" in result.data
    if result.data["active_window"]:
        win = result.data["active_window"]
        assert "title" in win
        assert "process_name" in win
        assert "quadrant" in win

def test_desktop_context_summary():
    summary = DesktopContext.get_context_summary()
    assert isinstance(summary, str)
    assert len(summary) > 0

def test_clipboard_control_lifecycle():
    tool = registry.get_tool("clipboard_control")
    assert tool is not None
    
    test_token = "UNEX_PHASE_4_TEST_PAYLOAD_XYZ"
    write_res = asyncio.run(tool.execute(action="write", text=test_token))
    assert write_res.success is True
    
    read_res = asyncio.run(tool.execute(action="read"))
    assert read_res.success is True
    assert read_res.data["text"] == test_token
    
    clear_res = asyncio.run(tool.execute(action="clear"))
    assert clear_res.success is True

def test_mouse_control_actions():
    tool = registry.get_tool("mouse_control")
    assert tool is not None
    
    # Get current cursor position
    pos_res = asyncio.run(tool.execute(action="get_position"))
    assert pos_res.success is True
    assert "x" in pos_res.data and "y" in pos_res.data
    
    # Move cursor safely
    move_res = asyncio.run(tool.execute(action="move", x=pos_res.data["x"], y=pos_res.data["y"]))
    assert move_res.success is True
    assert "x" in move_res.data

def test_keyboard_control_safety():
    tool = registry.get_tool("keyboard_control")
    assert tool is not None
    
    # Blocked critical system shortcut
    blocked_res = asyncio.run(tool.execute(action="hotkey", keys="ctrl+alt+del"))
    assert blocked_res.success is False
    assert "restricted" in blocked_res.error or "Security blocked" in blocked_res.error
    
    # Press safe key
    press_res = asyncio.run(tool.execute(action="press", keys="shift"))
    assert press_res.success is True

def test_computer_control_risk_classification():
    classifier = RiskClassifier()
    assert classifier.classify_tool("get_active_window") == RiskLevel.LOW
    assert classifier.classify_tool("list_windows") == RiskLevel.LOW
    assert classifier.classify_tool("clipboard_control") == RiskLevel.LOW
    assert classifier.classify_tool("mouse_control") == RiskLevel.MEDIUM
    assert classifier.classify_tool("keyboard_control") == RiskLevel.MEDIUM
    assert classifier.classify_tool("extract_screen_text") == RiskLevel.LOW
    assert classifier.classify_tool("analyze_screen") == RiskLevel.LOW

def test_app_discovery():
    from src.tools.application_catalog import ApplicationCatalog
    catalog = ApplicationCatalog()
    assert isinstance(catalog.apps, dict)
