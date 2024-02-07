import redis

from core.config import settings

redis_client = redis.Redis(
    host=settings.r.HOST,
    port=settings.r.PORT,
    db=settings.r.DB,
)


def delete_token_from_redis(token: str):
    redis_client.delete(token)
