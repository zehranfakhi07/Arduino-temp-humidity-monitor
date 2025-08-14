from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from .models import UserRole, AccessGrantScope


class Token(BaseModel):
	access_token: str
	token_type: str = "bearer"
	expires_in_hours: int


class UserBase(BaseModel):
	email: EmailStr
	full_name: str
	role: UserRole


class UserCreate(BaseModel):
	email: EmailStr
	full_name: str
	password: str = Field(min_length=8)
	role: UserRole
	date_of_birth: Optional[str] = None
	gender: Optional[str] = None
	address: Optional[str] = None
	organization: Optional[str] = None
	license_number: Optional[str] = None


class UserOut(UserBase):
	id: int
	created_at: datetime

	class Config:
		from_attributes = True


class LoginRequest(BaseModel):
	email: EmailStr
	password: str


class MedicalRecordCreate(BaseModel):
	patient_user_id: Optional[int] = None
	title: str
	content: str


class MedicalRecordOut(BaseModel):
	id: int
	patient_user_id: int
	title: str
	content: str
	created_by_user_id: int
	created_at: datetime

	class Config:
		from_attributes = True


class TestResultCreate(BaseModel):
	patient_user_id: Optional[int] = None
	name: str
	result: str


class TestResultOut(BaseModel):
	id: int
	patient_user_id: int
	name: str
	result: str
	created_by_user_id: int
	created_at: datetime

	class Config:
		from_attributes = True


class PrescriptionCreate(BaseModel):
	patient_user_id: Optional[int] = None
	medication_name: str
	dosage: Optional[str] = None
	instructions: str


class PrescriptionOut(BaseModel):
	id: int
	patient_user_id: int
	medication_name: str
	dosage: Optional[str]
	instructions: str
	prescribed_by_user_id: int
	created_at: datetime

	class Config:
		from_attributes = True


class AccessGrantCreate(BaseModel):
	provider_email: Optional[EmailStr] = None
	provider_user_id: Optional[int] = None
	scopes: List[AccessGrantScope]
	expires_at: Optional[datetime] = None


class AccessGrantOut(BaseModel):
	id: int
	granted_by_user_id: int
	granted_to_user_id: int
	scopes: List[AccessGrantScope]
	expires_at: Optional[datetime]
	created_at: datetime

	class Config:
		from_attributes = True