from datetime import datetime
import enum
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from db.database import Base

class EventStaffRole(str, enum.Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"

class EventStaff(Base):
    __tablename__ = "event_staffs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(EventStaffRole), default=EventStaffRole.MEMBER, nullable=False)
    joined_at = Column(DateTime, default=datetime.now)
    
    event = relationship("Event", back_populates="staffs")
    user = relationship("User", back_populates="events_involved")