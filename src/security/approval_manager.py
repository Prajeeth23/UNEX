import asyncio
from typing import Dict, Any, Optional
from src.security.permissions import RiskLevel, ActionStatus

class PendingAction:
    def __init__(self, tool_name: str, tool_args: dict, risk_level: RiskLevel):
        self.tool_name = tool_name
        self.tool_args = tool_args
        self.risk_level = risk_level
        self.status = ActionStatus.PENDING
        self.confirmations_received = 0
        self.required_confirmations = self._get_required_confirmations(risk_level)
        
    def _get_required_confirmations(self, risk: RiskLevel) -> int:
        if risk == RiskLevel.MEDIUM: return 1
        if risk == RiskLevel.HIGH: return 1
        if risk == RiskLevel.CRITICAL: return 2
        return 0

class ApprovalManager:
    def __init__(self):
        self.pending_action: Optional[PendingAction] = None
        
    def request_approval(self, tool_name: str, tool_args: dict, risk_level: RiskLevel) -> PendingAction:
        """Queues an action for approval."""
        self.pending_action = PendingAction(tool_name, tool_args, risk_level)
        return self.pending_action
        
    def provide_confirmation(self, is_approved: bool) -> ActionStatus:
        """Process a user's yes/no response."""
        if not self.pending_action:
            return ActionStatus.DENIED
            
        if not is_approved:
            self.pending_action.status = ActionStatus.DENIED
            action = self.pending_action
            self.pending_action = None
            return action.status
            
        self.pending_action.confirmations_received += 1
        
        if self.pending_action.confirmations_received >= self.pending_action.required_confirmations:
            self.pending_action.status = ActionStatus.APPROVED
            
        return self.pending_action.status

    def clear_pending(self):
        self.pending_action = None
