from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.routing import APIRouter
from auth_backend.schemas.auth import LoginSchema, SignupSchema, UserResponseLoginWithRefresh, UserResponseSignUp, UserResponseLogin
from auth_backend.services.auth import signup_user, login_user, refresh_access_token, delete_refresh_token
from auth_backend.services.rate_limit import get_login_attempts, increment_login_attempts, clear_login_attempts

from auth_backend.core.config import REFRESH_TOKEN_EXPIRE_MINUTES, ACCESS_TOKEN_EXPIRE_MINUTES




router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/refresh", response_model=UserResponseLoginWithRefresh)
async def refresh_token(response: Response, request: Request) -> UserResponseLoginWithRefresh:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")
    
    data = await refresh_access_token(refresh_token)
    if not data:
        response.delete_cookie("refresh_token")
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    
    access_token, new_refresh_token = data['access_token'], data['refresh_token']

    
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,  # Use HTTPS in production
        samesite="lax",  # Adjust based on your frontend domain
        max_age=REFRESH_TOKEN_EXPIRE_MINUTES * 60
    )  # Convert minutes to seconds

    return UserResponseLoginWithRefresh(access_token=access_token)

@router.post("/login", response_model=UserResponseLogin)
async def login(response: Response, user_request: LoginSchema) -> UserResponseLogin:
    logging_attempts = await get_login_attempts(user_request.email)
    if logging_attempts >= 5:
        raise HTTPException(status_code=429, detail="Too many failed login attempts. Please try again later.")
    

    user = await login_user(user_request.email, user_request.password)
    if not user:
        await increment_login_attempts(user_request.email)
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    response.set_cookie(
        key="refresh_token",
        value=user['refresh_token'],
        httponly=True,
        secure=False,  # Use HTTPS in production
        samesite="lax",  # Adjust based on your frontend domain
        max_age=REFRESH_TOKEN_EXPIRE_MINUTES * 60
    )  # Convert minutes to seconds

    await clear_login_attempts(user['email'])

    return UserResponseLogin(username=user['username'], email=user['email'], access_token=user['access_token'])

@router.post("/signup", response_model=UserResponseSignUp)
async def signup(user: SignupSchema) -> UserResponseSignUp:

    signup_success = await signup_user(user.username, user.email, user.password)

    if not signup_success:
        raise HTTPException(status_code=400, detail="Username already exists")

    return UserResponseSignUp(username=user.username, email=user.email)

@router.post("/logout")
async def logout(response: Response, request: Request):

    refresh_token = request.cookies.get("refresh_token")

    if refresh_token:
        await delete_refresh_token(refresh_token)

    response.delete_cookie("refresh_token")

    return {"message": "Logged out successfully"}