from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List

from .database import get_db
from .models import User, AccessGrant, AccessGrantScope, UserRole
from .security import decode_token


bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
	credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
	db: Session = Depends(get_db),
) -> User:
	if not credentials.scheme.lower() == "bearer":
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth scheme")
	try:
		payload = decode_token(credentials.credentials)
	except Exception:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
	user_id = int(payload.get("sub"))
	user: User | None = db.query(User).filter(User.id == user_id).first()
	if not user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
	return user


def ensure_scope_for_patient(
	current_user: User,
	patient_user_id: int,
	required_scopes: List[AccessGrantScope],
	db: Session,
) -> None:
	if current_user.role == UserRole.admin:
		return
	if current_user.role == UserRole.patient:
		if current_user.id != patient_user_id:
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed for another patient")
		return
	# Provider: check grants from patient to provider
	if current_user.role == UserRole.provider:
		grant: AccessGrant | None = (
			db.query(AccessGrant)
			.filter(
				AccessGrant.granted_by_user_id == patient_user_id,
				AccessGrant.granted_to_user_id == current_user.id,
			)
			.first()
		)
		if not grant:
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access grant")
		if grant.expires_at is not None and grant.expires_at < datetime.now(timezone.utc):
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Grant expired")
		scopes = set((grant.scopes_csv or "").split(","))
		if "all" in scopes:
			return
		for s in required_scopes:
			if s.value not in scopes:
				raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Missing scope: {s.value}")
		return
	raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized role")