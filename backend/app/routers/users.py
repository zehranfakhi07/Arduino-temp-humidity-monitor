from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_current_user
from ..database import get_db
from ..schemas import UserOut
from ..models import User


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	return current_user