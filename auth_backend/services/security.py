import bcrypt
import jwt
from datetime import datetime, timedelta

from auth_backend.services.user import get_user_by_email, get_user_by_id
from auth_backend.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    to_encode['type'] = 'access'
    to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=expires_delta)})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(user_id: int, expires_delta: int = REFRESH_TOKEN_EXPIRE_MINUTES) -> str:
    token = jwt.encode({"user_id": user_id, "exp": datetime.utcnow() + timedelta(minutes=expires_delta), 'type': 'refresh'}, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_refresh_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get('type') != 'refresh':
            print("Invalid token type")
            return None
        return payload
    except jwt.ExpiredSignatureError:
        print("Refresh token has expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid refresh token")
        return None

def verify_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get('type') != 'access':
            print("Invalid token type")
            return None
        return payload
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None
    
