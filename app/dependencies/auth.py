from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials 
import jwt
from sqlalchemy.orm import Session
from core.config import settings
from db.database import get_db
from models import User, UserRole
from schemas.token import TokenData

# Khai báo schema xác thực qua Header Authorization
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    Giải mã Token:
    1. Kiểm tra tính hợp lệ và thời hạn của JWT Token.
    2. Lấy email từ payload ('sub') và truy vấn User từ DB.
    """
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin (Token sai hoặc hết hạn)"
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Kiểm tra tài khoản người dùng có đang hoạt động"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Tài khoản đã bị khóa"
        )
    return current_user

def get_admin_user(current_user: User = Depends(get_current_active_user)):
    """Phân quyền"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403, 
            detail="Không có quyền truy cập (Yêu cầu ADMIN)"
        )
    return current_user