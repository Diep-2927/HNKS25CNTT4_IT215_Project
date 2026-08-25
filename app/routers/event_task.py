from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from db.database import get_db
from dependencies.auth import get_current_active_user
from models import TaskPriority, TaskStatus, User
from schemas.event_task import EventTaskCreate, EventTaskResponse, EventTaskUpdate
from services import event, event_task

router = APIRouter(prefix="", tags=["Event Tasks"])


@router.post("/{event_id}/event-tasks", response_model=EventTaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(event_id: int, data: EventTaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> EventTaskResponse:
    """Thành viên của event có thể tạo task."""
    event_obj = event.get_event(event_id, db)
    event.check_member(event_obj, current_user, db)
    return event_task.create_task(event_obj.id, data, db)


@router.get("/{event_id}/event-tasks", response_model=list[EventTaskResponse])
def list_tasks(event_id: int, search: str | None = Query(None, max_length=255), task_status: TaskStatus | None = Query(None, alias="status"), priority: TaskPriority | None = None, assignee_id: int | None = None, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100), sort_by: str = Query("created_at"), sort_order: str = Query("desc"), db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> list[EventTaskResponse]:
    """Danh sách task của event"""
    event_obj = event.get_event(event_id, db)
    event.check_member(event_obj, current_user, db)
    return event_task.list_tasks(event_obj.id, search, task_status, priority, assignee_id, page, size, sort_by, sort_order, db)


@router.get("/event-tasks/{task_id}", response_model=EventTaskResponse)
def get_task_detail(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> EventTaskResponse:
    """Xem chi tiết task"""
    task = event_task.get_task(task_id, db)
    event_obj = event.get_event(task.event_id, db)
    event.check_member(event_obj, current_user, db)
    return task


@router.patch("/event-tasks/{task_id}", response_model=EventTaskResponse)
def update_task(task_id: int, data: EventTaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> EventTaskResponse:
    """OWNER hoặc ASSIGNEE được update task."""
    task = event_task.get_task(task_id, db)
    event_obj = event.get_event(task.event_id, db)
    event_task.check_task_permission(task, event_obj, current_user)
    return event_task.update_task(task, event_obj, data, current_user, db)


@router.delete("/event-tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)) -> None:
    """Chỉ OWNER được xóa task"""
    task = event_task.get_task(task_id, db)
    event_obj = event.get_event(task.event_id, db)
    event.check_owner(event_obj, current_user)
    event_task.delete_task(task, db)
    return None