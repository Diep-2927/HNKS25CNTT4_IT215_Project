from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import EventStaff, EventStaffRole, User, EventTask

def add_member(event, data, db: Session):
    """
    Thêm thành viên vào sự kiện:
    - Kiểm tra không thêm OWNER trùng lặp.
    - Không cấp role OWNER thủ công qua API thêm member.
    - Kiểm tra user tồn tại, đang hoạt động (is_active) và chưa từng tham gia sự kiện.
    """
    if data.user_id == event.owner_id:
        raise HTTPException(status_code=400, detail="Owner đã là thành viên của sự kiện")

    if data.role == EventStaffRole.OWNER:
        raise HTTPException(status_code=400, detail="Không thể thêm thành viên với role OWNER")

    user = db.query(User).filter(User.id == data.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User không tồn tại")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Không thể thêm tài khoản đang bị khóa")

    existing_member = db.query(EventStaff).filter(
        EventStaff.event_id == event.id,
        EventStaff.user_id == user.id
    ).first()

    if existing_member:
        raise HTTPException(status_code=400, detail="User đã là thành viên của sự kiện")

    member = EventStaff(event_id=event.id, user_id=user.id, role=EventStaffRole.MEMBER)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member

def list_members(event_id, db: Session):
    return db.query(EventStaff).filter(EventStaff.event_id == event_id).order_by(EventStaff.joined_at).all()

def remove_member(event, user_id, db: Session):
    """Xóa thành viên khỏi sự kiện (Bảo vệ: Tuyệt đối không xóa OWNER khỏi sự kiện)"""
    member = db.query(EventStaff).filter(
        EventStaff.event_id == event.id,
        EventStaff.user_id == user_id
    ).first()

    if member is None:
        raise HTTPException(status_code=404, detail="User không phải thành viên của sự kiện")

    if member.role == EventStaffRole.OWNER:
        raise HTTPException(status_code=400, detail="Không thể xóa OWNER khỏi sự kiện")

    # Tìm các task đang giao cho member bị xóa
    tasks = db.query(EventTask).filter(
        EventTask.event_id == event.id, 
        EventTask.assignee_id == user_id
    ).all()

    # Bỏ assignee
    for task in tasks:
        task.assignee_id = None

    # Sau đó mới xóa member
    db.delete(member)
    db.commit()