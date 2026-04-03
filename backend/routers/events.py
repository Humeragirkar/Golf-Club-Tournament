from fastapi import APIRouter, Request, Depends, BackgroundTasks
from backend.qr_util import generate_ticket_qr
from backend.email_util import send_ticket_email
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Event, Ticket, User
from fastapi.responses import RedirectResponse
from backend.payment_util import create_razorpay_order, client
from backend.models import Payment
import os


router = APIRouter()
templates = Jinja2Templates(directory="templates")


# Event Listing Page
@router.get("/events")
def event_listing(request: Request, db: Session = Depends(get_db)):

    events = db.query(Event).all()
    user_id = request.cookies.get("user_id")

    return templates.TemplateResponse(
        request,
        "event-listing.html",
        {
            "request": request,
            "events": events,
            "user_id": user_id
        }
    )


# Event Detail Page
@router.get("/events/{event_id}")
def event_detail(request: Request, event_id: int, db: Session = Depends(get_db)):

    event = db.query(Event).filter(Event.id == event_id).first()
    user_id = request.cookies.get("user_id")

    booked_tickets = db.query(Ticket).filter(
    Ticket.event_id == event_id
        ).count()

    available_tickets = event.capacity - booked_tickets

    return templates.TemplateResponse(
        request,
        "event-detail.html",
        {
            "request": request,
            "event": event,
            "user_id": user_id,
            "booked_tickets": booked_tickets,
            "available_tickets": available_tickets
        }
    )

@router.post("/book-ticket/{event_id}")
def book_ticket(event_id: int, request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):

    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse("/", status_code=303)

    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        return RedirectResponse("/", status_code=303)

    event = db.query(Event).filter(Event.id == event_id).first()

    # count booked tickets
    booked_tickets = db.query(Ticket).filter(
        Ticket.event_id == event_id
    ).count()

    # prevent booking if full
    if booked_tickets >= event.capacity:
        return RedirectResponse(f"/events/{event_id}?error=full", status_code=303)

    ticket = Ticket(
        event_id=event_id,
        user_id=user.id,
        user_name=user.name
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    ticket_image = generate_ticket_qr(
    ticket.id,
    event.title,
    event.date,
    event.location
    )

    ticket.ticket_image = ticket_image
    db.commit()

    background_tasks.add_task(
    send_ticket_email,
    user.email,
    user.name,
    event.title,
    ticket_image
    )
    
    return RedirectResponse("/my-tickets", status_code=303)

@router.get("/my-tickets")
def my_tickets(request: Request, db: Session = Depends(get_db)):

    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse("/", status_code=303)

    tickets = db.query(Ticket).filter(
        Ticket.user_id == int(user_id)
    ).all()

    
    return templates.TemplateResponse(
        request,
        "my-tickets.html",
        {
            "request": request,
            "tickets": tickets,
            "user_id": user_id
        }
    )

@router.post("/cancel-ticket/{ticket_id}")
def cancel_ticket(ticket_id: int, db: Session = Depends(get_db)):

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if ticket:
        db.delete(ticket)
        db.commit()

    return RedirectResponse(url="/my-tickets", status_code=303)    

@router.get("/verify-ticket/{ticket_id}")
def verify_ticket(ticket_id: int, db: Session = Depends(get_db)):

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        return {"status": "Invalid Ticket"}

    return {
        "status": "Valid Ticket",
        "event": ticket.event.title,
        "user": ticket.user.email
    }


@router.post("/create-payment/{event_id}")
def create_payment(event_id: int, request: Request, db: Session = Depends(get_db)):

    user_id = request.cookies.get("user_id")

    if not user_id:
        return {"error": "Login required"}

    event = db.query(Event).filter(Event.id == event_id).first()

    amount = int(event.price * 100)

    order = create_razorpay_order(amount)

    return {
        "order_id": order["id"],
        "amount": order["amount"],
        "key": os.getenv("RAZORPAY_KEY")   
    }


@router.post("/verify-payment/{event_id}")
async def verify_payment(
    event_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    data = await request.json()

    razorpay_payment_id = data["razorpay_payment_id"]
    razorpay_order_id = data["razorpay_order_id"]
    razorpay_signature = data["razorpay_signature"]

    params_dict = {
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_order_id": razorpay_order_id,
        "razorpay_signature": razorpay_signature
    }

    try:
        client.utility.verify_payment_signature(params_dict)

    except:
        return {"status": "Payment verification failed"}

    user_id = request.cookies.get("user_id")

    user = db.query(User).filter(User.id == int(user_id)).first()

    event = db.query(Event).filter(Event.id == event_id).first()

    payment = Payment(
        user_id=user.id,
        event_id=event.id,
        razorpay_payment_id=razorpay_payment_id,
        razorpay_order_id=razorpay_order_id,
        amount=event.price,
        status="success"
    )

    db.add(payment)
    db.commit()

    ticket = Ticket(
        event_id=event.id,
        user_id=user.id,
        user_name=user.name
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    ticket_image = generate_ticket_qr(
        ticket.id,
        event.title,
        event.date,
        event.location
    )

    ticket.ticket_image = ticket_image
    db.commit()

    background_tasks.add_task(
        send_ticket_email,
        user.email,
        user.name,
        event.title,
        ticket_image
    )

    return {"status": "Payment verified"}
