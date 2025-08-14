from typing import Any, Optional
from sqlalchemy.orm import Session
from .models import AuditLog


def log_action(
	db: Session,
	user_id: Optional[int],
	action: str,
	target_type: Optional[str] = None,
	target_id: Optional[int] = None,
	metadata_json: Optional[dict[str, Any]] = None,
) -> None:
	entry = AuditLog(
		user_id=user_id,
		action=action,
		target_type=target_type,
		target_id=target_id,
		metadata_json=metadata_json,
	)
	db.add(entry)
	db.commit()