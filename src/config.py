from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class RedisSettings(BaseSettings):
    host: str
    port: int

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        env_prefix = "redis_"


redis_settings = RedisSettings()
