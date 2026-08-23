from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class EventBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

# Dùng khi tạo Event
class EventCreate(EventBase):
    pass

# Dùng khi sửa Event
class EventUpdate(BaseModel):
    name: Optional[str] = Field(None,min_length=1,max_length=255)
    description: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# Dữ liệu trả về
class EventResponse(EventBase):
    id: int
    owner_id: int
    created_at: datetime
    is_deleted: bool
    model_config = ConfigDict(from_attributes=True)