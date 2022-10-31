import redis


class RedisCli:
    def __init__(self) -> None:
        self = redis.Redis(host='localhost', port=6379, db=0)

redis_cli = redis.Redis(host='localhost', port=6379, db=0)
