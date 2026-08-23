import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRole), default=UserRole.USER)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    
    events_owned = relationship("Event", back_populates="owner", foreign_keys="Event.owner_id")
    events_involved = relationship("EventStaff", back_populates="user")
    tasks_assigned = relationship("EventTask",back_populates="assignee")