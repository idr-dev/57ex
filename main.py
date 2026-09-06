from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from . import auth, keys, proxy

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="57eX",
    description=(
        "Issues per-user API keys and proxies swap requests to the 0x API, "
        f"collecting a {settings.FEE_BPS} bps fee on every trade."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(keys.router)
app.include_router(proxy.router)


@app.get("/health")
def health():
    return {"status": "ok", "fee_bps": settings.FEE_BPS}
