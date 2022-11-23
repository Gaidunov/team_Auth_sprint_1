from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from src.config import (
    redis_settings,
)

LIMITER_SECOND_LIMIT = '1 per second'
LIMITER_MINUTE_LIMIT = '100 per minute'

LIMITER_STRATEGY = 'fixed-window'


def configure_limiter(app: Flask) -> Limiter:
    return Limiter(
        app,
        key_func=get_remote_address,
        default_limits=[
            LIMITER_SECOND_LIMIT,
            LIMITER_MINUTE_LIMIT,
        ],
        storage_uri=f"redis://:{redis_settings.password}@"
            f"redis:{redis_settings.port}/3",
        strategy=LIMITER_STRATEGY,
    )
