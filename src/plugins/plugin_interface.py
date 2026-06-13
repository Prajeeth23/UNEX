from typing import Any
from src.tools.base_tool import BaseTool

class BasePlugin(BaseTool):
    """
    Interface for third-party plugins.
    Plugins must inherit from this and define their execution logic.
    They are automatically mapped to RiskLevel.MEDIUM by the Security layer.
    """
    pass
