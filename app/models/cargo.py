from datetime import date

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UniqueConstraint, ForeignKey

from .base import Base


class CargoType(Base):
    __tablename__ = "cargo_types"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(unique=True)


class CargoRate(Base):
    __tablename__ = "cargo_rates"

    id: Mapped[int] = mapped_column(primary_key=True)

    rate: Mapped[float] = mapped_column()
    dt: Mapped[date] = mapped_column()
    cargo_type_id: Mapped[int] = mapped_column(ForeignKey("cargo_types.id"))

    cargo_type: Mapped[CargoType] = relationship()

    __table_args__ = (UniqueConstraint("cargo_type_id", "dt"),)

    def __repr__(self):
        return f"CargoRate(rate={self.rate}, dt={self.dt}, cargo_type_id={self.cargo_type_id})"
