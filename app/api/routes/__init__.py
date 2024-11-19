from fastapi import APIRouter

from app.api.routes.cargo import router as cargo_rates_router
from app.config import settings

ROUTES_V1 = (cargo_rates_router,)

router_v1 = APIRouter(prefix=settings.api.v1.prefix)
for route in ROUTES_V1:
    router_v1.include_router(route)

router = APIRouter(prefix=settings.api.prefix)
router.include_router(router_v1)
