from httpx import AsyncClient


def assert_response_admin_data(
    response: dict,
):
    assert response["name"] == "test_admin_name"
    assert response["surname"] == "test_admin_surname"
    assert response["username"] == "test_admin_username"
    assert response["phone_number"] == "123-456-789"
    assert response["email"] == "test_admin_email@example.com"
    assert response["role"] == "ADMIN"
    assert response["group_name"] == "test_group_name"


def assert_response_moderator_data(
    response: dict,
):
    assert response["name"] == "test_moderator_name"
    assert response["surname"] == "test_moderator_surname"
    assert response["username"] == "test_moderator_username"
    assert response["phone_number"] == "123-456-789"
    assert response["email"] == "test_moderator_email@example.com"
    assert response["role"] == "MODERATOR"
    assert response["group_name"] == "test_group_name"


def assert_response_user_data(
    response: dict,
):
    assert response["name"] == "test_name"
    assert response["surname"] == "test_surname"
    assert response["username"] == "test_username"
    assert response["phone_number"] == "123-456-789"
    assert response["email"] == "test_email@example.com"
    assert response["role"] == "USER"
    assert response["group_name"] == "test_group_name"


async def signup_user(
    async_client: AsyncClient,
    user_signup_data: dict,
    user_files: dict,
    role: str,
) -> dict:
    response = await async_client.post(
        "/auth/signup/",
        data=user_signup_data,
        files=user_files,
    )
    assert response.status_code == 200, response.text
    response_data = response.json()
    if role == "USER":
        assert_response_user_data(response_data)
    elif role == "ADMIN":
        assert_response_admin_data(response_data)
    elif role == "MODERATOR":
        assert_response_moderator_data(response_data)

    return response_data


async def login_and_get_access_token(
    async_client: AsyncClient,
    user_login_data: dict,
) -> str:
    response = await async_client.post(
        "/auth/login/",
        json=user_login_data,
    )
    assert response.status_code == 200, response.text
    token_data = response.json()
    return token_data["access_token"]
