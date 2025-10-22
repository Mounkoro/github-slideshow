from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, Literal
from decimal import Decimal
from pydantic import field_serializer


class Token(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserOut(UserBase):
    id: int
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)


class AccountBase(BaseModel):
    type: Literal["standard", "savings"]
    annual_rate_percent: Optional[Decimal] = None
    term_months: Optional[int] = None

    @field_serializer("annual_rate_percent")
    def ser_rate(self, v: Optional[Decimal]):  # type: ignore[override]
        return float(v) if v is not None else None


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    annual_rate_percent: Optional[Decimal] = None
    term_months: Optional[int] = None

    @field_serializer("annual_rate_percent")
    def ser_rate(self, v: Optional[Decimal]):  # type: ignore[override]
        return float(v) if v is not None else None


class AccountOut(AccountBase):
    id: int
    user_id: int
    balance: Decimal

    @field_serializer("balance")
    def ser_balance(self, v: Decimal):  # type: ignore[override]
        return float(v)

    model_config = ConfigDict(from_attributes=True)


class AmountRequest(BaseModel):
    amount: Decimal = Field(gt=0)

    @field_serializer("amount")
    def ser_amount(self, v: Decimal):  # type: ignore[override]
        return float(v)


class BoostRequest(BaseModel):
    boost_percent: Decimal = Field(gt=0)

    @field_serializer("boost_percent")
    def ser_boost(self, v: Decimal):  # type: ignore[override]
        return float(v)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class MeOut(UserOut):
    pass
