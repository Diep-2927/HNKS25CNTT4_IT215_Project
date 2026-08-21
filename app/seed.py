from db.database import SessionLocal
from models import User, Event, EventTask, EventStaff, UserRole, TaskStatus, TaskPriority, EventStaffRole
from core.security import get_password_hash

def seed_data():
    db = SessionLocal()
    try:
        # Seed User
        user = db.query(User).filter(User.email == "admin@gmail.com").first()
        if not user:
            user = User(
                email="admin@gmail.com",
                hashed_password=get_password_hash("admin123"), 
                full_name="Quản trị viên",
                role=UserRole.ADMIN
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print("Seed thành công User.")

        # Seed Event
        event = db.query(Event).filter(Event.name == "Lễ kỷ niệm 5 năm").first()
        if not event:
            event = Event(
                name="Lễ kỷ niệm 5 năm",
                description="Kỷ niệm thành lập công ty",
                location="Hà Nội",
                owner_id=user.id
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            print("Seed thành công Event.")
            
            # Phân quyền cho User làm OWNER của Event
            staff = EventStaff(event_id=event.id, user_id=user.id, role=EventStaffRole.OWNER)
            db.add(staff)
            
            # Seed Event Task
            task = EventTask(
                event_id=event.id,
                title="Chuẩn bị hội trường",
                description="Liên hệ đặt phòng và setup thiết bị âm thanh",
                status=TaskStatus.TODO,
                priority=TaskPriority.HIGH,
                assignee_id=user.id
            )
            db.add(task)
            db.commit()
            print("Seed thành công Staff và Task.")
            
    except Exception as e:
        print("Lỗi seed dữ liệu:", e)
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()