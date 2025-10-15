"""
CRUD utilities for Event model.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import select, or_, and_
from sqlalchemy.orm import Session

from src.db.models import Event, EventStatus
from src.db.schemas import EventCreate, EventUpdate


# PUBLIC_INTERFACE
def list_events(
    db: Session,
    *,
    q: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Event]:
    """
    List events with optional filtering.

    Args:
        db: SQLAlchemy Session
        q: Full-text like filter on title/description/location (case-insensitive)
        status: 'draft' or 'published'
        date_from: Filter events with start_time >= date_from
        date_to: Filter events with end_time <= date_to
        skip: Offset for pagination
        limit: Limit for pagination

    Returns:
        List of Event ORM instances.
    """
    stmt = select(Event)

    conditions: list = []
    if q:
        pattern = f"%{q}%"
        conditions.append(
            or_(
                Event.title.ilike(pattern),
                Event.description.ilike(pattern),
                Event.location.ilike(pattern),
                Event.tags.ilike(pattern),
            )
        )
    if status in ("draft", "published"):
        conditions.append(Event.status == EventStatus(status))
    if date_from:
        conditions.append(Event.start_time >= date_from)
    if date_to:
        conditions.append(Event.end_time <= date_to)

    if conditions:
        stmt = stmt.where(and_(*conditions))

    stmt = stmt.order_by(Event.start_time.asc()).offset(max(0, skip)).limit(max(1, limit))
    return list(db.execute(stmt).scalars().all())


# PUBLIC_INTERFACE
def get_event(db: Session, event_id: int) -> Optional[Event]:
    """
    Retrieve a single event by ID.
    """
    return db.get(Event, event_id)


# PUBLIC_INTERFACE
def create_event(db: Session, data: EventCreate) -> Event:
    """
    Create a new event.
    """
    obj = Event(
        title=data.title,
        description=data.description,
        start_time=data.start_time,
        end_time=data.end_time,
        location=data.location,
        capacity=data.capacity,
        status=EventStatus(data.status),
        tags=data.tags,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# PUBLIC_INTERFACE
def update_event(db: Session, event_id: int, data: EventUpdate) -> Optional[Event]:
    """
    Update an existing event by ID. Returns the updated event or None if not found.
    """
    obj = db.get(Event, event_id)
    if not obj:
        return None

    # Update only provided fields
    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "status" and value is not None:
            setattr(obj, field, EventStatus(value))
        else:
            setattr(obj, field, value)

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# PUBLIC_INTERFACE
def delete_event(db: Session, event_id: int) -> bool:
    """
    Delete an event by ID.

    Returns:
        True if a row was deleted, False otherwise.
    """
    obj = db.get(Event, event_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
