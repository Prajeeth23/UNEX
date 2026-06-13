import os
import json
from src.config.defaults import Defaults
from src.config.profiles import RunProfile

class Settings:
    """Singleton Configuration Manager for UNEX."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
        
    def _load_config(self):
        self.profile = RunProfile(os.getenv("UNEX_PROFILE", "production"))
        self.llm_model = os.getenv("LLM_MODEL", Defaults.LLM_MODEL)
        self.vision_model = os.getenv("VISION_MODEL", Defaults.VISION_MODEL)
        self.ollama_host = os.getenv("OLLAMA_HOST", Defaults.OLLAMA_HOST)
        self.db_path = os.getenv("DB_PATH", Defaults.DB_PATH)
        self.knowledge_db_path = os.getenv("KNOWLEDGE_DB_PATH", Defaults.KNOWLEDGE_DB_PATH)
        self.visual_memory_path = os.getenv("VISUAL_MEMORY_PATH", Defaults.VISUAL_MEMORY_PATH)
        
        # Load from optional settings.json file if it exists
        self.settings_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "settings.json"))
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    data = json.load(f)
                    self.llm_model = data.get("llm_model", self.llm_model)
                    self.vision_model = data.get("vision_model", self.vision_model)
            except Exception as e:
                print(f"[Settings] Failed to load settings.json: {e}")
                
    def save(self):
        """Saves current mutable config to settings.json"""
        data = {
            "llm_model": self.llm_model,
            "vision_model": self.vision_model
        }
        with open(self.settings_file, "w") as f:
            json.dump(data, f, indent=4)
            
    def enable_safe_mode(self):
        print("[Settings] WARNING: Entering Safe Mode. AI models degraded.")
        self.profile = RunProfile.SAFE_MODE
        # In safe mode, we bypass heavy models to prevent crashes
        self.llm_model = None
        self.vision_model = None
        
settings = Settings()
