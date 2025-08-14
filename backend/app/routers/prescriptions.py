from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..deps import get_current_user, ensure_scope_for_patient
from ..models import User, Prescription, AccessGrantScope, UserRole
from ..schemas import PrescriptionCreate, PrescriptionOut
from ..crypto import encrypt_string, decrypt_string
from ..audit import log_action


router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])


@router.post("/", response_model=PrescriptionOut)
def create_prescription(
	payload: PrescriptionCreate,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	patient_id = payload.patient_user_id or current_user.id
	if current_user.role == UserRole.patient:
		patient_id = current_user.id
	elif current_user.role == UserRole.provider:
		ensure_scope_for_patient(current_user, patient_id, [AccessGrantScope.prescriptions_write], db)
	elif current_user.role != UserRole.admin:
		raise HTTPException(status_code=403, detail="Not allowed")

	row = Prescription(
		patient_user_id=patient_id,
		medication_name=payload.medication_name,
		dosage=payload.dosage,
		instructions_encrypted=encrypt_string(payload.instructions),
		prescribed_by_user_id=current_user.id,
	)
	db.add(row)
	db.commit()
	db.refresh(row)
	log_action(db, current_user.id, "create_prescription", target_type="Prescription", target_id=row.id)
	return PrescriptionOut(
		id=row.id,
		patient_user_id=row.patient_user_id,
		medication_name=row.medication_name,
		dosage=row.dosage,
		instructions=decrypt_string(row.instructions_encrypted),
		prescribed_by_user_id=row.prescribed_by_user_id,
		created_at=row.created_at,
	)


@router.get("/", response_model=List[PrescriptionOut])
def list_prescriptions(
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
		ensure_scope_for_patient(current_user, patient_id, [AccessGrantScope.prescriptions_read], db)
	else:
		patient_id = patient_user_id or current_user.id

	rows = (
		db.query(Prescription)
		.filter(Prescription.patient_user_id == patient_id)
		.order_by(Prescription.created_at.desc())
		.all()
	)
	return [
		PrescriptionOut(
			id=r.id,
			patient_user_id=r.patient_user_id,
			medication_name=r.medication_name,
			dosage=r.dosage,
			instructions=decrypt_string(r.instructions_encrypted),
			prescribed_by_user_id=r.prescribed_by_user_id,
			created_at=r.created_at,
		)
		for r in rows
	]


@router.get("/{prescription_id}", response_model=PrescriptionOut)
def get_prescription(
	prescription_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	row = db.query(Prescription).filter(Prescription.id == prescription_id).first()
	if not row:
		raise HTTPException(status_code=404, detail="Prescription not found")
	patient_id = row.patient_user_id
	if current_user.role == UserRole.patient and current_user.id != patient_id:
		raise HTTPException(status_code=403, detail="Not allowed")
	elif current_user.role == UserRole.provider:
		ensure_scope_for_patient(current_user, patient_id, [AccessGrantScope.prescriptions_read], db)

	return PrescriptionOut(
		id=row.id,
		patient_user_id=row.patient_user_id,
		medication_name=row.medication_name,
		dosage=row.dosage,
		instructions=decrypt_string(row.instructions_encrypted),
		prescribed_by_user_id=row.prescribed_by_user_id,
		created_at=row.created_at,
	)