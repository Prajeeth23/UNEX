from enum import Enum

class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ActionStatus(Enum):
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    PENDING = "PENDING"
