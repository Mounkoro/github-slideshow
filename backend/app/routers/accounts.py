from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Account, AccountType, User
from ..schemas import AccountCreate, AccountOut, AccountUpdate, AmountRequest, BoostRequest
from ..deps import get_current_user, get_current_admin

router = APIRouter(prefix="/accounts", tags=["accounts"])


def _ensure_owner_or_admin(account: Account, user: User) -> None:
    if not (user.is_admin or account.user_id == user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")


@router.post("/", response_model=AccountOut, status_code=201)
def create_account(payload: AccountCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    acc_type = AccountType(payload.type)
    if acc_type == AccountType.SAVINGS:
        if payload.annual_rate_percent is None or payload.term_months is None:
            raise HTTPException(status_code=400, detail="Savings requires rate and term")
    account = Account(
        user_id=current_user.id,
        type=acc_type,
        balance=Decimal("0.00"),
        annual_rate_percent=payload.annual_rate_percent,
        term_months=payload.term_months,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.get("/", response_model=List[AccountOut])
def list_my_accounts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
    return accounts


@router.get("/{account_id}", response_model=AccountOut)
def get_account(account_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    _ensure_owner_or_admin(account, current_user)
    return account


@router.patch("/{account_id}", response_model=AccountOut)
def update_account(account_id: int, payload: AccountUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    _ensure_owner_or_admin(account, current_user)
    if account.type == AccountType.SAVINGS:
        if payload.annual_rate_percent is not None:
            account.annual_rate_percent = payload.annual_rate_percent
        if payload.term_months is not None:
            account.term_months = payload.term_months
    else:
        # ignore savings-only fields for standard accounts
        pass
    db.commit()
    db.refresh(account)
    return account


@router.delete("/{account_id}", status_code=204)
def delete_account(account_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    _ensure_owner_or_admin(account, current_user)
    db.delete(account)
    db.commit()
    return


@router.post("/{account_id}/deposit", response_model=AccountOut)
def deposit(account_id: int, req: AmountRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    _ensure_owner_or_admin(account, current_user)
    account.balance = (account.balance or Decimal("0")) + req.amount
    db.commit()
    db.refresh(account)
    return account


@router.post("/{account_id}/withdraw", response_model=AccountOut)
def withdraw(account_id: int, req: AmountRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    _ensure_owner_or_admin(account, current_user)
    new_balance = (account.balance or Decimal("0")) - req.amount
    if new_balance < 0:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    account.balance = new_balance
    db.commit()
    db.refresh(account)
    return account


@router.post("/{account_id}/boost", response_model=AccountOut)
def boost_rate(account_id: int, req: BoostRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    _ensure_owner_or_admin(account, current_user)
    if account.type != AccountType.SAVINGS or account.annual_rate_percent is None:
        raise HTTPException(status_code=400, detail="Boost applies to savings accounts only")
    account.annual_rate_percent = account.annual_rate_percent + req.boost_percent
    db.commit()
    db.refresh(account)
    return account
