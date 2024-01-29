from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent
USER = "postgres"
PASSWORD = "postgres"
HOST = "localhost"
PORT = "5432"
DB_NAME = "demo_db"


class DbSetting(BaseModel):
    url: str = f"postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
    echo: bool = True


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "private_key.pem"
    public_key_path: Path = BASE_DIR / "certs" / "public_key.pem"
    algorithm: str = "RS512"
    access_token_expire_minutes: int = 3
    refresh_token_expire_minutes: int = 15


class Settings(BaseSettings):
    db: DbSetting = DbSetting()
    auth_jwt: AuthJWT = AuthJWT()


settings = Settings()
