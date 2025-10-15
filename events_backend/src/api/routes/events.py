from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.db import crud
from src.db.session import get_db
from src.db.schemas import EventCreate, EventOut, EventUpdate

router = APIRouter(
    prefix="/events",
    tags=["Events"],
    responses={404: {"description": "Not found"}},
)


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[EventOut],
    summary="List events",
    description=(
        "Retrieve a list of events with optional filtering and pagination.\n\n"
        "Filters:\n"
        "- status: draft|published\n"
        "- from: ISO datetime; events starting at or after this time\n"
        "- to: ISO datetime; events ending at or before this time\n"
        "- q: substring match on title, description, location, tags (case-insensitive)\n"
        "Pagination via skip and limit."
    ),
    responses={
        200: {"description": "List of events"},
        422: {"description": "Validation error"},
    },
)
def list_events(
    db: Session = Depends(get_db),
    status: Optional[str] = Query(
        None,
        pattern="^(draft|published)$",
        description="Filter by event status",
        alias="status",
    ),
    from_: Optional[datetime] = Query(
        None,
        description="Filter events with start_time >= this ISO datetime",
        alias="from",
    ),
    to: Optional[datetime] = Query(
        None,
        description="Filter events with end_time <= this ISO datetime",
        alias="to",
    ),
    q: Optional[str] = Query(
        None,
        description="Free-text query on title, description, location, or tags",
    ),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=500, description="Pagination limit"),
) -> List[EventOut]:
    """
    List events with optional filters and pagination.
    """
    items = crud.list_events(
        db,
        q=q,
        status=status,
        date_from=from_,
        date_to=to,
        skip=skip,
        limit=limit,
    )
    return items


# PUBLIC_INTERFACE
@router.get(
    "/{event_id}",
    response_model=EventOut,
    summary="Get event by ID",
    description="Retrieve a single event by its identifier.",
    responses={
        200: {"description": "Event found"},
        404: {"description": "Event not found"},
    },
)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
) -> EventOut:
    """
    Get one event by ID.
    """
    obj = crud.get_event(db, event_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return obj


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=EventOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create event",
    description="Create a new event.",
    responses={
        201: {"description": "Event created"},
        422: {"description": "Validation error"},
    },
)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
) -> EventOut:
    """
    Create a new event.
    """
    obj = crud.create_event(db, payload)
    return obj


# PUBLIC_INTERFACE
@router.put(
    "/{event_id}",
    response_model=EventOut,
    summary="Update event",
    description="Update an existing event by ID.",
    responses={
        200: {"description": "Event updated"},
        404: {"description": "Event not found"},
        422: {"description": "Validation error"},
    },
)
def update_event(
    event_id: int,
    payload: EventUpdate,
    db: Session = Depends(get_db),
) -> EventOut:
    """
    Update an event by ID.
    """
    updated = crud.update_event(db, event_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return updated


# PUBLIC_INTERFACE
@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete event",
    description="Delete an existing event by ID.",
    responses={
        204: {"description": "Event deleted"},
        404: {"description": "Event not found"},
    },
)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
) -> None:
    """
    Delete an event by ID.
    """
    ok = crud.delete_event(db, event_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    # 204 No Content
    return None
