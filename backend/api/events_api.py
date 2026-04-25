from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Event, Ticket

router = APIRouter(prefix="/api", tags=["API"])


@router.get("/events")
def get_events(db: Session = Depends(get_db)):

    events = db.query(Event).all()

    return [
        {
            "id": e.id,
            "title": e.title,
            "location": e.location,
            "price": e.price,
            "date": e.date
        }
        for e in events
    ]


@router.get("/events/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db)):

    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        return {"error": "Event not found"}

    return {
        "id": event.id,
        "title": event.title,
        "location": event.location,
        "price": event.price,
        "date": event.date
    }


@router.get("/tickets/{user_id}")
def get_user_tickets(user_id: int, db: Session = Depends(get_db)):

    tickets = db.query(Ticket).filter(
        Ticket.user_id == user_id
    ).all()

    return tickets


