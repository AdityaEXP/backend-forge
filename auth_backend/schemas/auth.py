from pydantic import BaseModel, EmailStr, Field


class SignupSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., max_length=100)
    password: str = Field(..., min_length=6)

class LoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserResponseSignUp(BaseModel):
    username: str
    email: EmailStr

class UserResponseLogin(BaseModel):
    username: str
    email: EmailStr
    access_token: str

class UserResponseLoginWithRefresh(BaseModel):
    access_token: str