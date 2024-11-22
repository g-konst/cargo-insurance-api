from functools import wraps
from fastapi import Request


def log_action(fn=None, *, kafka_action: str = None):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            request.state.kafka_action = kafka_action or func.__name__
            return await func(request, *args, **kwargs)

        return wrapper

    if fn is not None and callable(fn):
        return decorator(fn)

    return decorator
