from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware import Middleware

from app.api.routes import router as api_router
from app.api.middlewares.user_id import UserIDMiddleware
from app.api.middlewares.kafka_logger import KafkaLoggerMiddleware
from app.database import db_helper
from app.config import settings
from app.broker import app_broker


@asynccontextmanager
async def lifespan(app: FastAPI):
    await app_broker.connect()
    yield
    await db_helper.dispose()
    await app_broker.dispose()


application = FastAPI(
    title="Cargo Insurance API",
    version="0.1.0",
    description="Cargo Insurance API",
    license_info={
        "name": "MIT",
        "url": "https://choosealicense.com/licenses/mit/",
    },
    contact={
        "name": "Konstantin Grudnitskiy",
        "email": "k.grudnitskiy@yandex.ru",
    },
    middleware=[
        Middleware(UserIDMiddleware),
        Middleware(KafkaLoggerMiddleware),
    ],
    lifespan=lifespan,
)
application.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(
        app="app.api.http_server:application",
        host=settings.api.host,
        port=settings.api.port,
        reload=True,
    )
