from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.routers import event
from db.database import get_db
from dependencies.auth import get_current_active_user
from models import Event, EventStaff, EventTask, User, TaskStatus, TaskPriority
from schemas.event_task import EventTaskCreate, EventTaskUpdate, EventTaskResponse

router = APIRouter(prefix="/events", tags=["Event Tasks"])


# Tìm Event
def get_event(event_id: int, db: Session):
    event = db.query(Event).filter(Event.id == event_id, Event.is_deleted == False).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Sự kiện không tồn tại")
    return event


# Tìm thành viên
def get_member(event_id: int, user_id: int, db: Session):
    return db.query(EventStaff).filter(EventStaff.event_id == event_id, EventStaff.user_id == user_id).first()


# Kiểm tra User có phải thành viên Event không
def check_member(event: Event, user: User, db: Session):
    member = get_member(event.id, user.id, db)
    if member is None:
        raise HTTPException(status_code=403, detail="Bạn không phải thành viên của sự kiện")
    return member


# Kiểm tra Owner
def check_owner(event: Event, user: User):
    if event.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Chỉ OWNER mới có quyền thực hiện thao tác này")


# Tìm Task
def get_task(task_id: int, db: Session):
    task = db.query(EventTask).filter(EventTask.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Công việc không tồn tại")
    return task


# Kiểm tra người được giao có phải thành viên Event
def check_assignee(event_id: int, user_id: int, db: Session):
    member = get_member(event_id, user_id, db)
    if member is None:
        raise HTTPException(status_code=400, detail="Người được giao phải là thành viên của sự kiện")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=400, detail="Người được giao không hoạt động")
    return member


# Kiểm tra quyền cập nhật Task
def check_task_permission(task: EventTask, event: Event, user: User):
    if event.owner_id == user.id or task.assignee_id == user.id:
        return
    raise HTTPException(status_code=403, detail="Bạn không có quyền thực hiện thao tác này")


# TẠO TASK
@router.post("/{event_id}/event-tasks", response_model=EventTaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(event_id: int, data: EventTaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    event = get_event(event_id, db)
    check_member(event, current_user, db)

    title = data.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Tên công việc không được để trống")

    if data.assignee_id is not None:
        check_assignee(event.id, data.assignee_id, db)

    task = EventTask(
        event_id=event.id,
        title=title,
        description=data.description,
        priority=data.priority,
        due_date=data.due_date,
        assignee_id=data.assignee_id,
        status=TaskStatus.TODO
    )

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


# DANH SÁCH TASK
@router.get("/{event_id}/event-tasks", response_model=List[EventTaskResponse])
def list_tasks(event_id: int, search: Optional[str] = Query(None, max_length=255), task_status: Optional[TaskStatus] = Query(None, alias="status"), priority: Optional[TaskPriority] = None, assignee_id: Optional[int] = None, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100), sort_by: str = Query("created_at"), sort_order: str = Query("desc"), db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    event = get_event(event_id, db)
    check_member(event, current_user, db)

    query = db.query(EventTask).filter(EventTask.event_id == event.id)

    # Search theo tên Task
    if search:
        query = query.filter(EventTask.title.ilike("%" + search.strip() + "%"))

    # Filter Status
    if task_status:
        query = query.filter(EventTask.status == task_status)

    # Filter Priority
    if priority:
        query = query.filter(EventTask.priority == priority)

    # Filter Assignee
    if assignee_id:
        query = query.filter(EventTask.assignee_id == assignee_id)

    # Sort
    order_column = EventTask.due_date if sort_by == "due_date" else EventTask.created_at
    query = query.order_by(order_column.asc() if sort_order.lower() == "asc" else order_column.desc())

    # Pagination
    skip = (page - 1) * size
    return query.offset(skip).limit(size).all()


# CHI TIẾT TASK
@router.get("/event-tasks/{task_id}", response_model=EventTaskResponse)
def get_task_detail(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    task = get_task(task_id, db)
    event = get_event(task.event_id, db)
    check_member(event, current_user, db)
    return task


# CẬP NHẬT TASK
@router.patch("/event-tasks/{task_id}", response_model=EventTaskResponse)
def update_task(task_id: int, data: EventTaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    task = get_task(task_id, db)
    event = get_event(task.event_id, db)
    check_task_permission(task, event, current_user)

    update_data = data.model_dump(exclude_unset=True)

    # Kiểm tra tên Task
    if "title" in update_data:
        title = update_data["title"].strip()
        if not title:
            raise HTTPException(status_code=400, detail="Tên công việc không được để trống")
        update_data["title"] = title

    # Kiểm tra Assignee
    if update_data.get("assignee_id") is not None:
        check_assignee(event.id, update_data["assignee_id"], db)

    # Cập nhật
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


# XÓA TASK
@router.delete("/event-tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    task = get_task(task_id, db)
    event = get_event(task.event_id, db)
    check_owner(event, current_user)

    db.delete(task)
    db.commit()
    return None