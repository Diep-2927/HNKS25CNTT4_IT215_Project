from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from models.event_task import TaskPriority, TaskStatus

class EventTaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime | None = None

class EventTaskCreate(EventTaskBase):
    assignee_id: int | None = None

class EventTaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None
    assignee_id: int | None = None

class EventTaskResponse(EventTaskBase):
    id: int
    event_id: int
    assignee_id: int | None = None
    status: TaskStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)