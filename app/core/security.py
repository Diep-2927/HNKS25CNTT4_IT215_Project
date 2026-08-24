import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from .config import settings

def get_password_hash(password: str) -> str:
    """Băm mật khẩu bằng bcrypt có tự sinh salt an toàn"""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Xác thực mật khẩu"""
    pass_bytes = plain_password.encode("utf-8")
    hashed_pw_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(pass_bytes, hashed_pw_bytes)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Tạo JWT Access Token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encode_jwt