from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session

from app.database import get_session
from app.models.user import User
from app.schemas.user import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    MessageResponse,
)
from app.services.auth_service import (
    register_user,
    authenticate_user,
    logout_user,
    request_password_reset,
    reset_password,
)
from app.utils.security import get_current_user, security_scheme

router = APIRouter(prefix="/auth", tags=["Authentication & Accounts"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, session: Session = Depends(get_session)):
    """
    Register a new passenger account.
    Passwords are encrypted using standard bcrypt hashing.
    """
    return register_user(session, data)


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, session: Session = Depends(get_session)):
    """
    Authenticate passenger or administrator credentials.
    Returns a signed JWT access token for Bearer authorization.
    """
    return authenticate_user(session, data)


@router.post("/logout", response_model=MessageResponse)
def logout(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Log out the current user by revoking the JWT token on the server side.
    Revoked tokens are recorded in the database denylist and immediately invalidated.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bearer token required to perform logout.",
        )
    return logout_user(session, credentials.credentials)


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(data: ForgotPasswordRequest, session: Session = Depends(get_session)):
    """
    Request a password reset link/token.
    In development mode, the expiring single-use token is simulated and returned in the response.
    """
    return request_password_reset(session, data.email)


@router.post("/reset-password", response_model=MessageResponse)
def reset_user_password(data: ResetPasswordRequest, session: Session = Depends(get_session)):
    """
    Reset account password using an expiring single-use reset token.
    Prevents reuse of already utilized tokens.
    """
    return reset_password(session, data)


@router.get("/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """
    View authenticated user profile.
    Only accessible by the logged-in owner.
    """
    return UserResponse.model_validate(current_user)
