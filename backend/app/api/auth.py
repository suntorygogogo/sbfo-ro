from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, config

router = APIRouter()


@router.get("/config")
def get_config():
    """Return current auth mode so the frontend knows how to handle login."""
    return {"auth_mode": config.AUTH_MODE}


@router.get("/me")
def get_me(request: Request, db: Session = Depends(get_db)):
    """DBX mode only: resolve current user from Databricks-injected header."""
    email = request.headers.get("X-Forwarded-Email")
    if not email:
        raise HTTPException(status_code=401, detail="No user identity provided by Databricks")
    user = (
        db.query(models.AppUser)
        .filter(models.AppUser.email == email, models.AppUser.is_active == True)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User '{email}' is not registered in this application. Please contact your administrator.",
        )
    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "role": user.role,
        "departments": user.departments,
    }
