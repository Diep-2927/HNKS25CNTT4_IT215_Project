from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from models.event_task import TaskStatus, TaskPriority

class EventTaskBase(BaseModel):

    title: str = Field(
        min_length=1,
        max_length=255,
    )

    description: Optional[str] = None

    priority: TaskPriority = (
        TaskPriority.MEDIUM
    )

    due_date: Optional[datetime] = None


class EventTaskCreate(EventTaskBase):

    assignee_id: Optional[int] = None


class EventTaskUpdate(BaseModel):

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
    )

    description: Optional[str] = None

    status: Optional[TaskStatus] = None

    priority: Optional[TaskPriority] = None

    due_date: Optional[datetime] = None

    assignee_id: Optional[int] = None


class EventTaskResponse(EventTaskBase):

    id: int

    event_id: int

    assignee_id: Optional[int] = None

    status: TaskStatus

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )