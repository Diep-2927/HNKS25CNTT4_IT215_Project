from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from db.database import get_db
from dependencies.auth import get_current_active_user
from models import User
from schemas.event import EventCreate, EventResponse, EventUpdate
from schemas.event_staff import EventStaffCreate, EventStaffResponse
from services import event_service, event_member_service

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(data: EventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return event_service.create_event(data, current_user, db)


@router.get("/", response_model=List[EventResponse])
def list_events(search: Optional[str] = Query(None, max_length=255), db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return event_service.list_events(search, current_user, db)


@router.get("/{event_id}", response_model=EventResponse)
def get_event_detail(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    event = event_service.get_event(event_id, db)
    event_service.check_member(event, current_user, db)
    return event


@router.patch("/{event_id}", response_model=EventResponse)
def update_event(event_id: int, data: EventUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    event = event_service.get_event(event_id, db)
    event_service.check_owner(event, current_user)
    return event_service.update_event(event, data, db)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    event = event_service.get_event(event_id, db)
    event_service.check_owner(event, current_user)
    event_service.delete_event(event, db)
    return None


@router.post("/{event_id}/members", response_model=EventStaffResponse, status_code=status.HTTP_201_CREATED)
def add_member(event_id: int, data: EventStaffCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    event = event_service.get_event(event_id, db)
    event_service.check_owner(event, current_user)
    return event_member_service.add_member(event, data, db)


@router.get("/{event_id}/members", response_model=List[EventStaffResponse])
def list_members(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    event = event_service.get_event(event_id, db)
    event_service.check_member(event, current_user, db)
    return event_member_service.list_members(event.id, db)


@router.delete("/{event_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(event_id: int, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    event = event_service.get_event(event_id, db)
    event_service.check_owner(event, current_user)
    event_member_service.remove_member(event, user_id, db)
    return None