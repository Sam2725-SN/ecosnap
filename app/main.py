# ──────────────────────────────────────────────
# app/main.py  –  FastAPI application entry point
# ──────────────────────────────────────────────
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import os

from app.database import engine, Base
from app.models import User, Complaint          # ensure models are registered
from app.routes import auth, complaints, dashboard
from app.auth import hash_password
from app.database import SessionLocal


# ── Create tables + seed admin on startup ────
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _seed_admin()
    yield


def _seed_admin():
    """Create a default admin account if none exists."""
    db = SessionLocal()
    try:
        from app.models.user import User as UserModel
        if not db.query(UserModel).filter(UserModel.is_admin == True).first():
            admin = UserModel(
                name="EcoSnap Admin",
                email="admin@ecosnap.com",
                hashed_password=hash_password("admin123"),
                is_admin=True,
            )
            db.add(admin)
            db.commit()
            print("✅  Default admin created  →  admin@ecosnap.com / admin123")
    finally:
        db.close()


# ── App factory ───────────────────────────────
app = FastAPI(title="EcoSnap", version="1.0.0", lifespan=lifespan)

# Static files (CSS / JS / images)
app.mount("/static",  StaticFiles(directory="app/static"),  name="static")
app.mount("/uploads", StaticFiles(directory="app/uploads"), name="uploads")

# Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# ── Routers ───────────────────────────────────
app.include_router(auth.router)
app.include_router(complaints.router)
app.include_router(dashboard.router)


# ── Home page ─────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    from app.auth import get_current_user_from_cookie
    user = get_current_user_from_cookie(request)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})
