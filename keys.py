from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from collections import defaultdict

from .database import get_db
from .models import User, ApiKey, UsageLog
from .schemas import ApiKeyOut, ApiKeyCreate, UsageSummary
from .security import generate_api_key
from .auth import get_current_user

router = APIRouter(prefix="/keys", tags=["api-keys"])


@router.get("", response_model=list[ApiKeyOut])
def list_keys(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(ApiKey).filter(ApiKey.user_id == user.id).all()


@router.post("", response_model=ApiKeyOut)
def create_key(body: ApiKeyCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    key = ApiKey(key=generate_api_key(), label=body.label or "default", user_id=user.id)
    db.add(key)
    db.commit()
    db.refresh(key)
    return key


@router.delete("/{key_id}")
def revoke_key(key_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    key = db.query(ApiKey).filter(ApiKey.id == key_id, ApiKey.user_id == user.id).first()
    if not key:
        raise HTTPException(404, "Key not found")
    key.active = False
    db.commit()
    return {"status": "revoked"}


@router.get("/{key_id}/usage", response_model=UsageSummary)
def key_usage(key_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    key = db.query(ApiKey).filter(ApiKey.id == key_id, ApiKey.user_id == user.id).first()
    if not key:
        raise HTTPException(404, "Key not found")

    logs = db.query(UsageLog).filter(UsageLog.api_key_id == key.id).all()
    fees_by_token = defaultdict(float)
    for log in logs:
        if log.fee_token and log.fee_amount:
            try:
                fees_by_token[log.fee_token] += float(log.fee_amount)
            except ValueError:
                continue

    return UsageSummary(total_requests=len(logs), total_fees_by_token=dict(fees_by_token))
