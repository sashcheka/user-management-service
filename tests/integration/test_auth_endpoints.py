from io import BytesIO

import pytest
from httpx import AsyncClient

from src.main import app


@pytest.mark.asyncio
@pytest.mark.integration
async def test_signup():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        user_data = {
            "name": "Test",
            "surname": "User",
            "username": "test_username",
            "password": "test_password",
            "phone_number": "1234567890",
            "email": "testuser@example.com",
            "role": "USER",
            "group_name": "Test Group",
        }

        files = {
            "image": (
                "sunflower.jpg",
                BytesIO(b"fake_image_data"),
                "image/jpeg",
            ),
        }

        response = await ac.post("/auth/signup/", data=user_data, files=files)

        assert response.status_code == 200, response.text
        assert response.json()["email"] == "testuser@example.com"
