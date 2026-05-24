from fastapi import FastAPI, HTTPException, Depends
from fastapi.routing import APIRouter
from auth_backend.services.auth import get_current_user
from auth_backend.schemas.user import MeResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user), response_model=MeResponse):
    return response_model(**current_user)