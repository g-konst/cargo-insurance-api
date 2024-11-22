from datetime import date

from pydantic import RootModel, BaseModel


class CargoType(BaseModel):
    id: int
    name: str


class CargoRate(BaseModel):
    cargo_type: CargoType
    rate: float


class CargoRateIn(CargoRate):
    cargo_type: str
    dt: date | None = None


class PostRatesSchema(RootModel[dict[date, list[CargoRateIn]]]): ...


class DeleteRatesSchema(BaseModel):
    cargo_type: str | None = None
    dt: date | None = None
