from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.hash import bcrypt

from backend.database import get_db
from backend.models import User
from backend.data import page_data
from fastapi.responses import RedirectResponse


router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.post("/login")
def member_login(
    request: Request,
    membership_id: int = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    # Find user by membership ID
    user = db.query(User).filter(User.id == membership_id).first()

    # User not found
    if not user:
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "request": request,
                "data": page_data,
                "events": page_data["events"],
                "login_error": "Member not found"
            }
        )

    # Limit password length
    safe_password = password[:72]

    # Verify password
    if not bcrypt.verify(safe_password, user.password):
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "request": request,
                "data": page_data,
                "events": page_data["events"],
                "login_error": "Invalid password"
            }
        )



    response = RedirectResponse("/dashboard", status_code=303)

    response.set_cookie(
        key="user_id",
        value=str(user.id),
        httponly=True
    )

    return response


@router.get("/dashboard")
def dashboard(request: Request):

    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "request": request,
            "user_id": user_id
        }
    )

@router.get("/logout")
def logout():

    response = RedirectResponse("/", status_code=303)

    response.delete_cookie("user_id")

    return response