from fastapi import APIRouter, Request, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Event, Ticket, User, Payment

from backend.services.ticket_services import TicketService
from backend.services.email_services import EmailService
from backend.services.payment_service import PaymentService

from backend.core.config import settings


router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Initialize services
ticket_service = TicketService()
email_service = EmailService()
payment_service = PaymentService()


# EVENT LISTING
@router.get("/events")
def event_listing(request: Request, db: Session = Depends(get_db)):
    events = db.query(Event).all()
    user_id = request.cookies.get("user_id")

    return templates.TemplateResponse("event-listing.html", {
        "request": request,
        "events": events,
        "user_id": user_id
    })


# EVENT DETAIL
@router.get("/events/{event_id}")
def event_detail(request: Request, event_id: int, db: Session = Depends(get_db)):

    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        return RedirectResponse("/events", status_code=303)

    user_id = request.cookies.get("user_id")

    booked_tickets = db.query(Ticket).filter(
        Ticket.event_id == event_id
    ).count()

    available_tickets = event.capacity - booked_tickets

    return templates.TemplateResponse("event-detail.html", {
        "request": request,
        "event": event,
        "user_id": user_id,
        "available_tickets": available_tickets
    })


# MY TICKETS
@router.get("/my-tickets")
def my_tickets(request: Request, db: Session = Depends(get_db)):

    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse("/", status_code=303)

    tickets = db.query(Ticket).filter(
        Ticket.user_id == int(user_id)
    ).all()

    return templates.TemplateResponse("my-tickets.html", {
        "request": request,
        "tickets": tickets
    })



# CREATE PAYMENT 
@router.post("/create-payment/{event_id}")
def create_payment(event_id: int, request: Request, db: Session = Depends(get_db)):

    user_id = request.cookies.get("user_id")

    if not user_id:
        return {"error": "Login required"}

    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        return {"error": "Event not found"}

    amount = int(event.price * 100)  # INR paisa

    order = payment_service.create_order(amount)

    return {
        "order_id": order["id"],
        "amount": order["amount"],
        "key": settings.RAZORPAY_KEY
    }



# VERIFY PAYMENT + CREATE TICKET
@router.post("/verify-payment/{event_id}")
async def verify_payment(
    event_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    data = await request.json()

    # Verify Razorpay signature
    try:
        payment_service.verify_signature(data)
    except Exception:
        return {"status": "Payment verification failed"}

    user_id = request.cookies.get("user_id")

    if not user_id:
        return {"status": "User not logged in"}

    user = db.query(User).filter(User.id == int(user_id)).first()
    event = db.query(Event).filter(Event.id == event_id).first()

    if not user or not event:
        return {"status": "Invalid user or event"}

    # Prevent duplicate payment processing
    existing_payment = db.query(Payment).filter(
        Payment.razorpay_payment_id == data["razorpay_payment_id"]
    ).first()

    if existing_payment:
        return {"status": "Already processed"}

    # Check capacity again (IMPORTANT)
    booked_tickets = db.query(Ticket).filter(
        Ticket.event_id == event_id
    ).count()

    if booked_tickets >= event.capacity:
        return {"status": "Event Full"}

    # Save payment
    payment = Payment(
        user_id=user.id,
        event_id=event.id,
        razorpay_payment_id=data["razorpay_payment_id"],
        razorpay_order_id=data["razorpay_order_id"],
        amount=event.price,
        status="success"
    )

    db.add(payment)
    db.commit()

    # Create ticket
    ticket = Ticket(
        event_id=event.id,
        user_id=user.id,
        user_name=user.name
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    # Generate ticket QR
    ticket_image = ticket_service.generate_ticket(
        ticket.id,
        event.title,
        event.date,
        event.location
    )

    ticket.ticket_image = ticket_image
    db.commit()

    # Send email (background)
    background_tasks.add_task(
        email_service.send_ticket_email,
        user.email,
        user.name,
        event.title,
        ticket_image
    )

    return {"status": "Payment verified"}