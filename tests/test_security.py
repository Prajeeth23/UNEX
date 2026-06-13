import pytest
from src.security.permissions import RiskLevel, ActionStatus
from src.security.risk_classifier import RiskClassifier
from src.security.approval_manager import ApprovalManager
from src.security.action_validator import ActionValidator, ApprovalRequiredException

def test_risk_classification():
    classifier = RiskClassifier()
    assert classifier.classify_tool("launch_application") == RiskLevel.LOW
    assert classifier.classify_tool("write_file") == RiskLevel.MEDIUM
    assert classifier.classify_tool("delete_file") == RiskLevel.HIGH
    assert classifier.classify_tool("shutdown_system") == RiskLevel.CRITICAL
    assert classifier.classify_tool("unknown_tool") == RiskLevel.HIGH  # Default safety fallback

def test_approval_manager_flows():
    manager = ApprovalManager()
    
    # Test MEDIUM Risk (1 confirmation)
    action = manager.request_approval("write_file", {"file": "test.txt"}, RiskLevel.MEDIUM)
    assert action.status == ActionStatus.PENDING
    status = manager.provide_confirmation(True)
    assert status == ActionStatus.APPROVED
    manager.clear_pending()
    
    # Test HIGH Risk (1 confirmation)
    action = manager.request_approval("delete_file", {"file": "important.pdf"}, RiskLevel.HIGH)
    status = manager.provide_confirmation(False)
    assert status == ActionStatus.DENIED
    manager.clear_pending()
    
    # Test CRITICAL Risk (2 confirmations)
    action = manager.request_approval("shutdown_system", {}, RiskLevel.CRITICAL)
    status = manager.provide_confirmation(True)
    assert status == ActionStatus.PENDING # Still needs 1 more
    status = manager.provide_confirmation(True)
    assert status == ActionStatus.APPROVED

def test_action_validator_low_risk():
    validator = ActionValidator()
    # LOW risk should return True instantly without approval
    result = validator.validate_action("get_system_info", {})
    assert result is True

def test_action_validator_requires_approval():
    validator = ActionValidator()
    
    with pytest.raises(ApprovalRequiredException) as excinfo:
        validator.validate_action("write_file", {"content": "test"})
        
    assert excinfo.value.risk_level == RiskLevel.MEDIUM
    
    # Provide confirmation
    validator.approval_manager.provide_confirmation(True)
    
    # Should now pass
    result = validator.validate_action("write_file", {"content": "test"})
    assert result is True
