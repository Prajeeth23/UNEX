from src.security.permissions import RiskLevel, ActionStatus
from src.security.risk_classifier import RiskClassifier
from src.security.audit_logger import AuditLogger
from src.security.approval_manager import ApprovalManager

class ApprovalRequiredException(Exception):
    def __init__(self, message: str, tool_name: str, tool_args: dict, risk_level: RiskLevel):
        super().__init__(message)
        self.tool_name = tool_name
        self.tool_args = tool_args
        self.risk_level = risk_level

class ActionValidator:
    def __init__(self):
        self.classifier = RiskClassifier()
        self.logger = AuditLogger()
        self.approval_manager = ApprovalManager()
        
    def validate_action(self, tool_name: str, tool_args: dict, user_query: str = "") -> bool:
        """
        Validates the action. 
        Returns True if allowed immediately (LOW risk or already approved).
        Raises ApprovalRequiredException if user confirmation is needed.
        Raises PermissionError if explicitly denied or invalid.
        """
        risk_level = self.classifier.classify_tool(tool_name)
        
        # Check if this action is currently pending approval
        pending = self.approval_manager.pending_action
        if pending and pending.tool_name == tool_name and pending.tool_args == tool_args:
            if pending.status == ActionStatus.APPROVED:
                self.logger.log_action(tool_name, tool_args, risk_level, ActionStatus.APPROVED, user_query)
                self.approval_manager.clear_pending()
                return True
            elif pending.status == ActionStatus.DENIED:
                self.logger.log_action(tool_name, tool_args, risk_level, ActionStatus.DENIED, user_query, "User explicitly denied action.")
                self.approval_manager.clear_pending()
                raise PermissionError(f"User denied execution of {tool_name}.")
            else:
                # Still pending
                raise ApprovalRequiredException("Action is awaiting user confirmation.", tool_name, tool_args, risk_level)
                
        # Not pending. Evaluate fresh.
        if risk_level == RiskLevel.LOW:
            self.logger.log_action(tool_name, tool_args, risk_level, ActionStatus.APPROVED, user_query)
            return True
            
        # MEDIUM, HIGH, CRITICAL requires approval
        self.logger.log_action(tool_name, tool_args, risk_level, ActionStatus.PENDING, user_query, "Awaiting approval.")
        self.approval_manager.request_approval(tool_name, tool_args, risk_level)
        raise ApprovalRequiredException(f"Action requires approval due to {risk_level.value} risk.", tool_name, tool_args, risk_level)
        
    def log_failure(self, tool_name: str, tool_args: dict, error_msg: str, user_query: str = ""):
        risk_level = self.classifier.classify_tool(tool_name)
        self.logger.log_action(tool_name, tool_args, risk_level, ActionStatus.DENIED, user_query, error_msg)

validator = ActionValidator()
