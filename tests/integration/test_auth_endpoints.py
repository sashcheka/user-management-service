# from io import BytesIO
#
# import pytest
# import pytest_asyncio
# from httpx import AsyncClient
#
# from src.main import app
#
#
# @pytest_asyncio.fixture(scope="function")
# async def async_client():
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         yield client
#
#
# @pytest.fixture()
# def mock_user_signup_data() -> dict:
#     user_signup_data = {
#         "name": "test_name",
#         "surname": "test_surname",
#         "username": "test_username",
#         "password": "test_password",
#         "phone_number": "123-456-789",
#         "email": "test_email@example.com",
#         "role": "USER",
#         "group_name": "test_group_name",
#     }
#     return user_signup_data
#
#
# @pytest.fixture()
# def mock_files() -> dict:
#     files = {"image": ("image.jpg", BytesIO(b"fake_image_data"), "image/jpeg")}
#     return files
#
#
# @pytest.fixture()
# def mock_user_login_data() -> dict:
#     user_login_data = {
#         "username": "test_username",
#         "password": "test_password",
#     }
#     return user_login_data
#
#
# def assert_response_data(
#     response: dict,
# ):
#     assert response["name"] == "test_name"
#     assert response["surname"] == "test_surname"
#     assert response["username"] == "test_username"
#     assert response["phone_number"] == "123-456-789"
#     assert response["email"] == "test_email@example.com"
#     assert response["role"] == "USER"
#     assert response["group_name"] == "test_group_name"
#
#
# @pytest.mark.asyncio
# @pytest.mark.integration
# async def test_signup(
#     async_client: AsyncClient,
#     mock_user_signup_data: dict,
#     mock_files: dict,
# ):
#     response = await async_client.post(
#         "/auth/signup/",
#         data=mock_user_signup_data,
#         files=mock_files,
#     )
#
#     assert response.status_code == 200, response.text
#     assert_response_data(response=response.json())
#
#
# @pytest.mark.asyncio
# @pytest.mark.integration
# async def test_login(
#     async_client: AsyncClient,
#     mock_user_login_data: dict,
# ):
#     response = await async_client.post(
#         "/auth/login/",
#         json=mock_user_login_data,
#     )
#
#     assert response.status_code == 200, response.text
#     assert "access_token" in response.json()
#     assert response.json()["token_type"] == "Bearer"
#     assert "refresh_token" in response.json()
