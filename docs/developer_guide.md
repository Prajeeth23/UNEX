# UNEX Developer Guide

## Building Plugins
You can extend UNEX without modifying core code by placing a `.py` file in the `plugins/` directory.

### Example Plugin
```python
from src.plugins.plugin_interface import BasePlugin
from src.tools.tool_result import ToolResult

class MyCustomPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "my_custom_plugin"
        
    @property
    def description(self) -> str:
        return "A custom plugin for UNEX."
        
    @property
    def parameters_schema(self) -> dict:
        return {"type": "object", "properties": {}}
        
    async def execute(self, **kwargs):
        return ToolResult.ok(data={"msg": "Hello from plugin!"})
```
The `PluginManager` will automatically load it on startup and register it with the `UNEXAgent`.

## System Diagnostics
You can programmatically poll UNEX's health:
`GET http://localhost:8000/diagnostics`
This returns JSON describing RAM, Threads, DB status, and the current Ollama LLM provider.
