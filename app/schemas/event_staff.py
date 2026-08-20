from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from models.event_staff import EventStaffRole

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