import asyncio
import time
import ctypes
from typing import Any, Dict, List, Union, Optional
import win32api
import win32con
import win32clipboard
from src.tools.base_tool import BaseTool
from src.tools.tool_result import ToolResult
from src.tools.tool_registry import registry
from src.utils.win32_helper import ensure_desktop_access, clamp_coordinates, safe_get_cursor_pos, safe_set_cursor_pos

# --- Windows Input SendInput Structures for Unicode typing ---
user32 = ctypes.windll.user32
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
INPUT_KEYBOARD = 1

PUL = ctypes.POINTER(ctypes.c_ulong)

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL)
    ]

class INPUT_UNION(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT)]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("u", INPUT_UNION)
    ]

# Common Virtual Key Map
VK_MAP = {
    "ctrl": win32con.VK_CONTROL,
    "control": win32con.VK_CONTROL,
    "alt": win32con.VK_MENU,
    "shift": win32con.VK_SHIFT,
    "win": win32con.VK_LWIN,
    "windows": win32con.VK_LWIN,
    "enter": win32con.VK_RETURN,
    "return": win32con.VK_RETURN,
    "esc": win32con.VK_ESCAPE,
    "escape": win32con.VK_ESCAPE,
    "tab": win32con.VK_TAB,
    "backspace": win32con.VK_BACK,
    "delete": win32con.VK_DELETE,
    "del": win32con.VK_DELETE,
    "space": win32con.VK_SPACE,
    "up": win32con.VK_UP,
    "down": win32con.VK_DOWN,
    "left": win32con.VK_LEFT,
    "right": win32con.VK_RIGHT,
    "home": win32con.VK_HOME,
    "end": win32con.VK_END,
    "pageup": win32con.VK_PRIOR,
    "pagedown": win32con.VK_NEXT,
}
for i in range(1, 13):
    VK_MAP[f"f{i}"] = getattr(win32con, f"VK_F{i}")


def _resolve_vk(key: str) -> int:
    k = key.lower().strip()
    if k in VK_MAP:
        return VK_MAP[k]
    if len(k) == 1:
        return ord(k.upper())
    raise ValueError(f"Unrecognized key: {key}")


def _send_unicode_string(text: str):
    """Types any Unicode string directly without layout ambiguity."""
    for char in text:
        code = ord(char)
        inp_down = INPUT(type=INPUT_KEYBOARD, u=INPUT_UNION(ki=KEYBDINPUT(0, code, KEYEVENTF_UNICODE, 0, None)))
        inp_up = INPUT(type=INPUT_KEYBOARD, u=INPUT_UNION(ki=KEYBDINPUT(0, code, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, 0, None)))
        arr = (INPUT * 2)(inp_down, inp_up)
        user32.SendInput(2, ctypes.byref(arr), ctypes.sizeof(INPUT))
        time.sleep(0.002)


class KeyboardControlTool(BaseTool):
    BLOCKED_HOTKEYS = {
        "ctrl+alt+del",
        "ctrl+alt+delete",
    }
    MAX_TEXT_LEN = 5000

    @property
    def name(self) -> str:
        return "keyboard_control"
        
    @property
    def description(self) -> str:
        return "Simulates keyboard input: typing text, pressing individual keys, or executing hotkey shortcuts."
        
    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["type", "press", "hotkey"],
                    "description": "Action to perform: 'type' (Unicode string), 'press' (single key), or 'hotkey' (key combination)."
                },
                "text": {
                    "type": "string",
                    "description": "Text to type when action is 'type'."
                },
                "keys": {
                    "type": "string",
                    "description": "Key name or hotkey combo (e.g., 'enter', 'tab', 'ctrl+c', 'alt+tab')."
                }
            },
            "required": []
        }
        
    async def execute(self, action: str = "type", text: Optional[str] = None, keys: Optional[str] = None, **kwargs) -> Any:
        ensure_desktop_access()

        # Infer action if omitted
        if keys and not text and action == "type":
            action = "hotkey" if "+" in keys else "press"
        elif text and not keys:
            action = "type"

        if action == "type":
            if not text:
                return ToolResult.fail("Missing 'text' parameter for type action.")
            if len(text) > self.MAX_TEXT_LEN:
                return ToolResult.fail(f"Text length exceeds maximum allowed safety limit ({self.MAX_TEXT_LEN} chars).")
            
            try:
                _send_unicode_string(text)
                return ToolResult.ok(data={"action": "type", "chars_typed": len(text)})
            except Exception as e:
                return ToolResult.fail(f"Failed to type text: {e}")

        elif action == "press":
            target_key = keys or text
            if not target_key:
                return ToolResult.fail("Missing 'keys' parameter for press action.")
            try:
                vk = _resolve_vk(target_key)
                win32api.keybd_event(vk, 0, 0, 0)
                time.sleep(0.01)
                win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
                return ToolResult.ok(data={"action": "press", "key": target_key})
            except Exception as e:
                return ToolResult.fail(f"Failed to press key '{target_key}': {e}")

        elif action == "hotkey":
            if not keys:
                return ToolResult.fail("Missing 'keys' parameter for hotkey action.")
            normalized_combo = "+".join(k.strip().lower() for k in keys.split("+"))
            if normalized_combo in self.BLOCKED_HOTKEYS:
                return ToolResult.fail(f"Security blocked: '{keys}' is restricted by system safety policy.")
            
            key_tokens = [k.strip() for k in keys.split("+")]
            try:
                vks = [_resolve_vk(k) for k in key_tokens]
                # Press down in order
                for vk in vks:
                    win32api.keybd_event(vk, 0, 0, 0)
                    time.sleep(0.005)
                # Release in reverse order
                for vk in reversed(vks):
                    win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
                    time.sleep(0.005)
                return ToolResult.ok(data={"action": "hotkey", "combo": keys})
            except Exception as e:
                return ToolResult.fail(f"Failed to execute hotkey '{keys}': {e}")

        return ToolResult.fail(f"Unsupported keyboard action: {action}")


