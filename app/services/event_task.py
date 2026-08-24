from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models import Event, EventStaff, EventTask, TaskPriority, TaskStatus, User
from schemas.event_task import EventTaskCreate, EventTaskUpdate

def get_task(task_id: int, db: Session) -> EventTask:
    """Lấy task theo ID."""
    task = db.query(EventTask).filter(EventTask.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Công việc không tồn tại")
    return task

def check_assignee(event_id: int, user_id: int, db: Session) -> EventStaff:
    """Kiểm tra người được giao task: tồn tại trong EventStaff và đang hoạt động."""
    member = db.query(EventStaff).filter(EventStaff.event_id == event_id, EventStaff.user_id == user_id).first()
    if member is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Người được giao phải là thành viên của sự kiện")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Người được giao không hoạt động")
    return member

def check_task_permission(task: EventTask, event: Event, user: User) -> None:
    """Quyền cập nhật task: OWNER của event hoặc người được giao task."""
    if event.owner_id == user.id or task.assignee_id == user.id:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền thực hiện thao tác này")

def create_task(event_id: int, data: EventTaskCreate, db: Session) -> EventTask:
    """Tạo task mới."""
    title = data.title.strip()
    if not title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tên công việc không được để trống")

    if data.assignee_id is not None:
        check_assignee(event_id, data.assignee_id, db)

    task = EventTask(
        event_id=event_id,
        title=title,
        description=data.description,
        priority=data.priority,
        due_date=data.due_date,
        assignee_id=data.assignee_id,
        status=TaskStatus.TODO,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def list_tasks(event_id: int, search: str | None, task_status: TaskStatus | None, priority: TaskPriority | None, assignee_id: int | None, page: int, size: int, sort_by: str, sort_order: str, db: Session) -> list[EventTask]:
    """Danh sách task với các bộ lọc, sắp xếp và phân trang."""
    query = db.query(EventTask).filter(EventTask.event_id == event_id)

    if search and search.strip():
        query = query.filter(EventTask.title.ilike(f"%{search.strip()}%"))
    if task_status is not None:
        query = query.filter(EventTask.status == task_status)
    if priority is not None:
        query = query.filter(EventTask.priority == priority)
    if assignee_id is not None:
        query = query.filter(EventTask.assignee_id == assignee_id)

    allowed_sort_fields = {"created_at": EventTask.created_at, "due_date": EventTask.due_date}
    if sort_by not in allowed_sort_fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="sort_by phải là created_at hoặc due_date")

    sort_order = sort_order.lower()
    if sort_order not in ["asc", "desc"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="sort_order phải là asc hoặc desc")

    sort_column = allowed_sort_fields[sort_by]
    query = query.order_by(sort_column.asc() if sort_order == "asc" else sort_column.desc())

    return query.offset((page - 1) * size).limit(size).all()

def update_task(task: EventTask, event: Event, data: EventTaskUpdate, current_user: User, db: Session):
    is_owner = event.owner_id == current_user.id
    is_assignee = task.assignee_id == current_user.id

    if not is_owner and not is_assignee:
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền cập nhật task này"
        )

    update_data = data.model_dump(exclude_unset=True)

    if "title" in update_data:
        title = update_data["title"]

        if title is None or not title.strip():
            raise HTTPException(
                status_code=400,
                detail="Tên công việc không được để trống"
            )

        update_data["title"] = title.strip()

    if "assignee_id" in update_data:
        if not is_owner:
            raise HTTPException(
                status_code=403,
                detail="Chỉ OWNER mới có quyền thay đổi người được giao"
            )

        if update_data["assignee_id"] is not None:
            check_assignee(
                event.id,
                update_data["assignee_id"],
                db
            )

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task

def delete_task(task: EventTask, db: Session) -> None:
    """Xóa task."""
    db.delete(task)
    db.commit()