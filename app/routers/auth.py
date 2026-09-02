from datetime import timedelta
from enum import Enum
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.config import settings
from core.security import create_access_token, get_password_hash, verify_password
from db.database import get_db
from models import User
from schemas import UserCreate, UserLogin, UserResponse
from schemas.token import Token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="API Đăng ký: Kiểm tra email trùng lặp và băm mật khẩu trước khi lưu DB",
)
def register(user: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    """API Đăng ký: Kiểm tra email trùng lặp và băm mật khẩu trước khi lưu DB"""
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email này đã tồn tại")

    new_user = User(
        email=user.email,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="API Đăng nhập: Kiểm tra mật khẩu, trạng thái tài khoản và trả về JWT Bearer Token",
)
def login(data: UserLogin, db: Session = Depends(get_db)) -> dict:
    """API Đăng nhập: Kiểm tra mật khẩu, trạng thái tài khoản và trả về JWT Bearer Token"""
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản hoặc mật khẩu không chính xác",
        )
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tài khoản đã bị vô hiệu hóa")

    role_value = user.role.value if isinstance(user.role, Enum) else user.role
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": user.email, "id": user.id, "full_name": user.full_name, "role": role_value},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}