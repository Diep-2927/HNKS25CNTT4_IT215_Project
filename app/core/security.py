import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from .config import settings

def get_password_hash(
    password: str
) -> str:
    """
    Hash password bằng bcrypt.
    """

    password_bytes = password.encode(
        "utf-8"
    )

    salt = bcrypt.gensalt()

    hashed_password = bcrypt.hashpw(
        password_bytes,
        salt
    )

    return hashed_password.decode(
        "utf-8"
    )


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Kiểm tra password.
    """

    password_bytes = plain_password.encode(
        "utf-8"
    )

    hashed_password_bytes = (
        hashed_password.encode("utf-8")
    )

    try:
        return bcrypt.checkpw(
            password_bytes,
            hashed_password_bytes,
        )

    except ValueError:
        return False


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
):
    """
    Tạo JWT Access Token.
    """

    to_encode = data.copy()

    if expires_delta:
        expire = (
            datetime.now(timezone.utc)
            + expires_delta
        )
    else:
        expire = (
            datetime.now(timezone.utc)
            + timedelta(minutes=15)
        )

    to_encode.update({
        "exp": expire
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return encoded_jwt