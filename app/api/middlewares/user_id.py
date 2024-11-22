from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class UserIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.user_id = request.headers.get("X-User-Id")
        return await call_next(request)
