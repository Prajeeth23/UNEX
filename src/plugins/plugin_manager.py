import os
import importlib.util
import inspect
from src.tools.tool_registry import registry
from src.plugins.plugin_interface import BasePlugin

class PluginManager:
    @staticmethod
    def load_plugins():
        plugin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "plugins"))
        os.makedirs(plugin_dir, exist_ok=True)
        
        count = 0
        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                filepath = os.path.join(plugin_dir, filename)
                
                module_name = f"unex.plugins.{filename[:-3]}"
                spec = importlib.util.spec_from_file_location(module_name, filepath)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    try:
                        spec.loader.exec_module(module)
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                            if issubclass(obj, BasePlugin) and obj is not BasePlugin:
                                registry.register(obj())
                                count += 1
                                print(f"[PluginManager] Loaded plugin tool: {obj().name}")
                    except Exception as e:
                        print(f"[PluginManager] Failed to load plugin {filename}: {e}")
                        
        print(f"[PluginManager] Total plugins loaded: {count}")
