from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.broker import app_broker, KafkaMessage


class KafkaLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if 200 <= response.status_code < 300:
            if kafka_action := getattr(request.state, "kafka_action", None):
                user_id = getattr(request.state, "user_id", None)
                await app_broker.publish(
                    KafkaMessage(
                        user_id=user_id,
                        action=kafka_action,
                    )
                )

        return response
