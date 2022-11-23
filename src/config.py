import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pydantic import BaseSettings, validator

load_dotenv()

ENABLE_TRACER = bool(os.getenv('ENABLE_TRACER', False))


class VkConfig(BaseSettings):
    redirect_uri: str
    oath_url: str = None

    @validator('oath_url')
    def make_oath_url(cls, v, values):
        template = (
            'https://oauth.vk.com/authorize?client_id=51474914&redirect_uri='
            '{redirect_uri}&scope=email&display=page&response_type=code'
        )
        redirect_url = quote_plus(values['redirect_uri'])
        return template.format(redirect_uri=redirect_url)

    class Config:
        env_file = "../.env"
        env_file_encoding = 'utf-8'
        env_prefix = "vk_"


class RedisSettings(BaseSettings):
    host: str
    port: int
    password: str

    class Config:
        env_file = "../.env"
        env_file_encoding = 'utf-8'
        env_prefix = "redis_"


class JaegerSettings(BaseSettings):
    host: str
    port: int

    class Config:
        env_file = "../.env"
        env_file_encoding = 'utf-8'
        env_prefix = "jaeger_"


class FlaskAppSettings(BaseSettings):
    jwt_access_token_ttl: int
    jwt_refresh_token_ttl: int

    class Config:
        env_file = "../.env"
        env_file_encoding = 'utf-8'


class AuthDBSettings(BaseSettings):
    host: str
    port: int
    user: str
    password: str
    database: str

    class Config:
        env_file = "../.env"
        env_file_encoding = 'utf-8'
        env_prefix = "auth_db_"


redis_settings = RedisSettings()
flask_app_settings = FlaskAppSettings()
auth_db_settings = AuthDBSettings()
vk_settings = VkConfig()

DB_CONNECTION_STRING = (
    f'postgresql+psycopg2://'
    f'{auth_db_settings.user}:{auth_db_settings.password}@'
    f'{auth_db_settings.host}:{auth_db_settings.port}/'
    f'{auth_db_settings.database}'
)
