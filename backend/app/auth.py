from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from .database import get_db
from .models import User, UserRole, PatientProfile, ProviderProfile
from .schemas import UserCreate, UserOut, LoginRequest, Token
from .security import hash_password, verify_password, create_access_token
from .config import settings
from .audit import log_action


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
	existing = db.query(User).filter(User.email == payload.email).first()
	if existing:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
	password_hash = hash_password(payload.password)
	user = User(
		email=payload.email,
		full_name=payload.full_name,
		password_hash=password_hash,
		role=payload.role,
	)
	db.add(user)
	db.flush()
	if payload.role == UserRole.patient:
		profile = PatientProfile(
			user_id=user.id,
			date_of_birth=payload.date_of_birth,
			gender=payload.gender,
			address=payload.address,
		)
		db.add(profile)
	elif payload.role == UserRole.provider:
		profile = ProviderProfile(
			user_id=user.id,
			organization=payload.organization,
			license_number=payload.license_number,
		)
		db.add(profile)
	db.commit()
	db.refresh(user)
	log_action(db, user_id=user.id, action="register", target_type="user", target_id=user.id)
	return user


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
	user: Optional[User] = db.query(User).filter(User.email == payload.email).first()
	if not user or not verify_password(payload.password, user.password_hash):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
	token = create_access_token(subject=str(user.id), role=user.role.value, expires_hours=settings.jwt_exp_hours)
	log_action(db, user_id=user.id, action="login")
	return Token(access_token=token, expires_in_hours=settings.jwt_exp_hours)