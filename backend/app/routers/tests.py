from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..deps import get_current_user, ensure_scope_for_patient
from ..models import User, TestResult, AccessGrantScope, UserRole
from ..schemas import TestResultCreate, TestResultOut
from ..crypto import encrypt_string, decrypt_string
from ..audit import log_action


router = APIRouter(prefix="/tests", tags=["tests"])


@router.post("/", response_model=TestResultOut)
def create_test_result(
	payload: TestResultCreate,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	patient_id = payload.patient_user_id or current_user.id
	if current_user.role == UserRole.patient:
		patient_id = current_user.id
	elif current_user.role == UserRole.provider:
		ensure_scope_for_patient(current_user, patient_id, [AccessGrantScope.tests_write], db)
	elif current_user.role != UserRole.admin:
		raise HTTPException(status_code=403, detail="Not allowed")

	row = TestResult(
		patient_user_id=patient_id,
		name=payload.name,
		result_encrypted=encrypt_string(payload.result),
		created_by_user_id=current_user.id,
	)
	db.add(row)
	db.commit()
	db.refresh(row)
	log_action(db, current_user.id, "create_test_result", target_type="TestResult", target_id=row.id)
	return TestResultOut(
		id=row.id,
		patient_user_id=row.patient_user_id,
		name=row.name,
		result=decrypt_string(row.result_encrypted),
		created_by_user_id=row.created_by_user_id,
		created_at=row.created_at,
	)


@router.get("/", response_model=List[TestResultOut])
def list_test_results(
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
		ensure_scope_for_patient(current_user, patient_id, [AccessGrantScope.tests_read], db)
	else:
		patient_id = patient_user_id or current_user.id

	rows = (
		db.query(TestResult)
		.filter(TestResult.patient_user_id == patient_id)
		.order_by(TestResult.created_at.desc())
		.all()
	)
	return [
		TestResultOut(
			id=r.id,
			patient_user_id=r.patient_user_id,
			name=r.name,
			result=decrypt_string(r.result_encrypted),
			created_by_user_id=r.created_by_user_id,
			created_at=r.created_at,
		)
		for r in rows
	]


@router.get("/{test_id}", response_model=TestResultOut)
def get_test_result(
	test_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	row = db.query(TestResult).filter(TestResult.id == test_id).first()
	if not row:
		raise HTTPException(status_code=404, detail="Test result not found")
	patient_id = row.patient_user_id
	if current_user.role == UserRole.patient and current_user.id != patient_id:
		raise HTTPException(status_code=403, detail="Not allowed")
	elif current_user.role == UserRole.provider:
		ensure_scope_for_patient(current_user, patient_id, [AccessGrantScope.tests_read], db)

	return TestResultOut(
		id=row.id,
		patient_user_id=row.patient_user_id,
		name=row.name,
		result=decrypt_string(row.result_encrypted),
		created_by_user_id=row.created_by_user_id,
		created_at=row.created_at,
	)