from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Event, EventStaff, EventTask, User, TaskStatus, TaskPriority


def get_task(task_id: int, db: Session):
    task = db.query(EventTask).filter(EventTask.id == task_id).first()

    if task is None:
        raise HTTPException(status_code=404, detail="Công việc không tồn tại")

    return task


def check_assignee(event_id: int, user_id: int, db: Session):
    member = db.query(EventStaff).filter(EventStaff.event_id == event_id, EventStaff.user_id == user_id).first()

    if member is None:
        raise HTTPException(status_code=400, detail="Người được giao phải là thành viên của sự kiện")

    user = db.query(User).filter(User.id == user_id).first()

    if user is None or not user.is_active:
        raise HTTPException(status_code=400, detail="Người được giao không hoạt động")

    return member


def check_task_permission(task: EventTask, event: Event, user: User):
    if event.owner_id == user.id or task.assignee_id == user.id:
        return

    raise HTTPException(status_code=403, detail="Bạn không có quyền thực hiện thao tác này")


def create_task(event_id, data, db: Session):
    title = data.title.strip()

    if not title:
        raise HTTPException(status_code=400, detail="Tên công việc không được để trống")

    if data.assignee_id is not None:
        check_assignee(event_id, data.assignee_id, db)

    task = EventTask(event_id=event_id, title=title, description=data.description, priority=data.priority, due_date=data.due_date, assignee_id=data.assignee_id, status=TaskStatus.TODO)

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


def list_tasks(event_id, search, task_status, priority, assignee_id, page, size, sort_by, sort_order, db: Session):
    query = db.query(EventTask).filter(EventTask.event_id == event_id)

    if search:
        query = query.filter(EventTask.title.ilike("%" + search.strip() + "%"))

    if task_status:
        query = query.filter(EventTask.status == task_status)

    if priority:
        query = query.filter(EventTask.priority == priority)

    if assignee_id:
        query = query.filter(EventTask.assignee_id == assignee_id)

    order_column = EventTask.due_date if sort_by == "due_date" else EventTask.created_at

    if sort_order.lower() == "asc":
        query = query.order_by(order_column.asc())
    else:
        query = query.order_by(order_column.desc())

    skip = (page - 1) * size

    return query.offset(skip).limit(size).all()


def update_task(task, event, data, db: Session):
    update_data = data.model_dump(exclude_unset=True)

    if "title" in update_data:
        title = update_data["title"].strip()

        if not title:
            raise HTTPException(status_code=400, detail="Tên công việc không được để trống")

        update_data["title"] = title

    if update_data.get("assignee_id") is not None:
        check_assignee(event.id, update_data["assignee_id"], db)

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return task


def delete_task(task, db: Session):
    db.delete(task)
    db.commit()