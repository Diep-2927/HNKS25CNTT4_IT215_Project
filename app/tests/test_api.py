import sys
from pathlib import Path

# Đảm bảo nhận diện thư mục app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from db.database import Base, get_db
from main import app

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:29012007@localhost:3306/event_management_db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=engine)
client = TestClient(app)

@pytest.fixture(scope="module")
def auth_tokens():
    # 1. Đăng ký Admin & Users
    client.post("/auth/register", json={"email": "admin@test.com", "full_name": "Admin Test", "password": "password123"})
    client.post("/auth/register", json={"email": "user1@test.com", "full_name": "User One", "password": "password123"})
    client.post("/auth/register", json={"email": "user2@test.com", "full_name": "User Two", "password": "password123"})

    # Cập nhật quyền Admin trực tiếp trong DB test
    db = TestingSessionLocal()
    from models.user import User, UserRole
    admin_user = db.query(User).filter(User.email == "admin@test.com").first()
    admin_user.role = UserRole.ADMIN
    db.commit()
    db.close()

    # 2. Login lấy access token
    t_admin = client.post("/auth/login", json={"email": "admin@test.com", "password": "password123"}).json()["access_token"]
    t_user1 = client.post("/auth/login", json={"email": "user1@test.com", "password": "password123"}).json()["access_token"]
    t_user2 = client.post("/auth/login", json={"email": "user2@test.com", "password": "password123"}).json()["access_token"]

    return {"admin": t_admin, "user1": t_user1, "user2": t_user2}


def test_auth_workflow(auth_tokens):
    # Test Register trùng email
    res = client.post("/auth/register", json={"email": "user1@test.com", "full_name": "Duplicate", "password": "password123"})
    assert res.status_code == 400

    # Test lấy profile cá nhân
    res = client.get("/users/me", headers={"Authorization": f"Bearer {auth_tokens['user1']}"})
    assert res.status_code == 200
    assert res.json()["email"] == "user1@test.com"

    # Test User thường không được xem danh sách users
    res = client.get("/users", headers={"Authorization": f"Bearer {auth_tokens['user1']}"})
    assert res.status_code == 403

    # Test Admin xem được danh sách users
    res = client.get("/users", headers={"Authorization": f"Bearer {auth_tokens['admin']}"})
    assert res.status_code == 200
    assert len(res.json()) >= 3


def test_event_and_task_lifecycle(auth_tokens):
    h_user1 = {"Authorization": f"Bearer {auth_tokens['user1']}"}
    h_user2 = {"Authorization": f"Bearer {auth_tokens['user2']}"}

    # 1. User1 tạo Event
    res_event = client.post("/events/", json={"name": "Hội nghị Công nghệ 2026", "location": "Hà Nội"}, headers=h_user1)
    assert res_event.status_code == 201
    event_id = res_event.json()["id"]

    # 2. User2 chưa tham gia -> Không xem được chi tiết (403)
    res_forbidden = client.get(f"/events/{event_id}", headers=h_user2)
    assert res_forbidden.status_code == 403

    # 3. User1 thêm User2 làm Member
    user2_id = client.get("/users/me", headers=h_user2).json()["id"]
    res_add = client.post(f"/events/{event_id}/members", json={"user_id": user2_id, "role": "MEMBER"}, headers=h_user1)
    assert res_add.status_code == 201

    # 4. User2 đã là Member -> Xem được event
    res_view = client.get(f"/events/{event_id}", headers=h_user2)
    assert res_view.status_code == 200

    # 5. Tạo task và gán cho User2
    res_task = client.post(
        f"/events/{event_id}/event-tasks",
        json={"title": "Thiết kế Banner", "priority": "HIGH", "assignee_id": user2_id},
        headers=h_user1
    )
    assert res_task.status_code == 201
    task_id = res_task.json()["id"]

    # 6. User2 (Assignee) đổi status sang DONE
    res_update_status = client.patch(f"/event-tasks/{task_id}", json={"status": "DONE"}, headers=h_user2)
    assert res_update_status.status_code == 200
    assert res_update_status.json()["status"] == "DONE"

    # 7. User2 không phải Owner cố tình đổi assignee -> 403
    res_unauth_reassign = client.patch(f"/event-tasks/{task_id}", json={"assignee_id": None}, headers=h_user2)
    assert res_unauth_reassign.status_code == 403

    # 8. User1 (Owner) xóa Task -> 204
    res_delete_task = client.delete(f"/event-tasks/{task_id}", headers=h_user1)
    assert res_delete_task.status_code == 204

    # 9. User1 xóa Event -> 204
    res_delete_event = client.delete(f"/events/{event_id}", headers=h_user1)
    assert res_delete_event.status_code == 204