from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    location = Column(String(255))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True, default=None)

    owner = relationship("User", foreign_keys=[owner_id])
    staffs = relationship("EventStaff", back_populates="event")
    tasks = relationship("EventTask", back_populates="event")
    owner = relationship("User", back_populates="events_owned", foreign_keys=[owner_id])