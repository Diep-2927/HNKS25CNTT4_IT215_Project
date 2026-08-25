from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Event, EventStaff, EventStaffRole, User

def get_event(event_id: int, db: Session):
    """Lấy thông tin sự kiện và tự động lọc bỏ các sự kiện đã bị xóa mềm (is_deleted)"""
    event = db.query(Event).filter(Event.id == event_id, Event.is_deleted == False).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Sự kiện không tồn tại")
    return event

def get_member(event_id: int, user_id: int, db: Session):
    return db.query(EventStaff).filter(EventStaff.event_id == event_id, EventStaff.user_id == user_id).first()

def check_member(event: Event, user: User, db: Session):
    """Kiểm tra xem User có nằm trong danh sách thành viên sự kiện hay không"""
    member = get_member(event.id, user.id, db)
    if member is None:
        raise HTTPException(status_code=403, detail="Bạn không phải thành viên của sự kiện")
    return member

def check_owner(event: Event, user: User):
    """Kiểm tra quyền hạn tối cao: Chỉ cho phép người tạo (OWNER) sự kiện thực hiện"""
    if event.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Chỉ OWNER mới có quyền thực hiện thao tác này")

def create_event(data, current_user, db: Session):
    """
    Tạo sự kiện mới:
    1. Validate logic thời gian bắt đầu và kết thúc
    2. Tạo bản ghi Event
    """
    name = data.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Tên sự kiện không được để trống")

    if data.start_date and data.end_date and data.end_date < data.start_date:
        raise HTTPException(status_code=400, detail="Ngày kết thúc phải sau ngày bắt đầu")

    event = Event(
        name=name,
        description=data.description,
        location=data.location,
        start_date=data.start_date,
        end_date=data.end_date,
        owner_id=current_user.id
    )

    db.add(event)
    db.flush() 

    owner = EventStaff(event_id=event.id, user_id=current_user.id, role=EventStaffRole.OWNER)
    db.add(owner)
    db.commit()
    db.refresh(event)
    return event

def list_events(search, current_user, db: Session):
    """Lấy danh sách các sự kiện mà user hiện tại đang tham gia (JOIN EventStaff)"""
    query = db.query(Event).join(EventStaff, EventStaff.event_id == Event.id).filter(
        EventStaff.user_id == current_user.id,
        Event.is_deleted == False
    )

    if search:
        search = search.strip()
        query = query.filter(Event.name.ilike("%" + search + "%"))

    return query.order_by(Event.created_at.desc()).all()

def update_event(event, data, db: Session):
    """Cập nhật thông tin sự kiện, chỉ cập nhật các trường được truyền lên (exclude_unset)"""
    update_data = data.model_dump(exclude_unset=True)

    start_date = update_data.get("start_date", event.start_date)
    end_date = update_data.get("end_date", event.end_date)

    if start_date and end_date and end_date < start_date:
        raise HTTPException(status_code=400, detail="Ngày kết thúc phải sau ngày bắt đầu")

    for field, value in update_data.items():
        if field == "name":
            value = value.strip()
            if not value:
                raise HTTPException(status_code=400, detail="Tên sự kiện không được để trống")
        setattr(event, field, value)

    db.commit()
    db.refresh(event)
    return event

def delete_event(event, db: Session):
    """Thực hiện Soft Delete: Đánh dấu cờ is_deleted và lưu thời điểm xóa"""
    event.is_deleted = True
    event.deleted_at = datetime.now()
    db.commit()