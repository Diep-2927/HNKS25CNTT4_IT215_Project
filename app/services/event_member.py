from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import EventStaff, EventStaffRole, User


def add_member(event, data, db: Session):
    if data.user_id == event.owner_id:
        raise HTTPException(status_code=400, detail="Owner đã là thành viên của sự kiện")

    if data.role == EventStaffRole.OWNER:
        raise HTTPException(status_code=400, detail="Không thể thêm thành viên với role OWNER")

    user = db.query(User).filter(User.id == data.user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User không tồn tại")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Không thể thêm tài khoản đang bị khóa")

    existing_member = db.query(EventStaff).filter(EventStaff.event_id == event.id, EventStaff.user_id == user.id).first()

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
    member = db.query(EventStaff).filter(EventStaff.event_id == event.id, EventStaff.user_id == user_id).first()

    if member is None:
        raise HTTPException(status_code=404, detail="User không phải thành viên của sự kiện")

    if member.role == EventStaffRole.OWNER:
        raise HTTPException(status_code=400, detail="Không thể xóa OWNER khỏi sự kiện")

    db.delete(member)
    db.commit()