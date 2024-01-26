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


class Settings(BaseSettings):
    db: DbSetting = DbSetting()


settings = Settings()
