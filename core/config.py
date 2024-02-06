from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent


class LocalStackSettings(BaseSettings):
    HOST: str = "localstack"
    PORT: str = "4566"
    aws_access_key_id: str = "aws_access_key_id"
    aws_secret_access_key: str = "aws_secret_access_key"
    region_name: str = "us-east-1"
    bucket_name: str = "my-local-bucket"

    @property
    def url(self) -> str:
        return f"http://{self.HOST}:{self.PORT}"


class RabbitMQSettings(BaseSettings):
    USER: str = "guest"
    PASSWORD: str = "guest"
    HOST: str = "rabbitmq"
    PORT: str = "5672"

    @property
    def url(self) -> str:
        return f"amqp://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/"


class RedisSettings(BaseModel):
    HOST: str = "redis"
    PORT: str = "6379"
    DB: str = "0"


class DbSettings(BaseModel):
    USER: str = "postgres"
    PASSWORD: str = "postgres"
    HOST: str = "db"
    PORT: str = "5432"
    DB_NAME: str = "demo_db"
    echo: bool = True

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB_NAME}"


class AuthJWTSettings(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "private_key.pem"
    public_key_path: Path = BASE_DIR / "certs" / "public_key.pem"
    algorithm: str = "RS512"
    access_token_expire_minutes: int = 10
    refresh_token_expire_minutes: int = 60


class Settings(BaseSettings):
    localstack: LocalStackSettings = LocalStackSettings()
    rabbitmq: RabbitMQSettings = RabbitMQSettings()
    r: RedisSettings = RedisSettings()
    db: DbSettings = DbSettings()
    auth_jwt: AuthJWTSettings = AuthJWTSettings()


settings = Settings()
