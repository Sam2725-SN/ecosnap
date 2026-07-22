# ──────────────────────────────────────────────
# app/auth.py  –  Password hashing + JWT helpers
# ──────────────────────────────────────────────
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from typing import Optional

SECRET_KEY  = "ecosnap-super-secret-key-change-in-production"
ALGORITHM   = "HS256"
TOKEN_EXPIRE_HOURS = 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Password helpers ─────────────────────────
def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── JWT helpers ──────────────────────────────
def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


# ── Cookie-based current-user helper ────────
def get_current_user_from_cookie(request: Request) -> Optional[dict]:
    """Returns decoded payload dict or None (no exception)."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    return decode_token(token)


def require_login(request: Request) -> dict:
    """Raises 401 if not authenticated. Use as a FastAPI dependency."""
    user = get_current_user_from_cookie(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/login"},
        )
    return user


def require_admin(request: Request) -> dict:
    """Raises 403 if not admin."""
    user = require_login(request)
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
