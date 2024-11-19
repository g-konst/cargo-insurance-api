from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.models import CargoRate, CargoType
from app.services.base.handler import BaseHandler
from app.services.cargo.schemas import PostRatesSchema


class CargoTypeHandler(BaseHandler[CargoType]):
    model = CargoType


class CargoRateHandler(BaseHandler[CargoRate]):
    model = CargoRate

    @classmethod
    async def get_rate(
        cls, session: AsyncSession, cargo_type: str, dt: date
    ) -> CargoRate:
        type_stmt = await CargoTypeHandler.get_by(
            session, name=cargo_type, only_stmt=True
        )

        rates_stmt = await cls.get_by(
            session,
            filters=(
                CargoRate.cargo_type_id.in_(
                    type_stmt.with_only_columns(CargoType.id).subquery()
                ),
            ),
            dt=dt,
            only_stmt=True,
        )
        stmt = rates_stmt.options(selectinload(CargoRate.cargo_type))

        result = await session.scalars(stmt)
        return result.one_or_none()

    @classmethod
    async def post_rates(
        cls,
        session: AsyncSession,
        data: PostRatesSchema,
    ) -> None:

        objects = list()
        cargo_types = set()
        for dt, cargo_rates in data.root.items():
            for cargo_rate in cargo_rates:
                cargo_types.add(cargo_rate.cargo_type)
                objects.append(
                    dict(
                        dt=dt,
                        cargo_type=cargo_rate.cargo_type,
                        rate=cargo_rate.rate,
                    )
                )

        cargo_types_stmt = await CargoTypeHandler.get_list(
            session=session,
            filters=(CargoType.name.in_(cargo_types),),
            only_stmt=True,
        )

        cargo_types_result = (await session.scalars(cargo_types_stmt)).all()
        if len(cargo_types_result) != len(cargo_types):
            new_cargo_types_result = await CargoTypeHandler.create_many(
                session,
                [
                    {"name": name}
                    for name in cargo_types
                    if name not in [res.name for res in cargo_types_result]
                ],
            )
            cargo_types_result.extend(new_cargo_types_result)
        cargo_types = dict(map(lambda r: (r.name, r), cargo_types_result))

        for obj in objects:
            cargo_type_name = obj.pop("cargo_type")
            obj["cargo_type_id"] = cargo_types[cargo_type_name].id

        return await cls.upsert_many(session, ("cargo_type_id", "dt"), objects)
