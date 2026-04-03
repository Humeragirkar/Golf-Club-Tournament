from fastapi import APIRouter, Depends, Form, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.hash import bcrypt

from backend.database import get_db
from backend.models import User, Membership
from backend.data import page_data

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.post("/membership")
def create_membership(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db)
):

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "request": request,
                "data": page_data,
                "events": page_data["events"],
                "membership_error": "User with this email already exists"
            }
        )

    # Limit password length for bcrypt
    safe_password = password[:72]

    # Hash password
    hashed_password = bcrypt.hash(safe_password)

    # Create new user
    new_user = User(
        name=full_name,
        email=email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create membership
    new_membership = Membership(
        user_id=new_user.id,
        type="T1"
    )

    db.add(new_membership)
    db.commit()

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "data": page_data,
            "events": page_data["events"],
            "membership_success": "Membership created successfully!"
        }
    )