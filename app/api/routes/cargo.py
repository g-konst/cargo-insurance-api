from datetime import date
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Query, status, Depends, HTTPException

from app.database import db_helper
from app.services.cargo.schemas import PostRatesSchema, CargoRate
from app.services.cargo.handler import CargoRateHandler

router = APIRouter(prefix="/cargo", tags=["cargo"])


@router.get("/{cargo_type}/rates")
async def get_rate(
    cargo_type: str,
    dt: date = Query(..., default_factory=date.today),
    session: AsyncSession = Depends(db_helper.get_session),
) -> Optional[CargoRate]:
    rate_data = await CargoRateHandler.get_rate(session, cargo_type, dt)
    if not rate_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rate not found for this date.",
        )
    return rate_data


@router.get("/{cargo_type}/insurance")
async def get_insurance(
    cargo_type: str,
    price: int,
    dt: date = Query(..., default_factory=date.today),
    session: AsyncSession = Depends(db_helper.get_session),
) -> float:
    rate_data = await CargoRateHandler.get_rate(session, cargo_type, dt)
    if not rate_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rate not found for this date.",
        )

    return float(f"{price * rate_data.rate:2f}")


@router.post("/rates", status_code=status.HTTP_201_CREATED)
async def post_rates(
    data: PostRatesSchema,
    session: AsyncSession = Depends(db_helper.get_session),
) -> None:
    return await CargoRateHandler.post_rates(session, data)
