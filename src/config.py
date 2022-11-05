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


class FlaskAppSettings(BaseSettings):
    database_uri: str
    jwt_access_token_ttl: int
    jwt_refresh_token_ttl: int

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


redis_settings = RedisSettings()
flask_app_settings = FlaskAppSettings()
