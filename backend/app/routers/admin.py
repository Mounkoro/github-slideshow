from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User, LoginAttempt
from ..schemas import UserOut
from ..deps import get_current_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return db.query(User).all()


@router.post("/users/{user_id}/lock")
def lock_user(user_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_locked = True
    db.commit()
    return {"status": "locked"}


@router.post("/users/{user_id}/unlock")
def unlock_user(user_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_locked = False
    db.commit()
    return {"status": "unlocked"}


@router.get("/attempts")
def recent_attempts(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    attempts = db.query(LoginAttempt).order_by(LoginAttempt.attempted_at.desc()).limit(200).all()
    # naive serialization
    return [
        {
            "email": a.email,
            "ip": a.ip_address,
            "time": a.attempted_at.isoformat(),
            "success": a.success,
        }
        for a in attempts
    ]
