from pydantic import BaseModel
from typing import Optional


class NonceResponse(BaseModel):
    nonce: str
    message: str


class VerifyRequest(BaseModel):
    address: str
    message: str
    signature: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    wallet_address: str


class ApiKeyOut(BaseModel):
    id: str
    key: str
    label: str
    active: bool

    class Config:
        from_attributes = True


class ApiKeyCreate(BaseModel):
    label: Optional[str] = "default"


class UsageSummary(BaseModel):
    total_requests: int
    total_fees_by_token: dict
