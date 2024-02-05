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
    url: str = f"http://{HOST}:{PORT}"


class RabbitMQSettings(BaseSettings):
    USER: str = "guest"
    PASSWORD: str = "guest"
    HOST: str = "rabbitmq"
    PORT: str = "5672"
    CLOUDAMQP_URL: str = f"amqp://{USER}:{PASSWORD}@{HOST}:{PORT}/"


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
    url: str = f"postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
    echo: bool = True


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
