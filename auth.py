"""
Wallet-based login (Sign-In with Ethereum style, EIP-4361 message format)
with no email/password. Flow:

1. Client asks for a nonce for their wallet address:      GET  /auth/nonce?address=0x...
2. Client has the wallet sign a plain-text message that embeds that nonce.
3. Client posts {address, message, signature} to:          POST /auth/verify
4. Server recovers the signer from the signature, checks it matches
   `address` and that the nonce is valid + unused, then issues a JWT.
"""
import datetime as dt
from eth_account import Account
from eth_account.messages import encode_defunct
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from .database import get_db
from .models import User, Nonce
from .schemas import NonceResponse, VerifyRequest, TokenResponse
from .security import generate_nonce, create_access_token, decode_access_token
from .config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

NONCE_TTL_MINUTES = 10


def build_siwe_message(address: str, nonce: str) -> str:
    issued_at = dt.datetime.utcnow().isoformat() + "Z"
    return (
        f"{settings.SIWE_DOMAIN} wants you to sign in with your Ethereum account:\n"
        f"{address}\n\n"
        f"Sign in to the 0x Trading Gateway to manage your API keys. "
        f"This request will not trigger a blockchain transaction or cost gas.\n\n"
        f"URI: https://{settings.SIWE_DOMAIN}\n"
        f"Version: 1\n"
        f"Nonce: {nonce}\n"
        f"Issued At: {issued_at}"
    )


@router.get("/nonce", response_model=NonceResponse)
def get_nonce(address: str, db: Session = Depends(get_db)):
    address = address.lower()
    nonce = generate_nonce()
    db.add(Nonce(wallet_address=address, nonce=nonce))
    db.commit()
    return NonceResponse(nonce=nonce, message=build_siwe_message(address, nonce))


@router.post("/verify", response_model=TokenResponse)
def verify(payload: VerifyRequest, db: Session = Depends(get_db)):
    address = payload.address.lower()

    try:
        nonce_value = payload.message.split("Nonce: ")[1].splitlines()[0].strip()
    except IndexError:
        raise HTTPException(400, "Message missing nonce")

    record = (
        db.query(Nonce)
        .filter(Nonce.wallet_address == address, Nonce.nonce == nonce_value, Nonce.used == False)  # noqa: E712
        .order_by(Nonce.created_at.desc())
        .first()
    )
    if not record:
        raise HTTPException(400, "Unknown or already-used nonce")

    if dt.datetime.utcnow() - record.created_at > dt.timedelta(minutes=NONCE_TTL_MINUTES):
        raise HTTPException(400, "Nonce expired, request a new one")

    # Recover the signer of the message and confirm it matches the claimed address.
    try:
        encoded = encode_defunct(text=payload.message)
        recovered = Account.recover_message(encoded, signature=payload.signature)
    except Exception:
        raise HTTPException(400, "Could not verify signature")

    if recovered.lower() != address:
        raise HTTPException(401, "Signature does not match address")

    record.used = True
    db.commit()

    user = db.query(User).filter(User.wallet_address == address).first()
    if not user:
        user = User(wallet_address=address)
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(address)
    return TokenResponse(access_token=token, wallet_address=address)


def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)) -> User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        address = decode_access_token(token)
    except Exception:
        raise HTTPException(401, "Invalid or expired token")
    user = db.query(User).filter(User.wallet_address == address).first()
    if not user:
        raise HTTPException(401, "User not found")
    return user
