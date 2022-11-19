import redis
from ..config import redis_settings, redis_rl_settings

redis_cli = redis.Redis(
    host=redis_settings.host,
    port=redis_settings.port,
    password=redis_settings.password,
)
