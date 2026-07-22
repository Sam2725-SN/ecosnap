import os, uuid, shutil
from fastapi import APIRouter, Depends, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.complaint import Complaint, StatusEnum
from app.models.user import User
from app.auth import get_current_user_from_cookie

router    = APIRouter()
templates = Jinja2Templates(directory="app/templates")

UPLOAD_DIR = "app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


def save_upload(file: UploadFile):
    if not file or not file.filename:
        return None
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(400, "Only image files are allowed.")
    filename = f"{uuid.uuid4().hex}{ext}"
    dest = os.path.join(UPLOAD_DIR, filename)
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return f"/uploads/{filename}"


@router.get("/report", response_class=HTMLResponse)
async def report_page(request: Request):
    user = get_current_user_from_cookie(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse("report.html", {"request": request, "user": user})


@router.post("/report-waste")
async def report_waste(
    request:     Request,
    location:    str        = Form(...),
    description: str        = Form(...),
    image:       UploadFile = File(None),
    db: Session  = Depends(get_db),
):
    user = get_current_user_from_cookie(request)
    if not user:
        return RedirectResponse("/login", status_code=302)

    if len(description.strip()) < 10:
        return templates.TemplateResponse(
            "report.html",
            {"request": request, "user": user, "error": "Description too short (min 10 chars)."},
            status_code=400,
        )

    # Image is mandatory
    if not image or not image.filename:
        return templates.TemplateResponse(
            "report.html",
            {"request": request, "user": user, "error": "Please upload a photo of the waste issue."},
            status_code=400,
        )
    image_url = save_upload(image)

    complaint = Complaint(
        user_id     = int(user["sub"]),
        location    = location.strip(),
        description = description.strip(),
        image_url   = image_url,
    )
    db.add(complaint)
    db.commit()
    return RedirectResponse("/my-complaints?submitted=1", status_code=302)


@router.get("/my-complaints", response_class=HTMLResponse)
async def my_complaints(request: Request, db: Session = Depends(get_db), submitted: str = ""):
    user = get_current_user_from_cookie(request)
    if not user:
        return RedirectResponse("/login", status_code=302)

    items = (
        db.query(Complaint)
        .filter(Complaint.user_id == int(user["sub"]))
        .order_by(Complaint.created_at.desc())
        .all()
    )
    return templates.TemplateResponse(
        "my_complaints.html",
        {"request": request, "user": user, "complaints": items, "submitted": submitted == "1"},
    )


@router.get("/complaints")
async def list_complaints(request: Request, status: str = "", db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request)
    if not user:
        raise HTTPException(401, "Not authenticated")

    q = db.query(Complaint)
    if not user["is_admin"]:
        q = q.filter(Complaint.user_id == int(user["sub"]))
    if status:
        q = q.filter(Complaint.status == status)

    items = q.order_by(Complaint.created_at.desc()).all()
    return [
        {
            "id":          c.id,
            "location":    c.location,
            "description": c.description,
            "image_url":   c.image_url,
            "status":      c.status.value,
            "created_at":  c.created_at.isoformat(),
            "user_id":     c.user_id,
        }
        for c in items
    ]


@router.get("/my-complaints/{user_id}")
async def complaints_by_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request)
    if not user:
        raise HTTPException(401, "Not authenticated")
    if int(user["sub"]) != user_id and not user["is_admin"]:
        raise HTTPException(403, "Forbidden")

    items = db.query(Complaint).filter(Complaint.user_id == user_id).all()
    return [{"id": c.id, "location": c.location, "status": c.status.value} for c in items]


@router.put("/update-status/{complaint_id}")
async def update_status(complaint_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request)
    if not user or not user["is_admin"]:
        raise HTTPException(403, "Admin access required")

    body = await request.json()
    new_status = body.get("status")

    if new_status not in [s.value for s in StatusEnum]:
        raise HTTPException(400, f"Invalid status: {new_status}")

    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(404, "Complaint not found")

    complaint.status = new_status
    db.commit()
    return {"message": "Status updated", "id": complaint_id, "status": new_status}


@router.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request)
    if not user or not user["is_admin"]:
        return RedirectResponse("/login", status_code=302)

    complaints = (
        db.query(Complaint, User)
        .join(User, Complaint.user_id == User.id)
        .order_by(Complaint.created_at.desc())
        .all()
    )
    rows = [
        {
            "id":          c.id,
            "location":    c.location,
            "description": c.description,
            "image_url":   c.image_url,
            "status":      c.status.value,
            "created_at":  c.created_at.strftime("%d %b %Y, %H:%M"),
            "user_name":   u.name,
            "user_email":  u.email,
        }
        for c, u in complaints
    ]
    return templates.TemplateResponse(
        "admin.html", {"request": request, "user": user, "complaints": rows}
    )
@router.delete("/delete-complaint/{complaint_id}")
def delete_complaint(
    complaint_id: int,
    db: Session = Depends(get_db)
):

    complaint = db.query(Complaint).filter(
        Complaint.id == complaint_id
    ).first()

    if not complaint:
        return {"error": "Complaint not found"}

    db.delete(complaint)
    db.commit()

    return {
        "message": "Complaint deleted successfully"
    }

@router.delete("/delete-complaint/{complaint_id}")
async def delete_complaint(complaint_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request)
    if not user:
        raise HTTPException(401, "Not authenticated")

    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(404, "Complaint not found")

    # User can only delete their own complaints
    # Admin can delete any complaint
    if not user["is_admin"] and complaint.user_id != int(user["sub"]):
        raise HTTPException(403, "You can only delete your own complaints")

    # Delete image file if exists
    if complaint.image_url:
        image_path = "app" + complaint.image_url
        if os.path.exists(image_path):
            os.remove(image_path)

    db.delete(complaint)
    db.commit()
    return {"message": "Complaint deleted successfully", "id": complaint_id}