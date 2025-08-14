from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..deps import get_current_user
from ..models import User, AccessGrant, AccessGrantScope, UserRole
from ..schemas import AccessGrantCreate, AccessGrantOut
from ..audit import log_action


router = APIRouter(prefix="/grants", tags=["grants"])


def _serialize(grant: AccessGrant) -> AccessGrantOut:
	return AccessGrantOut(
		id=grant.id,
		granted_by_user_id=grant.granted_by_user_id,
		granted_to_user_id=grant.granted_to_user_id,
		scopes=[AccessGrantScope(s) for s in (grant.scopes_csv or "").split(",") if s],
		expires_at=grant.expires_at,
		created_at=grant.created_at,
	)


@router.post("/", response_model=AccessGrantOut)
def create_grant(
	payload: AccessGrantCreate,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	if current_user.role != UserRole.patient:
		raise HTTPException(status_code=403, detail="Only patients can create grants")

	if payload.provider_user_id is None and payload.provider_email is None:
		raise HTTPException(status_code=400, detail="provider_user_id or provider_email required")

	provider: Optional[User]
	if payload.provider_user_id is not None:
		provider = db.query(User).filter(User.id == payload.provider_user_id, User.role == UserRole.provider).first()
	else:
		provider = db.query(User).filter(User.email == payload.provider_email, User.role == UserRole.provider).first()
	if not provider:
		raise HTTPException(status_code=404, detail="Provider not found")

	scopes_csv = ",".join([s.value for s in payload.scopes])
	grant = AccessGrant(
		granted_by_user_id=current_user.id,
		granted_to_user_id=provider.id,
		scopes_csv=scopes_csv,
		expires_at=payload.expires_at,
	)
	db.add(grant)
	db.commit()
	db.refresh(grant)
	log_action(db, current_user.id, "create_grant", target_type="AccessGrant", target_id=grant.id)
	return _serialize(grant)


@router.get("/mine", response_model=List[AccessGrantOut])
def my_grants(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	if current_user.role != UserRole.patient:
		raise HTTPException(status_code=403, detail="Only patients have grants")
	rows = (
		db.query(AccessGrant)
		.filter(AccessGrant.granted_by_user_id == current_user.id)
		.order_by(AccessGrant.created_at.desc())
		.all()
	)
	return [_serialize(g) for g in rows]


@router.delete("/{grant_id}")
def revoke_grant(grant_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	grant = db.query(AccessGrant).filter(AccessGrant.id == grant_id).first()
	if not grant:
		raise HTTPException(status_code=404, detail="Grant not found")
	if current_user.role != UserRole.patient or grant.granted_by_user_id != current_user.id:
		raise HTTPException(status_code=403, detail="Not allowed")
	db.delete(grant)
	db.commit()
	log_action(db, current_user.id, "revoke_grant", target_type="AccessGrant", target_id=grant_id)
	return {"status": "revoked"}