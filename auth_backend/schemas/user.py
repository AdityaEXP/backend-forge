from pydantic import BaseModel, EmailStr, Field


class MeResponse(BaseModel):
    id: int
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., max_length=100)