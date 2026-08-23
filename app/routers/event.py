from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from db.database import get_db
from dependencies.auth import get_current_active_user
from models import Event, EventStaff, EventStaffRole, User
from schemas.event import EventCreate, EventResponse, EventUpdate
from schemas.event_staff import EventStaffCreate, EventStaffResponse
from datetime import datetime

router = APIRouter(prefix="/events", tags=["Events"])

# HÀM TÌM EVENT
def get_event(event_id: int, db: Session):
    event = db.query(Event).filter(Event.id == event_id, Event.is_deleted == False).first()

    if event is None:
        raise HTTPException(status_code=404, detail="Sự kiện không tồn tại")

    return event


# HÀM TÌM MEMBER
def get_member(event_id: int, user_id: int, db: Session):
    member = db.query(EventStaff).filter(EventStaff.event_id == event_id, EventStaff.user_id == user_id).first()

    return member


# KIỂM TRA MEMBER
def check_member(event: Event, user: User, db: Session):
    member = get_member(event.id, user.id, db)

    if member is None:
        raise HTTPException(status_code=403, detail="Bạn không phải thành viên của sự kiện")

    return member


# KIỂM TRA OWNER
def check_owner(event: Event, user: User):
    if event.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Chỉ OWNER mới có quyền thực hiện thao tác này")


# 1. TẠO EVENT
@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(data: EventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):

    name = data.name.strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Tên sự kiện không được để trống"
        )

    # Kiểm tra ngày
    if data.start_date and data.end_date:
        if data.end_date < data.start_date:
            raise HTTPException(status_code=400, detail="Ngày kết thúc phải sau ngày bắt đầu")

    # Tạo event
    event = Event(
        name=name,
        description=data.description,
        location=data.location,
        start_date=data.start_date,
        end_date=data.end_date,
        owner_id=current_user.id
    )

    db.add(event)

    # Lưu tạm để lấy event.id
    db.flush()

    # Người tạo tự động trở thành OWNER
    owner = EventStaff(event_id=event.id, user_id=current_user.id, role=EventStaffRole.OWNER)

    db.add(owner)
    db.commit()
    db.refresh(event)

    return event


# 2. DANH SÁCH EVENT
@router.get("/", response_model=List[EventResponse])
def list_events(search: Optional[str] = Query(None, max_length=255), db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):

    # Lấy những event mà user tham gia
    query = db.query(Event).join(EventStaff,EventStaff.event_id == Event.id).filter(EventStaff.user_id == current_user.id,Event.is_deleted == False)

    # Tìm kiếm theo tên
    if search:
        search = search.strip()
        query = query.filter(Event.name.ilike("%" + search + "%"))

    # Event mới nhất lên trước
    events = query.order_by(Event.created_at.desc()).all()

    return events


# 3. XEM CHI TIẾT EVENT
@router.get("/{event_id}", response_model=EventResponse)
def get_event_detail(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):

    # Tìm event
    event = get_event(event_id, db)

    # Kiểm tra user có tham gia không
    check_member(event, current_user, db)

    return event


# 4. CẬP NHẬT EVENT
@router.patch("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):

    # Tìm event
    event = get_event(event_id, db)

    # Chỉ OWNER được sửa
    check_owner(event, current_user)

    # Lấy những dữ liệu được gửi lên
    update_data = data.model_dump(exclude_unset=True)

    # Lấy ngày mới hoặc ngày cũ
    start_date = update_data.get("start_date", event.start_date)
    end_date = update_data.get("end_date", event.end_date)

    # Kiểm tra ngày
    if start_date and end_date:
        if end_date < start_date:
            raise HTTPException(
                status_code=400,
                detail="Ngày kết thúc phải sau ngày bắt đầu"
            )

    # Cập nhật dữ liệu
    for field, value in update_data.items():

        if field == "name":
            value = value.strip()

            if not value:
                raise HTTPException(
                    status_code=400,
                    detail="Tên sự kiện không được để trống"
                )

        setattr(event, field, value)

    db.commit()
    db.refresh(event)

    return event


# 5. XÓA EVENT
@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    event = get_event(event_id, db)
    check_owner(event, current_user)
    event.is_deleted = True
    event.deleted_at = datetime.now()
    db.commit()
    return None


# 6. THÊM MEMBER
@router.post("/{event_id}/members", response_model=EventStaffResponse, status_code=status.HTTP_201_CREATED)
def add_member(event_id: int, data: EventStaffCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):

    # Tìm event
    event = get_event(event_id, db)

    # Chỉ OWNER được thêm
    check_owner(event, current_user)

    # Không được thêm OWNER
    if data.user_id == event.owner_id:
        raise HTTPException(status_code=400, detail="Owner đã là thành viên của sự kiện")

    # Không cho thêm role OWNER
    if data.role == EventStaffRole.OWNER:
        raise HTTPException(status_code=400, detail="Không thể thêm thành viên với role OWNER")

    # Tìm user
    user = db.query(User).filter(User.id == data.user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User không tồn tại")

    # Kiểm tra user active
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Không thể thêm tài khoản đang bị khóa")

    # Kiểm tra member đã tồn tại
    existing_member = get_member(event.id, user.id, db)

    if existing_member:
        raise HTTPException(status_code=400, detail="User đã là thành viên của sự kiện")

    # Tạo member
    member = EventStaff(event_id=event.id,user_id=user.id,role=EventStaffRole.MEMBER)

    db.add(member)
    db.commit()
    db.refresh(member)

    return member


# 7. DANH SÁCH MEMBER
@router.get("/{event_id}/members", response_model=List[EventStaffResponse])
def list_members(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):

    # Tìm event
    event = get_event(event_id, db)

    # User phải là member
    check_member(event, current_user, db)

    # Lấy danh sách member
    members = db.query(EventStaff).filter(EventStaff.event_id == event.id).order_by(EventStaff.joined_at).all()

    return members


# 8. XÓA MEMBER
@router.delete("/{event_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(event_id: int, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):

    # Tìm event
    event = get_event(event_id, db)

    # Chỉ OWNER được xóa
    check_owner(event, current_user)

    # Tìm member
    member = get_member(event.id, user_id, db)

    if member is None:
        raise HTTPException(status_code=404, detail="User không phải thành viên của sự kiện")

    # Không được xóa OWNER
    if member.role == EventStaffRole.OWNER:
        raise HTTPException(status_code=400, detail="Không thể xóa OWNER khỏi sự kiện")

    # Xóa member
    db.delete(member)
    db.commit()

    return None