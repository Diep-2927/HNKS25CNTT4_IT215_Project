from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(
        min_length=1,
        max_length=255
    )


class UserCreate(UserBase):
    password: str = Field(
        min_length=6,
        max_length=128
    )


class UserLogin(BaseModel):
    email: EmailStr

    password: str = Field(
        min_length=1,
        max_length=128
    )


class UserResponse(UserBase):
    id: int

    role: UserRole

    is_active: bool

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )