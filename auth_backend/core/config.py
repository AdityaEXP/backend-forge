import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 3600))  # Default to 1 hour if not set
REFRESH_TOKEN_EXPIRE_MINUTES = float(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 3600 * 7))  # Default to 7 days if not set
REDIS_HOST = os.getenv("REDIS_HOST", "redis")  # Default to "redis" for Docker, can be overridden for local development