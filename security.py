import secrets
import datetime as dt
import jwt
from .config import settings


def generate_api_key() -> str:
    # Prefixed so keys are easy to recognize in logs / dashboards, e.g. in
    # support tickets, without ever logging the whole secret elsewhere.
    return "57ex_live_" + secrets.token_urlsafe(32)


def generate_nonce() -> str:
    return secrets.token_hex(16)


def create_access_token(wallet_address: str) -> str:
    expire = dt.datetime.utcnow() + dt.timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": wallet_address, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> str:
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    return payload["sub"]
