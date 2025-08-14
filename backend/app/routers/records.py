from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..deps import get_current_user, ensure_scope_for_patient
from ..models import User, MedicalRecord, AccessGrantScope, UserRole
from ..schemas import MedicalRecordCreate, MedicalRecordOut
from ..crypto import encrypt_string, decrypt_string
from ..audit import log_action


router = APIRouter(prefix="/records", tags=["records"])


@router.post("/", response_model=MedicalRecordOut)
def create_record(
	payload: MedicalRecordCreate,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	patient_id = payload.patient_user_id or current_user.id
	if current_user.role == UserRole.patient:
		patient_id = current_user.id
	elif current_user.role == UserRole.provider:
		ensure_scope_for_patient(current_user, patient_id, [AccessGrantScope.records_write], db)
	elif current_user.role != UserRole.admin:
		raise HTTPException(status_code=403, detail="Not allowed")

	record = MedicalRecord(
		patient_user_id=patient_id,
		title=payload.title,
		content_encrypted=encrypt_string(payload.content),
		created_by_user_id=current_user.id,
	)
	db.add(record)
	db.commit()
	db.refresh(record)
	log_action(db, current_user.id, "create_record", target_type="MedicalRecord", target_id=record.id)
	return MedicalRecordOut(
		id=record.id,
		patient_user_id=record.patient_user_id,
		title=record.title,
		content=decrypt_string(record.content_encrypted),
		created_by_user_id=record.created_by_user_id,
		created_at=record.created_at,
	)


@router.get("/", response_model=List[MedicalRecordOut])
def list_records(
	patient_user_id: Optional[int] = Query(None),
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	if current_user.role == UserRole.patient:
		patient_id = current_user.id
	elif current_user.role == UserRole.provider:
		patient_id = patient_user_id
		if not patient_id:
			raise HTTPException(status_code=400, detail="patient_user_id required for provider")
		ensure_scope_for_patient(current_user, patient_id, [AccessGrantScope.records_read], db)
	else:
		patient_id = patient_user_id or current_user.id

	rows = (
		db.query(MedicalRecord)
		.filter(MedicalRecord.patient_user_id == patient_id)
		.order_by(MedicalRecord.created_at.desc())
		.all()
	)
	return [
		MedicalRecordOut(
			id=r.id,
			patient_user_id=r.patient_user_id,
			title=r.title,
			content=decrypt_string(r.content_encrypted),
			created_by_user_id=r.created_by_user_id,
			created_at=r.created_at,
		)
		for r in rows
	]


@router.get("/{record_id}", response_model=MedicalRecordOut)
def get_record(
	record_id: int,
	patient_user_id: Optional[int] = None,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
	if not record:
		raise HTTPException(status_code=404, detail="Record not found")
	# Access check
	patient_id = record.patient_user_id
	if current_user.role == UserRole.patient and current_user.id != patient_id:
		raise HTTPException(status_code=403, detail="Not allowed")
	elif current_user.role == UserRole.provider:
		ensure_scope_for_patient(current_user, patient_id, [AccessGrantScope.records_read], db)

	return MedicalRecordOut(
		id=record.id,
		patient_user_id=record.patient_user_id,
		title=record.title,
		content=decrypt_string(record.content_encrypted),
		created_by_user_id=record.created_by_user_id,
		created_at=record.created_at,
	)