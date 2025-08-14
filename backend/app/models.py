from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text, JSON, UniqueConstraint, func
from sqlalchemy.orm import relationship
import enum
from .database import Base


class UserRole(str, enum.Enum):
	patient = "patient"
	provider = "provider"
	admin = "admin"


class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	email = Column(String(255), unique=True, nullable=False, index=True)
	full_name = Column(String(255), nullable=False)
	password_hash = Column(String(255), nullable=False)
	role = Column(Enum(UserRole), nullable=False, index=True)
	created_at = Column(DateTime(timezone=True), server_default=func.now())

	patient_profile = relationship("PatientProfile", back_populates="user", uselist=False)
	provider_profile = relationship("ProviderProfile", back_populates="user", uselist=False)


class PatientProfile(Base):
	__tablename__ = "patient_profiles"

	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
	date_of_birth = Column(String(32), nullable=True)
	gender = Column(String(32), nullable=True)
	address = Column(String(512), nullable=True)

	user = relationship("User", back_populates="patient_profile")


class ProviderProfile(Base):
	__tablename__ = "provider_profiles"

	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
	organization = Column(String(255), nullable=True)
	license_number = Column(String(128), nullable=True)

	user = relationship("User", back_populates="provider_profile")


class MedicalRecord(Base):
	__tablename__ = "medical_records"

	id = Column(Integer, primary_key=True)
	patient_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
	title = Column(String(255), nullable=False)
	content_encrypted = Column(Text, nullable=False)
	created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	created_at = Column(DateTime(timezone=True), server_default=func.now())


class TestResult(Base):
	__tablename__ = "test_results"

	id = Column(Integer, primary_key=True)
	patient_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
	name = Column(String(255), nullable=False)
	result_encrypted = Column(Text, nullable=False)
	created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	created_at = Column(DateTime(timezone=True), server_default=func.now())


class Prescription(Base):
	__tablename__ = "prescriptions"

	id = Column(Integer, primary_key=True)
	patient_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
	medication_name = Column(String(255), nullable=False)
	dosage = Column(String(255), nullable=True)
	instructions_encrypted = Column(Text, nullable=False)
	prescribed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	created_at = Column(DateTime(timezone=True), server_default=func.now())


class AccessGrantScope(str, enum.Enum):
	records_read = "records_read"
	records_write = "records_write"
	tests_read = "tests_read"
	tests_write = "tests_write"
	prescriptions_read = "prescriptions_read"
	prescriptions_write = "prescriptions_write"
	all = "all"


class AccessGrant(Base):
	__tablename__ = "access_grants"

	id = Column(Integer, primary_key=True)
	granted_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	granted_to_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
	scopes_csv = Column(String(512), nullable=False)
	expires_at = Column(DateTime(timezone=True), nullable=True)
	created_at = Column(DateTime(timezone=True), server_default=func.now())

	__table_args__ = (
		UniqueConstraint("granted_by_user_id", "granted_to_user_id", name="uq_grant_pair"),
	)


class AuditLog(Base):
	__tablename__ = "audit_logs"

	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
	action = Column(String(255), nullable=False)
	target_type = Column(String(64), nullable=True)
	target_id = Column(Integer, nullable=True)
	metadata_json = Column(JSON, nullable=True)
	timestamp = Column(DateTime(timezone=True), server_default=func.now())