class MouseControlTool(BaseTool):
    @property
    def name(self) -> str:
        return "mouse_control"
        
    @property
    def description(self) -> str:
        return "Simulates mouse actions (move, click, double_click, right_click, drag, scroll, get_position) with safety bounds clamping."
        
    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["move", "click", "double_click", "right_click", "middle_click", "drag", "scroll", "get_position"],
                    "description": "Mouse action to execute."
                },
                "x": {"type": "integer", "description": "Target X coordinate on screen."},
                "y": {"type": "integer", "description": "Target Y coordinate on screen."},
                "dx": {"type": "integer", "description": "Relative X offset for drag or move."},
                "dy": {"type": "integer", "description": "Relative Y offset for drag or move."},
                "clicks": {"type": "integer", "description": "Number of clicks (default 1, max 10)."},
                "button": {"type": "string", "enum": ["left", "right", "middle"], "description": "Mouse button for click."},
                "scroll_amount": {"type": "integer", "description": "Wheel scroll amount (positive = up, negative = down)."}
            },
            "required": []
        }
        
    async def execute(
        self,
        action: str = "click",
        x: Optional[int] = None,
        y: Optional[int] = None,
        dx: Optional[int] = None,
        dy: Optional[int] = None,
        clicks: int = 1,
        button: str = "left",
        scroll_amount: Optional[int] = None,
        **kwargs
    ) -> Any:
        ensure_desktop_access()

        if action == "get_position":
            cur_x, cur_y = safe_get_cursor_pos()
            return ToolResult.ok(data={"action": "get_position", "x": cur_x, "y": cur_y})

        # Determine target coordinates
        cur_x, cur_y = safe_get_cursor_pos()
        target_x = x if x is not None else cur_x
        target_y = y if y is not None else cur_y

        if dx is not None:
            target_x += dx
        if dy is not None:
            target_y += dy

        target_x, target_y = clamp_coordinates(target_x, target_y)

        try:
            if action == "move":
                if not safe_set_cursor_pos(target_x, target_y):
                    return ToolResult.fail("Could not set cursor position (desktop input busy).")
                return ToolResult.ok(data={"action": "move", "x": target_x, "y": target_y})

            elif action in ("click", "double_click", "right_click", "middle_click"):
                # Move first if coordinates provided
                if x is not None or y is not None:
                    safe_set_cursor_pos(target_x, target_y)
                    time.sleep(0.01)

                effective_clicks = min(max(1, clicks), 10)
                if action == "double_click":
                    effective_clicks = 2
                    button = "left"
                elif action == "right_click":
                    button = "right"
                elif action == "middle_click":
                    button = "middle"

                down_flag = win32con.MOUSEEVENTF_LEFTDOWN
                up_flag = win32con.MOUSEEVENTF_LEFTUP
                if button == "right":
                    down_flag = win32con.MOUSEEVENTF_RIGHTDOWN
                    up_flag = win32con.MOUSEEVENTF_RIGHTUP
                elif button == "middle":
                    down_flag = win32con.MOUSEEVENTF_MIDDLEDOWN
                    up_flag = win32con.MOUSEEVENTF_MIDDLEUP

                for _ in range(effective_clicks):
                    win32api.mouse_event(down_flag, target_x, target_y, 0, 0)
                    time.sleep(0.01)
                    win32api.mouse_event(up_flag, target_x, target_y, 0, 0)
                    time.sleep(0.02)

                return ToolResult.ok(data={"action": action, "x": target_x, "y": target_y, "button": button, "clicks": effective_clicks})

            elif action == "scroll":
                amount = scroll_amount if scroll_amount is not None else 1
                wheel_delta = amount * 120
                win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, target_x, target_y, wheel_delta, 0)
                return ToolResult.ok(data={"action": "scroll", "x": target_x, "y": target_y, "scroll_amount": amount})

            elif action == "drag":
                if dx is None and dy is None and (x is None or y is None):
                    return ToolResult.fail("Drag requires start coordinates and destination (dx/dy or x/y).")
                
                safe_set_cursor_pos(cur_x, cur_y)
                time.sleep(0.01)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, cur_x, cur_y, 0, 0)
                time.sleep(0.02)
                safe_set_cursor_pos(target_x, target_y)
                time.sleep(0.02)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, target_x, target_y, 0, 0)
                return ToolResult.ok(data={"action": "drag", "from": {"x": cur_x, "y": cur_y}, "to": {"x": target_x, "y": target_y}})

            return ToolResult.fail(f"Unsupported mouse action: {action}")
        except Exception as e:
            return ToolResult.fail(f"Mouse action '{action}' failed: {e}")


