"""
The core of the gateway: a thin, fee-injecting reverse proxy in front of the
0x Swap API. Users call *this* service with the API key issued to them.
We add our fee parameters and our own 0x API key, forward the call to 0x,
log it, and return 0x's response untouched.

Supports every chain 0x supports, since chain selection is just the
`chainId` query parameter 0x already accepts — we never hardcode a chain.
"""
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from fastapi.responses import Response
from sqlalchemy.orm import Session

from .database import get_db
from .models import ApiKey, UsageLog
from .config import settings

router = APIRouter(prefix="/v1", tags=["proxy"])

# Endpoints where a trade is actually priced/settled, and so where our fee
# parameters belong. Read-only metadata endpoints (e.g. `/swap/*/sources`)
# are passed straight through untouched.
FEE_ELIGIBLE_SUFFIXES = ("/quote", "/price")


def get_api_key(x_api_key: str = Header(..., alias="x-api-key"), db: Session = Depends(get_db)) -> ApiKey:
    key = db.query(ApiKey).filter(ApiKey.key == x_api_key, ApiKey.active == True).first()  # noqa: E712
    if not key:
        raise HTTPException(401, "Invalid or inactive API key")
    return key


@router.api_route("/{full_path:path}", methods=["GET", "POST"])
async def proxy_to_0x(
    full_path: str,
    request: Request,
    api_key: ApiKey = Depends(get_api_key),
    db: Session = Depends(get_db),
):
    if not settings.ZEROX_API_KEY or not settings.FEE_RECIPIENT_ADDRESS:
        raise HTTPException(
            500,
            "Gateway is not configured yet: set ZEROX_API_KEY and "
            "FEE_RECIPIENT_ADDRESS in backend/.env",
        )

    params = dict(request.query_params)
    is_fee_eligible = any(full_path.endswith(suffix) for suffix in FEE_ELIGIBLE_SUFFIXES)

    if is_fee_eligible:
        # Take our cut on top of whatever the user already asked for.
        # If the caller set their own swapFee* params we respect theirs only
        # when it configures the *same* recipient — otherwise we overwrite,
        # since this gateway's whole purpose is collecting this fee.
        params["swapFeeRecipient"] = settings.FEE_RECIPIENT_ADDRESS
        params["swapFeeBps"] = str(settings.FEE_BPS)
        params.setdefault("swapFeeToken", params.get("buyToken"))

    url = f"{settings.ZEROX_BASE_URL}/{full_path}"
    headers = {
        "0x-api-key": settings.ZEROX_API_KEY,
        "0x-version": "v2",
    }

    body = await request.body()

    async with httpx.AsyncClient(timeout=20) as client:
        upstream = await client.request(
            request.method,
            url,
            params=params,
            headers=headers,
            content=body or None,
        )

    log = UsageLog(
        api_key_id=api_key.id,
        chain_id=int(params["chainId"]) if params.get("chainId", "").isdigit() else None,
        endpoint=full_path,
        sell_token=params.get("sellToken"),
        buy_token=params.get("buyToken"),
        sell_amount=params.get("sellAmount"),
        fee_bps=settings.FEE_BPS if is_fee_eligible else None,
        fee_token=params.get("swapFeeToken") if is_fee_eligible else None,
        status_code=upstream.status_code,
    )

    # 0x's response echoes back the exact fee amount taken, when available;
    # store it so the dashboard can show real earnings rather than estimates.
    try:
        data = upstream.json()
        fee_amount = data.get("fees", {}).get("integratorFee", {}).get("amount")
        if fee_amount:
            log.fee_amount = str(fee_amount)
    except ValueError:
        pass

    db.add(log)
    db.commit()

    return Response(
        status_code=upstream.status_code,
        content=upstream.content,
        media_type=upstream.headers.get("content-type", "application/json"),
    )
