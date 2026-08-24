from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from db.database import Base

class EventStaffRole(str, enum.Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"


class Event(Base):
    __tablename__ = "events"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    name = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    location = Column(
        String(255),
        nullable=True
    )

    start_date = Column(
        DateTime,
        nullable=True
    )

    end_date = Column(
        DateTime,
        nullable=True
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False
    )

    deleted_at = Column(
        DateTime,
        nullable=True
    )

    owner = relationship(
        "User",
        foreign_keys=[owner_id]
    )

    staff_members = relationship(
        "EventStaff",
        back_populates="event",
        cascade="all, delete-orphan"
    )

    tasks = relationship(
        "EventTask",
        back_populates="event",
        cascade="all, delete-orphan"
    )


class EventStaff(Base):
    __tablename__ = "event_staffs"

    __table_args__ = (
        UniqueConstraint(
            "event_id",
            "user_id",
            name="uq_event_staff_event_user"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    event_id = Column(
        Integer,
        ForeignKey("events.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    role = Column(
        Enum(EventStaffRole),
        nullable=False,
        default=EventStaffRole.MEMBER
    )

    joined_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    event = relationship(
        "Event",
        back_populates="staff_members"
    )

    user = relationship(
        "User"
    )