from auth_backend.database.db import database

async def get_user_by_email(email: str):
    async with database.pool.acquire() as connection:
        user = await connection.fetchrow("SELECT * FROM users WHERE email = $1", email)
        return user

async def get_user_by_id(user_id: int):
    async with database.pool.acquire() as connection:
        user = await connection.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
        return user