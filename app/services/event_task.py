from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import Event, EventStaff, EventTask, User, TaskStatus, TaskPriority


def get_task(task_id: int, db: Session):
    """
    Lấy task theo ID.
    """
    task = (
        db.query(EventTask)
        .filter(EventTask.id == task_id)
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Công việc không tồn tại"
        )

    return task


def check_assignee(
    event_id: int,
    user_id: int,
    db: Session
):
    """
    Kiểm tra người được giao task:
    - Phải tồn tại trong EventStaff.
    - Phải là tài khoản đang hoạt động.
    """

    member = (
        db.query(EventStaff)
        .filter(
            EventStaff.event_id == event_id,
            EventStaff.user_id == user_id
        )
        .first()
    )

    if member is None:
        raise HTTPException(
            status_code=400,
            detail="Người được giao phải là thành viên của sự kiện"
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Người được giao không hoạt động"
        )

    return member


def check_task_permission(
    task: EventTask,
    event: Event,
    user: User
):
    """
    Quyền cập nhật task:
    - OWNER của event
    - Người được giao task
    """

    if event.owner_id == user.id:
        return

    if task.assignee_id == user.id:
        return

    raise HTTPException(
        status_code=403,
        detail="Bạn không có quyền thực hiện thao tác này"
    )


def create_task(
    event_id: int,
    data,
    db: Session
):
    """
    Tạo task mới.
    """

    title = data.title.strip()

    if not title:
        raise HTTPException(
            status_code=400,
            detail="Tên công việc không được để trống"
        )

    # Nếu có assignee thì phải là member của event
    if data.assignee_id is not None:
        check_assignee(
            event_id,
            data.assignee_id,
            db
        )

    task = EventTask(
        event_id=event_id,
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


def list_tasks(
    event_id: int,
    search,
    task_status,
    priority,
    assignee_id,
    page: int,
    size: int,
    sort_by: str,
    sort_order: str,
    db: Session
):
    """
    Danh sách task:
    - Search theo title
    - Filter status
    - Filter priority
    - Filter assignee
    - Pagination
    - Sort created_at / due_date
    """

    query = (
        db.query(EventTask)
        .filter(EventTask.event_id == event_id)
    )

    # SEARCH

    if search:
        search = search.strip()

        if search:
            query = query.filter(
                EventTask.title.ilike(
                    f"%{search}%"
                )
            )

    # FILTER STATUS

    if task_status is not None:
        query = query.filter(
            EventTask.status == task_status
        )

    # FILTER PRIORITY

    if priority is not None:
        query = query.filter(
            EventTask.priority == priority
        )

    # FILTER ASSIGNEE

    if assignee_id is not None:
        query = query.filter(
            EventTask.assignee_id == assignee_id
        )

    # VALIDATE SORT

    allowed_sort_fields = {
        "created_at": EventTask.created_at,
        "due_date": EventTask.due_date,
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=400,
            detail="sort_by phải là created_at hoặc due_date"
        )

    sort_order = sort_order.lower()

    if sort_order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="sort_order phải là asc hoặc desc"
        )

    # SORT

    sort_column = allowed_sort_fields[sort_by]

    if sort_order == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    # PAGINATION

    skip = (page - 1) * size

    return (
        query
        .offset(skip)
        .limit(size)
        .all()
    )


def update_task(
    task: EventTask,
    event: Event,
    data,
    db: Session
):
    """
    Cập nhật task.
    Chỉ cập nhật field được gửi lên.
    """

    update_data = data.model_dump(
        exclude_unset=True
    )

    # TITLE

    if "title" in update_data:

        title = update_data["title"]

        if title is None:
            raise HTTPException(
                status_code=400,
                detail="Tên công việc không được để trống"
            )

        title = title.strip()

        if not title:
            raise HTTPException(
                status_code=400,
                detail="Tên công việc không được để trống"
            )

        update_data["title"] = title

    # ASSIGNEE

    if "assignee_id" in update_data:

        new_assignee_id = update_data["assignee_id"]

        # Cho phép null để bỏ người được giao
        if new_assignee_id is not None:
            check_assignee(
                event.id,
                new_assignee_id,
                db
            )

    # UPDATE

    for field, value in update_data.items():
        setattr(
            task,
            field,
            value
        )

    db.commit()
    db.refresh(task)

    return task


def delete_task(
    task: EventTask,
    db: Session
):
    """
    Xóa task.
    """

    db.delete(task)
    db.commit()