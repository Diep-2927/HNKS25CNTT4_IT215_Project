from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from models.event_staff import EventStaffRole

class EventBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    """Hỗ trợ cập nhật một phần (PATCH): toàn bộ các field đều là Optional"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class EventResponse(EventBase):
    id: int
    owner_id: int
    created_at: datetime
    is_deleted: bool
    model_config = ConfigDict(from_attributes=True)

class EventStaffCreate(BaseModel):
    user_id: int
    role: EventStaffRole = EventStaffRole.MEMBER

class EventStaffResponse(BaseModel):
    id: int
    event_id: int
    user_id: int
    role: EventStaffRole
    joined_at: datetime
    model_config = ConfigDict(from_attributes=True)