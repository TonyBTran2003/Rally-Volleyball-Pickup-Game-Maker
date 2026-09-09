import os
from pathlib import Path

from dotenv import load_dotenv

# find the backend/ directory
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env") #load env file


DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0",
)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not configured")