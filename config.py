"""
Central configuration, loaded from environment variables.
Copy backend/.env.example to backend/.env and fill in real values.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # --- Your 0x account ---
    ZEROX_API_KEY: str = os.getenv("ZEROX_API_KEY", "")
    ZEROX_BASE_URL: str = os.getenv("ZEROX_BASE_URL", "https://api.0x.org")

    # --- Your fee wallet ---
    # This is the address that receives the 15 bps (0.15%) fee on every
    # trade routed through the gateway. It must be a wallet you control.
    FEE_RECIPIENT_ADDRESS: str = os.getenv("FEE_RECIPIENT_ADDRESS", "")

    # Fee in basis points. 15 bps = 0.15%. 1 bps = 0.01%.
    FEE_BPS: int = int(os.getenv("FEE_BPS", "15"))

    # --- Auth ---
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-to-a-long-random-string")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
    SIWE_DOMAIN: str = os.getenv("SIWE_DOMAIN", "localhost")

    # --- Database ---
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./gateway.db")

    # --- CORS ---
    ALLOWED_ORIGINS: list[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

    # --- Rate limiting (very simple, per API key) ---
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))


settings = Settings()
