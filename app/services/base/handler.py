from typing import TypeVar, Generic, Union, Optional, Iterable, Sequence, List

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models import Base

M = TypeVar("M", bound=Base)


class BaseHandler(Generic[M]):
    model: M

    @classmethod
    async def get(
        cls,
        session: AsyncSession,
        pk: Union[int, str],
    ) -> Optional[M]:
        return await session.get(cls.model, pk)

    @classmethod
    async def get_by(
        cls,
        session: AsyncSession,
        filters: Iterable = tuple(),
        only_stmt: bool = False,
        **kw,
    ) -> Optional[M]:
        stmt = select(cls.model).filter(*filters).filter_by(**kw)
        if only_stmt:
            return stmt
        result = await session.scalars(stmt)
        return result.one_or_none()

    @classmethod
    async def get_list(
        cls,
        session: AsyncSession,
        filters: Iterable = tuple(),
        order_by: str = "id",
        order_direction: str = "asc",
        limit: Optional[int] = None,
        offset: int = 0,
        only_stmt: bool = False,
        **filter_by,
    ) -> Sequence[M]:
        order_by_column = getattr(cls.model, order_by, None)
        if order_by_column and order_direction == "desc":
            order_by_column = order_by_column.desc()

        stmt = (
            select(cls.model)
            .filter(*filters)
            .filter_by(**filter_by)
            .order_by(order_by_column)
            .limit(limit)
            .offset(offset)
        )

        if only_stmt:
            return stmt

        result = await session.scalars(stmt)
        return result.all()

    @classmethod
    async def create(cls, session: AsyncSession, **kw) -> M:
        obj: M = cls.model(**kw)
        session.add(obj)
        await session.commit()
        return obj

    @classmethod
    async def create_many(
        cls, session: AsyncSession, data: List[dict]
    ) -> List[M]:
        objs = [cls.model(**kw) for kw in data]
        session.add_all(objs)
        await session.commit()
        return objs

    @classmethod
    async def update(
        cls, session: AsyncSession, pk: Union[int, str], **kw
    ) -> Optional[M]:
        obj = await session.get(cls.model, pk)
        if obj is None:
            return None
        for key, value in kw.items():
            setattr(obj, key, value)
        session.add(obj)
        await session.commit()
        return obj

    @classmethod
    async def update_many(
        cls, session: AsyncSession, data: List[dict]
    ) -> List[M]:
        objs = []
        for kw in data:
            obj = await session.get(cls.model, kw["pk"])
            if obj:
                for key, value in kw.items():
                    setattr(obj, key, value)
                objs.append(obj)
        session.add_all(objs)
        await session.commit()
        return objs

    @classmethod
    async def delete(
        cls, session: AsyncSession, pk: Union[int, str]
    ) -> Optional[M]:
        obj = await session.get(cls.model, pk)
        if obj is None:
            return None
        await session.delete(obj)
        await session.commit()
        return obj

    @classmethod
    async def delete_many(
        cls, session: AsyncSession, ids: List[Union[int, str]]
    ) -> None:
        stmt = delete(cls.model).filter(cls.model.id.in_(ids))
        await session.execute(stmt)
        await session.commit()

    @classmethod
    async def upsert(cls, session: AsyncSession, pk_field: str, **data) -> M:
        pk_value = data.get(pk_field)
        if not pk_value:
            raise ValueError(f"Primary key field '{pk_field}' is required.")

        stmt = (
            pg_insert(cls.model)
            .values(**data)
            .on_conflict_do_update(
                index_elements=[pk_field],
                set_={
                    key: value
                    for key, value in data.items()
                    if key != pk_field
                },
            )
        )
        await session.execute(stmt)
        await session.commit()

        return await session.get(cls.model, pk_value)

    @classmethod
    async def upsert_many(
        cls, session: AsyncSession, pk_fields: Sequence[str], data: List[dict]
    ) -> None:
        stmt = (
            pg_insert(cls.model)
            .values(data)
            .on_conflict_do_update(
                index_elements=[getattr(cls.model, f) for f in pk_fields],
                set_={
                    key: pg_insert(cls.model).excluded[key]
                    for key in data[0]
                    if key not in pk_fields
                },
            )
        )
        await session.execute(stmt)
        await session.commit()
