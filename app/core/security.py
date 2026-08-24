from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from .config import settings


def get_password_hash(password: str) -> str:
    """Hash password bằng bcrypt"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra password"""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Tạo JWT Access Token."""
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    return jwt.encode({**data, "exp": expire}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)