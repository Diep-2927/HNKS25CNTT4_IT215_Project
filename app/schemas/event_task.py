from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from models.event_task import TaskStatus, TaskPriority

# Dữ liệu cơ bản
class EventTaskBase(BaseModel):
    title: str = Field(min_length=1,max_length=255)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None

# Dùng khi tạo task
class EventTaskCreate(EventTaskBase):pass

# Dùng khi cập nhật task
class EventTaskUpdate(BaseModel):
    title: Optional[str] = Field(None,min_length=1,max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None

# Dữ liệu trả về
class EventTaskResponse(EventTaskBase):
    id: int
    event_id: int
    assignee_id: Optional[int] = None
    status: TaskStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)