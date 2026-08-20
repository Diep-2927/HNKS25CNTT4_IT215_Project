from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from models.event_task import TaskStatus, TaskPriority

class EventTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None

class EventTaskCreate(EventTaskBase):
    pass

class EventTaskResponse(EventTaskBase):
    id: int
    event_id: int
    assignee_id: Optional[int] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)