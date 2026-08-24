from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr 
    full_name: str = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str 

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    """Schema trả về thông tin user"""
    id: int
    role: UserRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)