from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    location = Column(String(255))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # Cơ chế Soft Delete (Xóa mềm - ẩn khỏi query mà không xóa vật lý khỏi database)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    # Quan hệ ORM
    owner = relationship("User", back_populates="events_owned", foreign_keys=[owner_id])
    staffs = relationship("EventStaff", back_populates="event")
    tasks = relationship("EventTask", back_populates="event")