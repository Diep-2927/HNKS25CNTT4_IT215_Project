from datetime import datetime
import enum
from sqlalchemy import Column,Integer,ForeignKey,DateTime,Enum
from sqlalchemy.orm import relationship
from db.database import Base

class EventStaffRole(str, enum.Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"

class EventStaff(Base):
    __tablename__ = "event_staffs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(EventStaffRole), default=EventStaffRole.MEMBER, nullable=False)
    joined_at = Column(DateTime, default=datetime.now)
    # Quan hệ với Event
    event = relationship("Event", back_populates="staffs")
    # Quan hệ với User
    user = relationship("User", back_populates="events_involved")