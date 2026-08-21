from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int
    owner_id: int
    created_at: datetime
    is_deleted: bool
    
    model_config = ConfigDict(from_attributes=True)