from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from db.database import get_db
from models import User
from schemas import UserResponse
from dependencies.auth import get_current_active_user, get_admin_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Lấy thông tin cá nhân của người dùng đang đăng nhập dựa trên token"""
    return current_user

@router.get("/", response_model=List[UserResponse])
def get_users(
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user) # Yêu cầu quyền ADMIN
):
    """API Dành riêng cho Admin: Tra cứu, lọc danh sách toàn bộ người dùng trong hệ thống"""
    query = db.query(User)
    if search:
        query = query.filter(
            (User.email.ilike(f"%{search}%")) |
            (User.full_name.ilike(f"%{search}%"))
        )
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    return query.all()