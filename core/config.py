from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent


class RedisSettings(BaseModel):
    HOST: str = "localhost"
    PORT: str = "6379"
    DB: str = "0"


class DbSettings(BaseModel):
    USER: str = "postgres"
    PASSWORD: str = "postgres"
    HOST: str = "localhost"
    PORT: str = "5432"
    DB_NAME: str = "demo_db"
    url: str = f"postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
    echo: bool = True


class AuthJWTSettings(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "private_key.pem"
    public_key_path: Path = BASE_DIR / "certs" / "public_key.pem"
    algorithm: str = "RS512"
    access_token_expire_minutes: int = 3
    refresh_token_expire_minutes: int = 15


class Settings(BaseSettings):
    r: RedisSettings = RedisSettings()
    db: DbSettings = DbSettings()
    auth_jwt: AuthJWTSettings = AuthJWTSettings()


settings = Settings()
