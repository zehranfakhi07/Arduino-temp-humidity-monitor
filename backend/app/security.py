from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from .config import settings


password_hasher = PasswordHasher()


def hash_password(plain_password: str) -> str:
	return password_hasher.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
	try:
		password_hasher.verify(password_hash, plain_password)
		return True
	except VerifyMismatchError:
		return False


def create_access_token(subject: str, role: str, expires_hours: Optional[int] = None) -> str:
	expires_in = expires_hours or settings.jwt_exp_hours
	exp = datetime.now(tz=timezone.utc) + timedelta(hours=expires_in)
	payload: Dict[str, Any] = {
		"sub": subject,
		"role": role,
		"exp": int(exp.timestamp()),
	}
	return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Dict[str, Any]:
	return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])