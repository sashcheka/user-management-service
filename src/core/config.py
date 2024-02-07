import os
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent


class LocalStackSettings(BaseSettings):
    HOST: str = os.environ["LOCALSTACK_HOST"]
    PORT: str = os.environ["LOCALSTACK_PORT"]
    AWS_ACCESS_KEY_ID: str = os.environ["LOCALSTACK_AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY: str = os.environ["LOCALSTACK_AWS_SECRET_ACCESS_KEY"]
    REGION_NAME: str = os.environ["LOCALSTACK_REGION_NAME"]
    BUCKET_NAME: str = os.environ["LOCALSTACK_BUCKET_NAME"]

    @property
    def url(self) -> str:
        return f"http://{self.HOST}:{self.PORT}"


class RabbitMQSettings(BaseSettings):
    USER: str = os.environ["RABBITMQ_USER"]
    PASSWORD: str = os.environ["RABBITMQ_PASSWORD"]
    HOST: str = os.environ["RABBITMQ_HOST"]
    PORT: str = os.environ["RABBITMQ_PORT"]

    @property
    def url(self) -> str:
        return f"amqp://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/"


class RedisSettings(BaseModel):
    HOST: str = os.environ["REDIS_HOST"]
    PORT: str = os.environ["REDIS_PORT"]
    DB: str = os.environ["REDIS_DB"]


class DbSettings(BaseModel):
    USER: str = os.environ["DB_USER"]
    PASSWORD: str = os.environ["DB_PASSWORD"]
    HOST: str = os.environ["DB_HOST"]
    PORT: str = os.environ["DB_PORT"]
    DB_NAME: str = os.environ["DB_NAME"]
    echo: bool = True

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB_NAME}"


class AuthJWTSettings(BaseModel):
    PRIVATE_KEY_PATH: Path = BASE_DIR / "certs/private_key.pem"
    PUBLIC_KEY_PATH: Path = BASE_DIR / "certs/public_key.pem"
    ALGORITHM: str = os.environ["AUTH_JWT_ALGORITHM"]
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.environ["AUTH_JWT_ACCESS_TOKEN_EXPIRE_MINUTES"]
    )
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int(
        os.environ["AUTH_JWT_REFRESH_TOKEN_EXPIRE_MINUTES"]
    )


class Settings(BaseSettings):
    localstack: LocalStackSettings = LocalStackSettings()
    rabbitmq: RabbitMQSettings = RabbitMQSettings()
    r: RedisSettings = RedisSettings()
    db: DbSettings = DbSettings()
    auth_jwt: AuthJWTSettings = AuthJWTSettings()


settings = Settings()
