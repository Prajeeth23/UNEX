from sqlalchemy.orm import Session
from src.memory.database import AuditLogDB, init_db
import json
from src.security.permissions import RiskLevel, ActionStatus
import threading

class AuditLogger:
    def __init__(self):
        # Using the same database connection as memory
        self.SessionLocal = init_db()
        self._lock = threading.Lock()

    def log_action(self, tool_name: str, tool_args: dict, risk_level: RiskLevel, status: ActionStatus, user_query: str = "", error_message: str = ""):
        with self._lock:
            try:
                db = self.SessionLocal()
                log_entry = AuditLogDB(
                    tool_name=tool_name,
                    tool_args=json.dumps(tool_args),
                    risk_level=risk_level.value,
                    status=status.value,
                    user_query=user_query,
                    error_message=error_message
                )
                db.add(log_entry)
                db.commit()
            except Exception as e:
                print(f"[AuditLogger] Error logging action: {e}")
            finally:
                db.close()
                
    def get_recent_logs(self, limit: int = 50):
        try:
            db = self.SessionLocal()
            logs = db.query(AuditLogDB).order_by(AuditLogDB.timestamp.desc()).limit(limit).all()
            result = []
            for log in logs:
                result.append({
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat(),
                    "tool_name": log.tool_name,
                    "tool_args": json.loads(log.tool_args) if log.tool_args else {},
                    "risk_level": log.risk_level,
                    "status": log.status,
                    "user_query": log.user_query,
                    "error_message": log.error_message
                })
            return result
        except Exception as e:
            print(f"[AuditLogger] Error fetching logs: {e}")
            return []
        finally:
            db.close()
