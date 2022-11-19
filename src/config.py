from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class VkConfig(BaseSettings):
    client_id:str
    client_secret:str
    redirect_uri:str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        env_prefix = "vk_"


class RedisSettings(BaseSettings):
    host: str
    port: int
    password: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        env_prefix = "redis_"


class FlaskAppSettings(BaseSettings):
    jwt_access_token_ttl: int
    jwt_refresh_token_ttl: int

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


class AuthDBSettings(BaseSettings):
    host: str
    port: int
    user: str
    password: str
    database: str

    class Config:
        env_file = ".env"
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
