from auth_backend.database.reddis_core import redis_client

LOGIN_LIMIT_WINDOW = 60


def login_key(email: str) -> str:
    return f"failed:{email.strip().lower()}"


async def get_login_attempts(email: str) -> int:
    attempts = await redis_client.get(login_key(email))
    return int(attempts) if attempts else 0


async def increment_login_attempts(email: str) -> None:
    key = login_key(email)

    attempts = await redis_client.incr(key)

    if attempts == 1:
        await redis_client.expire(key, LOGIN_LIMIT_WINDOW)


async def clear_login_attempts(email: str) -> None:
    await redis_client.delete(login_key(email))