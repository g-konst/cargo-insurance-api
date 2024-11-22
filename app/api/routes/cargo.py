from datetime import date
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Query, status, Depends, HTTPException, Request

from app.database import db_helper
from app.services.cargo.schemas import (
    PostRatesSchema,
    CargoRate,
    DeleteRatesSchema,
)
from app.services.cargo.handler import CargoRateHandler
from app.utils.decorators import log_action

router = APIRouter(prefix="/cargo", tags=["cargo"])


@router.get("/{cargo_type}/rates")
async def get_rate(
    request: Request,
    cargo_type: str,
    dt: date = Query(..., default_factory=date.today),
    session: AsyncSession = Depends(db_helper.get_session),
) -> Optional[CargoRate]:
    request.state.kafka_action = f"get_{cargo_type}_rate"
    rate_data = await CargoRateHandler.get_rate(session, cargo_type, dt)
    if not rate_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rate not found for this date.",
        )
    return rate_data


@router.get("/{cargo_type}/insurance")
async def get_insurance(
    request: Request,
    cargo_type: str,
    price: int,
    dt: date = Query(..., default_factory=date.today),
    session: AsyncSession = Depends(db_helper.get_session),
) -> float:
    request.state.kafka_action = f"get_{cargo_type}_insurance"
    rate_data = await CargoRateHandler.get_rate(session, cargo_type, dt)
    if not rate_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rate not found for this date.",
        )

    return float(f"{price * rate_data.rate:2f}")


@router.post("/rates", status_code=status.HTTP_201_CREATED)
@log_action
async def post_rates(
    request: Request,
    data: PostRatesSchema,
    session: AsyncSession = Depends(db_helper.get_session),
) -> None:
    return await CargoRateHandler.post_rates(session, data)


@router.delete("/rates", status_code=status.HTTP_204_NO_CONTENT)
@log_action(kafka_action="delete")
async def delete_rates(
    request: Request,
    data: DeleteRatesSchema,
    session: AsyncSession = Depends(db_helper.get_session),
) -> None:
    await CargoRateHandler.delete_rates(session, data)
