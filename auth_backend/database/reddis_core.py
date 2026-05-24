import redis.asyncio as redis
from auth_backend.core.config import REDIS_HOST

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=6379,
    decode_responses=True
)