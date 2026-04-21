from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import httpx

router = APIRouter()

CBU_URL = "https://cbu.uz/oz/arkhiv-kursov-valyut/json/"
CACHE_TTL_SECONDS = 60 * 60  # 1 hour
CODES = ("USD", "EUR", "RUB")


class CurrencyRate(BaseModel):
    code: str
    rate: float
    diff: float
    date: str


class CurrencyRates(BaseModel):
    rates: List[CurrencyRate]
    fetched_at: str


_cache: dict = {"payload": None, "at": 0.0}


def _now_ts() -> float:
    return datetime.now(timezone.utc).timestamp()


def _parse_rate(item: dict) -> Optional[CurrencyRate]:
    try:
        return CurrencyRate(
            code=item["Ccy"],
            rate=float(item["Rate"]),
            diff=float(item.get("Diff", 0) or 0),
            date=item.get("Date", ""),
        )
    except (KeyError, ValueError, TypeError):
        return None


@router.get("/rates", response_model=CurrencyRates)
async def get_rates() -> CurrencyRates:
    """Return current USD/EUR/RUB rates from CBU, cached 1h."""
    cached = _cache.get("payload")
    if cached and _now_ts() - _cache.get("at", 0) < CACHE_TTL_SECONDS:
        return cached

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            rates: List[CurrencyRate] = []
            for code in CODES:
                resp = await client.get(f"{CBU_URL}{code}/")
                resp.raise_for_status()
                data = resp.json()
                if isinstance(data, list) and data:
                    parsed = _parse_rate(data[0])
                    if parsed:
                        rates.append(parsed)
            if not rates:
                raise HTTPException(status_code=502, detail="No rates returned")
            payload = CurrencyRates(
                rates=rates,
                fetched_at=datetime.now(timezone.utc).isoformat(),
            )
            _cache["payload"] = payload
            _cache["at"] = _now_ts()
            return payload
    except httpx.HTTPError as e:
        if cached:
            return cached
        raise HTTPException(status_code=502, detail=f"CBU unreachable: {e}")
