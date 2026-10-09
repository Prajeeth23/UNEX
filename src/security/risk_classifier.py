from src.security.permissions import RiskLevel

class RiskClassifier:
    """Classifies tools and arbitrary actions into Risk Levels."""
    
    # Pre-defined mapping of tool names to risk levels.
    TOOL_RISK_MAP = {
        "get_system_info": RiskLevel.LOW,
        "list_directory": RiskLevel.LOW,
        "read_file": RiskLevel.LOW,
        "search_files": RiskLevel.LOW,
        "launch_application": RiskLevel.LOW,  # User explicitly requested app opening as LOW
        "check_running_processes": RiskLevel.LOW,
        "list_windows": RiskLevel.LOW,
        "get_active_window": RiskLevel.LOW,
        "focus_window": RiskLevel.LOW,
        "minimize_window": RiskLevel.LOW,
        "maximize_window": RiskLevel.LOW,
        "restore_window": RiskLevel.LOW,
        "set_window_state": RiskLevel.LOW,
        "clipboard_control": RiskLevel.LOW,
        "mouse_control": RiskLevel.MEDIUM,
        "keyboard_control": RiskLevel.MEDIUM,
        "analyze_screen": RiskLevel.LOW,
        "analyze_image_file": RiskLevel.LOW,
        "extract_screen_text": RiskLevel.LOW,
        "close_application": RiskLevel.MEDIUM,
        "write_file": RiskLevel.MEDIUM,
        "rename_file": RiskLevel.MEDIUM,
        "move_file": RiskLevel.MEDIUM,
        "create_folder": RiskLevel.MEDIUM,
        "delete_file": RiskLevel.HIGH,
        "kill_process": RiskLevel.HIGH,
        "shutdown_system": RiskLevel.CRITICAL,
        "restart_system": RiskLevel.CRITICAL,
    }

    @staticmethod
    def classify_tool(tool_name: str) -> RiskLevel:
        """Returns the risk level of a given tool. Defaults to HIGH if unknown for safety."""
        return RiskClassifier.TOOL_RISK_MAP.get(tool_name, RiskLevel.HIGH)
