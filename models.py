import uuid
import datetime as dt
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from .database import Base


def uid() -> str:
    return uuid.uuid4().hex


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=uid)
    wallet_address = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    api_keys = relationship("ApiKey", back_populates="owner")


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=uid)
    key = Column(String, unique=True, index=True, nullable=False)
    label = Column(String, default="default")
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    owner = relationship("User", back_populates="api_keys")
    usage = relationship("UsageLog", back_populates="api_key")


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(String, primary_key=True, default=uid)
    api_key_id = Column(String, ForeignKey("api_keys.id"), nullable=False)
    chain_id = Column(Integer, nullable=True)
    endpoint = Column(String, nullable=True)
    sell_token = Column(String, nullable=True)
    buy_token = Column(String, nullable=True)
    sell_amount = Column(String, nullable=True)
    fee_bps = Column(Integer, nullable=True)
    fee_token = Column(String, nullable=True)
    fee_amount = Column(String, nullable=True)
    status_code = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    api_key = relationship("ApiKey", back_populates="usage")


class Nonce(Base):
    """Short-lived nonces issued for SIWE (Sign-In with Ethereum) login."""
    __tablename__ = "nonces"

    id = Column(String, primary_key=True, default=uid)
    wallet_address = Column(String, index=True, nullable=False)
    nonce = Column(String, nullable=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    used = Column(Boolean, default=False)
