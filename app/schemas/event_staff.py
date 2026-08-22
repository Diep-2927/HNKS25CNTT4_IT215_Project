from datetime import datetime
from pydantic import BaseModel, ConfigDict
from models.event_staff import EventStaffRole

# Dữ liệu nhận vào khi thêm member
class EventStaffCreate(BaseModel):
    user_id: int
    role: EventStaffRole = EventStaffRole.MEMBER

# Dữ liệu trả về
class EventStaffResponse(BaseModel):
    id: int
    event_id: int
    user_id: int
    role: EventStaffRole
    joined_at: datetime
    model_config = ConfigDict(from_attributes=True)