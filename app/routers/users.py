from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from dependencies.auth import get_admin_user, get_current_active_user
from models import User
from schemas import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])

@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current User",
    description="Lấy thông tin cá nhân của người dùng đang đăng nhập dựa trên JWT Token",
)
def read_users_me(current_user: User = Depends(get_current_active_user)) -> UserResponse:
    """Lấy thông tin cá nhân của người dùng đang đăng nhập dựa trên token"""
    return current_user

@router.get(
    "/",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List Users (Admin)",
    description="API Dành riêng cho Admin: Tra cứu, lọc danh sách toàn bộ người dùng trong hệ thống",
)
def get_users(search: str | None = None, is_active: bool | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)) -> list[User]:
    """API Dành riêng cho Admin: Tra cứu, lọc danh sách toàn bộ người dùng trong hệ thống"""
    query = db.query(User)
    if search:
        query = query.filter((User.email.ilike(f"%{search}%")) | (User.full_name.ilike(f"%{search}%")))
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    return query.all()