import asyncio
from io import BytesIO

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings
from src.core.db_helper import db_helper
from src.main import app


@pytest.fixture()
def mock_admin_signup_data() -> dict:
    admin_signup_data = {
        "name": "test_admin_name",
        "surname": "test_admin_surname",
        "username": "test_admin_username",
        "password": "test_admin_password",
        "phone_number": "123-456-789",
        "email": "test_admin_email@example.com",
        "role": "ADMIN",
        "group_name": "test_group_name",
    }
    return admin_signup_data


@pytest.fixture()
def mock_user_signup_data() -> dict:
    user_signup_data = {
        "name": "test_name",
        "surname": "test_surname",
        "username": "test_username",
        "password": "test_password",
        "phone_number": "123-456-789",
        "email": "test_email@example.com",
        "role": "USER",
        "group_name": "test_group_name",
    }
    return user_signup_data


@pytest.fixture()
def mock_files() -> dict:
    files = {"image": ("image.jpg", BytesIO(b"fake_image_data"), "image/jpeg")}
    return files


@pytest.fixture()
def mock_admin_login_data() -> dict:
    admin_login_data = {
        "username": "test_admin_username",
        "password": "test_admin_password",
    }
    return admin_login_data


@pytest.fixture()
def mock_moderator_login_data() -> dict:
    moderator_login_data = {
        "username": "test_moderator_username",
        "password": "test_moderator_password",
    }
    return moderator_login_data


@pytest.fixture()
def mock_user_login_data() -> dict:
    user_login_data = {
        "username": "test_username",
        "password": "test_password",
    }
    return user_login_data


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_engine():
    engine = create_async_engine(url=settings.db.url, echo=True)
    yield engine
    asyncio.run(engine.dispose())


@pytest_asyncio.fixture(scope="session")
async def cleanup_db():
    async with db_helper.session_factory() as session:
        yield

        await session.execute(text("TRUNCATE TABLE users, groups CASCADE;"))
        await session.commit()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine, cleanup_db):
    async_session = async_sessionmaker(
        test_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    async with async_session() as session:
        async with session.begin():
            yield session


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session):
    app.dependency_overrides[db_helper.scoped_session_dependencies] = lambda: db_session

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
