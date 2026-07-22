# ──────────────────────────────────────────────
# app/routes/dashboard.py  –  Analytics dashboard
# ──────────────────────────────────────────────
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.complaint import Complaint, StatusEnum
from app.auth import get_current_user_from_cookie

router    = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _build_stats(db: Session) -> dict:
    total      = db.query(func.count(Complaint.id)).scalar() or 0
    pending    = db.query(func.count(Complaint.id)).filter(Complaint.status == StatusEnum.pending).scalar() or 0
    in_prog    = db.query(func.count(Complaint.id)).filter(Complaint.status == StatusEnum.in_progress).scalar() or 0
    resolved   = db.query(func.count(Complaint.id)).filter(Complaint.status == StatusEnum.resolved).scalar() or 0
    return {"total": total, "pending": pending, "in_progress": in_prog, "resolved": resolved}


# ── GET /dashboard  (HTML page) ───────────────
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request)
    if not user:
        return RedirectResponse("/login", status_code=302)

    # Only admin can access dashboard
    if not user["is_admin"]:
        return RedirectResponse("/my-complaints", status_code=302)

    stats = _build_stats(db)
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "user": user, "stats": stats}
    )


# ── GET /dashboard  (JSON API) ────────────────
@router.get("/api/dashboard")
async def dashboard_api(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request)
    if not user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    return _build_stats(db)
