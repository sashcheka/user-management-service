from datetime import timedelta

import pytest
from fastapi import HTTPException, status
from freezegun import freeze_time

from core.redis_helper import redis_client
from src.auth.jwt_utils import decode_jwt, encode_jwt
from src.auth.tokens_utils import (
    create_access_token,
    create_refresh_token,
    delete_token_from_redis,
    get_payload_by_token,
)


def assert_payload_data(
    decoded_payload: dict,
    expected_token_type: str,
):
    assert decoded_payload["sub"] == "550e8400-e29b-41d4-a716-446655440000"
    assert decoded_payload["username"] == "username"
    assert decoded_payload["email"] == "email@example.com"
    assert decoded_payload["token_type"] == expected_token_type
    assert "exp" in decoded_payload
    assert "iat" in decoded_payload


@pytest.fixture(autouse=True)
def clear_redis():
    redis_client.flushdb()
    yield


@pytest.fixture
def mock_payload():
    payload = {
        "sub": "550e8400-e29b-41d4-a716-446655440000",
        "username": "username",
        "email": "email@example.com",
    }
    return payload


@pytest.fixture(params=["access_token", "refresh_token"])
def valid_jwt(request, mock_payload):
    token_type = request.param
    return encode_jwt(
        payload=mock_payload,
        token_type=token_type,
        expire_timedelta=timedelta(minutes=5),
    )


@pytest.mark.unit
def test_encode_and_decode_jwt(valid_jwt):
    decoded_payload = decode_jwt(valid_jwt)
    expected_token_type = decoded_payload["token_type"]
    assert_payload_data(
        decoded_payload=decoded_payload,
        expected_token_type=expected_token_type,
    )


@pytest.mark.unit
def test_create_access_token(mock_payload):
    token = create_access_token(mock_payload)
    decoded_payload = decode_jwt(token)
    assert_payload_data(
        decoded_payload=decoded_payload,
        expected_token_type="access_token",
    )


@pytest.mark.unit
def test_create_refresh_token(mock_payload):
    token = create_refresh_token(mock_payload)
    decoded_payload = decode_jwt(token)
    assert_payload_data(
        decoded_payload=decoded_payload,
        expected_token_type="refresh_token",
    )


@pytest.mark.unit
def test_token_deletion():
    test_token = "refresh_token_to_delete"
    redis_client.set(test_token, "test_value")

    delete_token_from_redis(test_token)

    assert redis_client.exists(test_token) == 0


@pytest.mark.unit
def test_access_token_expiry(mock_payload):
    with freeze_time("2022-01-01 12:00:00"):
        access_token = create_access_token(payload=mock_payload)

    with freeze_time("2022-01-01 12:11:00"), pytest.raises(HTTPException) as exc_info:
        get_payload_by_token(access_token)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid refresh token" in exc_info.value.detail.lower()


@pytest.mark.unit
def test_refresh_token_expiry(mock_payload):
    with freeze_time("2022-01-01 12:00:00"):
        refresh_token = create_refresh_token(payload=mock_payload)

    with freeze_time("2022-01-01 13:01:00"), pytest.raises(HTTPException) as exc_info:
        get_payload_by_token(refresh_token)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid refresh token" in exc_info.value.detail.lower()


@pytest.mark.unit
def test_decode_jwt_with_invalid_token():
    invalid_token = "invalid.token.here"
    with pytest.raises(HTTPException) as exc_info:
        get_payload_by_token(invalid_token)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "jwt error" in exc_info.value.detail.lower()
