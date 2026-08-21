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
    event_id = Column(Integer, ForeignKey("events.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(Enum(EventStaffRole), default=EventStaffRole.MEMBER)
    joined_at = Column(DateTime, default=datetime.now, nullable=False)

    event = relationship("Event", back_populates="staffs")
    user = relationship("User", back_populates="events_involved")