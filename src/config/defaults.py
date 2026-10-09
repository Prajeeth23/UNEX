import os

class Defaults:
    """Default hardcoded values for UNEX."""
    LLM_MODEL = "qwen2.5:3b"
    VISION_MODEL = "moondream"
    OLLAMA_HOST = "http://localhost:11434"
    WAKE_WORD = "UNEX"
    DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "unex.db"))
    KNOWLEDGE_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "knowledge_db"))
    VISUAL_MEMORY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "visual_memory"))
    LOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "unex.log"))
