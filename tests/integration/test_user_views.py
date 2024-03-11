import pytest
from httpx import AsyncClient

from tests.utils import (
    assert_response_user_data,
    login_and_get_access_token,
    signup_user,
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_self_info(
    async_client: AsyncClient,
    mock_user_signup_data: dict,
    mock_files: dict,
    mock_user_login_data: dict,
):
    access_token = await login_and_get_access_token(
        async_client=async_client,
        user_login_data=mock_user_login_data,
    )

    response = await async_client.get(
        "/user/me/",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 200, response.text
    assert_response_user_data(response=response.json())


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_self_info_partial(
    async_client: AsyncClient,
    mock_user_login_data: dict,
    mock_files: dict,
):
    access_token = await login_and_get_access_token(
        async_client=async_client,
        user_login_data=mock_user_login_data,
    )

    user_update_data = {
        "name": (None, "new_test_name"),
        "surname": (None, "new_test_surname"),
    }

    data = user_update_data.copy()
    data.update(mock_files)

    response = await async_client.patch(
        "/user/me/",
        files=data,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200, response.text

    updated_user_info = response.json()
    assert updated_user_info["name"] == "new_test_name"
    assert updated_user_info["surname"] == "new_test_surname"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_self_info(
    async_client: AsyncClient,
    mock_user_login_data: dict,
    mock_files: dict,
):
    access_token = await login_and_get_access_token(
        async_client=async_client,
        user_login_data=mock_user_login_data,
    )

    response = await async_client.delete(
        "/user/me/",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["detail"] == f"User new_test_name successfully deleted"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_users_info(
    async_client: AsyncClient,
    mock_admin_signup_data: dict,
    mock_files: dict,
    mock_admin_login_data: dict,
):
    await signup_user(
        async_client=async_client,
        user_signup_data=mock_admin_signup_data,
        user_files=mock_files,
        role="ADMIN",
    )

    access_token = await login_and_get_access_token(
        async_client=async_client,
        user_login_data=mock_admin_login_data,
    )

    response = await async_client.get(
        "/users/",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 200, response.text
    assert len(response.json()) == 1, response.text
