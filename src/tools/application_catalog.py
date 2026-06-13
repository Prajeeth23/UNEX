import os
import glob
import re

class ApplicationCatalog:
    """Builds a searchable catalog of installed applications."""
    def __init__(self):
        self.apps = {}
        self._build_catalog()
        
    def _build_catalog(self):
        """Scans common directories for executables and shortcuts."""
        # This is a simplified scanner for MVP.
        # A full production scanner would read Registry or all Program Files using concurrent threads.
        paths_to_scan = [
            os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs"),
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs")
        ]
        
        for base_path in paths_to_scan:
            if not os.path.exists(base_path):
                continue
                
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    if file.endswith(('.lnk', '.exe')):
                        name = os.path.splitext(file)[0].lower()
                        # Clean up name: remove common terms
                        clean_name = re.sub(r'[^a-z0-9\s]', '', name).strip()
                        abs_path = os.path.join(root, file)
                        
                        self.apps[clean_name] = abs_path
                        # Add basic word tokens as aliases
                        for word in clean_name.split():
                            if len(word) > 3 and word not in self.apps:
                                self.apps[word] = abs_path
                                
    def find_app(self, alias: str) -> str:
        """Finds the absolute path of an app given an alias."""
        alias_clean = re.sub(r'[^a-z0-9\s]', '', alias.lower()).strip()
        
        # Exact match
        if alias_clean in self.apps:
            return self.apps[alias_clean]
            
        # Partial match
        for app_name, app_path in self.apps.items():
            if alias_clean in app_name or app_name in alias_clean:
                return app_path
                
        return ""
