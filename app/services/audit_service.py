import json
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def log_action(
    db: Session,
    *,
    actor_id: int,
    action: str,
    target_id: Optional[int] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> AuditLog:
    entry = AuditLog(
        actor_user_id=actor_id,
        action=action,
        target_user_id=target_id,
        metadata_json=json.dumps(metadata) if metadata else None,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