class ClipboardControlTool(BaseTool):
    MAX_CLIPBOARD_LEN = 10_000_000

    @property
    def name(self) -> str:
        return "clipboard_control"
        
    @property
    def description(self) -> str:
        return "Reads from, writes to, or clears the system clipboard safely."
        
    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["read", "write", "clear"],
                    "description": "Action to perform: 'read' (default if text omitted), 'write' (copies text), or 'clear'."
                },
                "text": {
                    "type": "string",
                    "description": "Text content to write to clipboard when action is 'write'."
                }
            },
            "required": []
        }

    def _open_clipboard_with_retry(self, retries: int = 4, delay: float = 0.05):
        for attempt in range(retries):
            try:
                win32clipboard.OpenClipboard()
                return True
            except Exception:
                time.sleep(delay)
        raise RuntimeError("Unable to open Windows system clipboard (locked by another application).")

    async def execute(self, action: Optional[str] = None, text: Optional[str] = None, **kwargs) -> Any:
        ensure_desktop_access()

        if action is None:
            action = "write" if text is not None else "read"

        if action == "read":
            try:
                self._open_clipboard_with_retry()
                try:
                    clip_text = ""
                    if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                        clip_text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT) or ""
                    return ToolResult.ok(data={"action": "read", "text": clip_text, "length": len(clip_text)})
                finally:
                    win32clipboard.CloseClipboard()
            except Exception as e:
                return ToolResult.fail(f"Failed to read clipboard: {e}")

        elif action == "write":
            write_content = text or ""
            if len(write_content) > self.MAX_CLIPBOARD_LEN:
                return ToolResult.fail(f"Clipboard payload exceeds safety limit ({self.MAX_CLIPBOARD_LEN} characters).")
            try:
                self._open_clipboard_with_retry()
                try:
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardText(write_content, win32con.CF_UNICODETEXT)
                    return ToolResult.ok(data={"action": "write", "length": len(write_content)})
                finally:
                    win32clipboard.CloseClipboard()
            except Exception as e:
                return ToolResult.fail(f"Failed to write to clipboard: {e}")

        elif action == "clear":
            try:
                self._open_clipboard_with_retry()
                try:
                    win32clipboard.EmptyClipboard()
                    return ToolResult.ok(data={"action": "clear", "message": "Clipboard cleared successfully."})
                finally:
                    win32clipboard.CloseClipboard()
            except Exception as e:
                return ToolResult.fail(f"Failed to clear clipboard: {e}")

        return ToolResult.fail(f"Unsupported clipboard action: {action}")


# Register tools
registry.register(KeyboardControlTool())
registry.register(MouseControlTool())
registry.register(ClipboardControlTool())
