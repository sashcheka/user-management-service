import pytest
from httpx import AsyncClient

from tests.utils import assert_response_user_data, login_and_get_access_token


@pytest.mark.asyncio
@pytest.mark.integration
async def test_signup(
    async_client: AsyncClient,
    mock_user_signup_data: dict,
    mock_files: dict,
):
    response = await async_client.post(
        "/auth/signup/",
        data=mock_user_signup_data,
        files=mock_files,
    )

    assert response.status_code == 200, response.text
    assert_response_user_data(response=response.json())


@pytest.mark.asyncio
@pytest.mark.integration
async def test_login(
    async_client: AsyncClient,
    mock_user_login_data: dict,
):
    response = await async_client.post(
        "/auth/login/",
        json=mock_user_login_data,
    )

    assert response.status_code == 200, response.text
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "Bearer"
    assert "refresh_token" in response.json()


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_reset_password(
    async_client: AsyncClient,
    mock_user_login_data: dict,
):
    access_token = await login_and_get_access_token(
        async_client,
        mock_user_login_data,
    )

    response = await async_client.post(
        "/auth/reset-password/",
        json={"email": "test_email@example.com"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200, response.text
    assert (
        response.json()["message"]
        == "Password reset message sent on email: test_email@example.com."
    )


# @pytest.mark.asyncio
# @pytest.mark.asyncio
# async def test_consume_message(
#     async_client: AsyncClient,
#     mock_user_login_data: dict,
# ):
#     access_token = await login_and_get_access_token(
#         async_client,
#         mock_user_login_data,
#     )
#
#     response = await async_client.get(
#         "/auth/consume-message/",
#         headers={"Authorization": f"Bearer {access_token}"},
#     )
#
#     assert response.status_code == 200, response.text
#     assert response.json()["message"] == "Message consumed"
