from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Depends
from sqlalchemy.orm import Session


from backend.routers import users, events, membership
from backend.database import engine, get_db, SessionLocal
from backend.models import  Base, Newsletter, ContactMessage, User, Event
from backend.data import page_data
from dotenv import load_dotenv
import os


load_dotenv()


Base.metadata.create_all(bind=engine)


app = FastAPI()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

templates = Jinja2Templates(
    directory=os.path.join(BASE_DIR, "templates")
)

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static"
)

# Routers
app.include_router(users.router)
app.include_router(events.router)
app.include_router(membership.router)




# -----------------------------
# HOME PAGE
# -----------------------------

@app.get("/")
def home(request: Request):

    user_id = request.cookies.get("user_id")

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "data": page_data,
            "events": page_data["events"],
            "user_id": user_id
        }
    )

# -----------------------------
# EVENTS PAGE
# -----------------------------

@app.get("/events-page")
def events_page(request: Request):

    return templates.TemplateResponse(
        request,
        "event-listing.html",
        {
            "request": request,
            "data": page_data,
            "events": page_data["events"]
        }
    )


# -----------------------------
# NEWSLETTER FORM
# -----------------------------

@app.post("/subscribe")
def subscribe(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db)
):

    new_subscriber = Newsletter(email=email)

    db.add(new_subscriber)
    db.commit()

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "data": page_data,
            "events": page_data["events"],
            "newsletter_success": "Subscribed successfully!"
        }
    )




# -----------------------------
# CONTACT FORM
# -----------------------------

@app.post("/contact")
def contact_form(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db)
):

    new_message = ContactMessage(
        name=full_name,
        email=email,
        message=message
    )

    db.add(new_message)
    db.commit()

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "data": page_data,
            "events": page_data["events"],
            "contact_success": "Message sent successfully!"
        }
    )