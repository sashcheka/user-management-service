import redis

from core.config import settings

REFRESH_TOKEN_EXPIRE_MINUTES = settings.auth_jwt.REFRESH_TOKEN_EXPIRE_MINUTES

redis_client = redis.Redis(
    host=settings.r.HOST,
    port=settings.r.PORT,
    db=settings.r.DB,
)


def delete_token_from_redis(token: str):
    redis_client.delete(token)


def token_exists_in_redis(token: str) -> bool:
    return redis_client.exists(token)


def add_refresh_token_to_redis(refresh_token: str):
    redis_client.setex(refresh_token, REFRESH_TOKEN_EXPIRE_MINUTES * 60, "valid")
