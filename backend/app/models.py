from sqlalchemy import Column, Integer, String, Boolean, Enum, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .db import Base

class AccountType(str, enum.Enum):
    STANDARD = "standard"
    SAVINGS = "savings"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    accounts = relationship("Account", back_populates="owner")

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(Enum(AccountType), nullable=False)
    balance = Column(Numeric(12, 2), nullable=False, default=0)
    annual_rate_percent = Column(Numeric(5, 2), nullable=True)  # only for savings
    term_months = Column(Integer, nullable=True)  # only for savings
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="accounts")


class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), index=True, nullable=True)
    ip_address = Column(String(64), index=True, nullable=False)
    attempted_at = Column(DateTime, default=datetime.utcnow, index=True)
    success = Column(Boolean, default=False)

Index("ix_login_attempts_email_time", LoginAttempt.email, LoginAttempt.attempted_at)
Index("ix_login_attempts_ip_time", LoginAttempt.ip_address, LoginAttempt.attempted_at)
