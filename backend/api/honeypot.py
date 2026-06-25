from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models import HoneypotEvent

router = APIRouter(prefix="/honeypot", tags=["honeypot"])


@router.get("/events", response_model=List[HoneypotEvent])
def list_honeypot_events(session: Session = Depends(get_session)):
    """List all honeypot events."""
    return session.exec(
        select(HoneypotEvent).order_by(HoneypotEvent.timestamp.desc())
    ).all()


@router.get("/events/{event_id}", response_model=HoneypotEvent)
def get_honeypot_event(event_id: int, session: Session = Depends(get_session)):
    """Get a specific honeypot event by ID."""
    event = session.get(HoneypotEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Honeypot event not found")
    return event


@router.post("/events", response_model=HoneypotEvent)
def create_honeypot_event(
    event: HoneypotEvent, session: Session = Depends(get_session)
):
    """Log a new honeypot event."""
    session.add(event)
    session.commit()
    session.refresh(event)
    return event
