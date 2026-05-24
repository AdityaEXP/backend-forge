from auth_backend.database.db import database
from asyncpg.exceptions import UniqueViolationError
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

from auth_backend.services.security import (
    hash_password, check_password, create_access_token, create_refresh_token
    , verify_refresh_token, verify_access_token
)
from auth_backend.services.user import get_user_by_email, get_user_by_id


from auth_backend.core.config import REFRESH_TOKEN_EXPIRE_MINUTES, ACCESS_TOKEN_EXPIRE_MINUTES


security = HTTPBearer()  # For token authentication in FastAPI routes

# USER RELATED FUNCTIONS
async def get_current_user(token: str = Depends(security)):
    payload = verify_access_token(token.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = await get_user_by_email(payload.get("email"))
    print(f"Payload email: {payload}")
    print(f"Current user: {user}")
    return user

async def delete_refresh_token(refresh_token: str):
    async with database.pool.acquire() as connection:
        await connection.execute("DELETE FROM refresh_tokens WHERE token = $1", refresh_token)

# SINGUP, LOGIN, REFRESH TOKEN FUNCTIONS

async def signup_user(username: str, email:str, password: str) -> bool:
    async with database.pool.acquire() as connection:
        try:
            await connection.execute(
                    "INSERT INTO users (username, email, hashed_password) VALUES ($1, $2, $3)",
                    username, email, hash_password(password)
                )
            return True
        except UniqueViolationError:
            print("Username or email already exists")
            return False
        except Exception as e:
            print(f"Error signing up user: {e}")
            return False
    

async def rotate_or_insert_refresh_token(user_id: int) -> str:
    user = await get_user_by_id(user_id)
    if not user:
        raise ValueError("User not found")
    

    new_token = create_refresh_token(user_id, expires_delta=REFRESH_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token({"email": user['email'], "type": "access"}, expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES)
    async with database.pool.acquire() as connection:
        await connection.execute(
            "INSERT INTO refresh_tokens (user_id, token) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET token = EXCLUDED.token",
            user_id, new_token 
        )
    return access_token, new_token

async def check_refresh_token_exists(user_id: int, refresh_token: str) -> bool:
    async with database.pool.acquire() as connection:
        token = await connection.fetchval("SELECT token FROM refresh_tokens WHERE user_id = $1 AND token = $2", user_id, refresh_token)
        return token is not None

async def login_user(email: str, password: str) -> bool | dict:
    user = await get_user_by_email(email)
    if user and check_password(password, user['hashed_password']):
        try:
            access_token, refresh_token = await rotate_or_insert_refresh_token(user['id'])
        except ValueError as e:
            print(f"Error registering refresh token: {e}")
            return False
        
        return dict(user) | {"access_token": access_token, "refresh_token": refresh_token}

    return False

async def refresh_access_token(refresh_token: str) -> bool | dict:
    payload = verify_refresh_token(refresh_token)
    if payload is None:
        return False
    
    user_id = payload.get("user_id")
    is_valid = await check_refresh_token_exists(user_id, refresh_token)
    if not is_valid:
        return False

    access_token, new_refresh_token = await rotate_or_insert_refresh_token(user_id)
    return {"access_token": access_token, "refresh_token": new_refresh_token}
