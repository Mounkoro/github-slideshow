from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..db import get_db
from ..models import User, LoginAttempt
from ..schemas import UserCreate, LoginRequest, Token, MeOut
from ..security import get_password_hash, verify_password, create_access_token
from ..config import settings
from ..deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


def _record_attempt(db: Session, email: Optional[str], ip: str, success: bool) -> None:
    att = LoginAttempt(email=email, ip_address=ip, success=success)
    db.add(att)
    db.commit()


def _too_many_attempts(db: Session, email: Optional[str], ip: str) -> bool:
    window_start = datetime.utcnow() - timedelta(seconds=settings.brute_force_window_seconds)
    q = db.query(LoginAttempt).filter(LoginAttempt.attempted_at >= window_start)
    ip_count = q.filter(LoginAttempt.ip_address == ip, LoginAttempt.success == False).count()
    if ip_count >= settings.brute_force_max_attempts:
        return True
    if email:
        email_count = q.filter(LoginAttempt.email == email, LoginAttempt.success == False).count()
        if email_count >= settings.brute_force_max_attempts:
            return True
    return False


@router.post("/register", response_model=MeOut, status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(request: Request, creds: LoginRequest, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    if _too_many_attempts(db, creds.email, client_ip):
        raise HTTPException(status_code=429, detail="Too many attempts, try later")

    user: Optional[User] = db.query(User).filter(User.email == creds.email).first()
    if not user or not verify_password(creds.password, user.password_hash) or user.is_locked:
        _record_attempt(db, creds.email, client_ip, False)
        raise HTTPException(status_code=401, detail="Invalid credentials or account locked")

    _record_attempt(db, creds.email, client_ip, True)

    token, expires_in = create_access_token(subject=user.id, extra={"email": user.email, "is_admin": user.is_admin})
    return {"access_token": token, "token_type": "bearer", "expires_in": expires_in}


@router.get("/me", response_model=MeOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
