from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from backend.app.models.user import User
from backend.app.models.audit import AuditLog
from backend.app.services.auth_service import register_user, authenticate_user, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(request_data: UserRegisterRequest, request: Request, db: Session = Depends(get_db)):
    """Registers a new user account."""
    ip = request.client.host if request.client else None
    user = register_user(db, request_data, ip_address=ip)
    return user


@router.post("/login", response_model=TokenResponse)
def login(request_data: UserLoginRequest, request: Request, db: Session = Depends(get_db)):
    """Authenticates credentials and returns a JWT Bearer token."""
    ip = request.client.host if request.client else None
    token_response = authenticate_user(db, request_data, ip_address=ip)
    return token_response


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Returns the authenticated user's profile."""
    return current_user


@router.post("/logout")
def logout(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Logs out the user and records the event in audit logs."""
    ip = request.client.host if request.client else None
    audit = AuditLog(
        user_id=current_user.id,
        action="USER_LOGOUT",
        resource_type="USER",
        resource_id=current_user.id,
        ip_address=ip,
        status="SUCCESS"
    )
    db.add(audit)
    db.commit()
    return {"message": "Successfully logged out."}
