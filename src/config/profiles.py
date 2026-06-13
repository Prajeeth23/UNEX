from enum import Enum

class RunProfile(Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    SAFE_MODE = "safe_mode"
