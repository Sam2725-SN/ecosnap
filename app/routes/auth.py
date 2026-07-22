from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.auth import hash_password, verify_password, create_access_token

router    = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def register(
    request: Request,
    name:     str = Form(...),
    email:    str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Email already registered."},
            status_code=400,
        )
    if len(password) < 6:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Password must be at least 6 characters."},
            status_code=400,
        )
    user = User(name=name, email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return RedirectResponse("/login?registered=1", status_code=302)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, registered: str = ""):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "registered": registered == "1"},
    )


@router.post("/login")
async def login(
    request: Request,
    email:    str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid email or password."},
            status_code=401,
        )
    token = create_access_token(
        {"sub": str(user.id), "email": user.email, "name": user.name, "is_admin": user.is_admin}
    )
    response = RedirectResponse("/dashboard" if user.is_admin else "/my-complaints", status_code=302)
    response.set_cookie("access_token", token, httponly=True, max_age=86400)
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("access_token")
    return response