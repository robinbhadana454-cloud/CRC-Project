import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.config import settings
from app.models.user import User
from app.models.token import RevokedToken, PasswordResetToken
from app.schemas.user import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    MessageResponse,
)
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)


def register_user(session: Session, data: UserRegister) -> UserResponse:
    """Register a new passenger account."""
    email_clean = data.email.strip().lower()
    existing = session.exec(select(User).where(User.email == email_clean)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    user = User(
        email=email_clean,
        full_name=data.full_name.strip(),
        hashed_password=hash_password(data.password),
        role="passenger",
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserResponse.model_validate(user)


def authenticate_user(session: Session, data: UserLogin) -> TokenResponse:
    """Authenticate email and password, returning a signed JWT access token."""
    email_clean = data.email.strip().lower()
    user = session.exec(select(User).where(User.email == email_clean)).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Please contact support.",
        )

    token_payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "name": user.full_name,
    }
    access_token = create_access_token(token_payload)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


def logout_user(session: Session, token_str: str) -> MessageResponse:
    """Revoke JWT token on server-side and add to denylist table."""
    try:
        payload = decode_token(token_str)
        jti = payload.get("jti")
        exp_ts = payload.get("exp")
        if not jti or not exp_ts:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token structure.")

        expires_at = datetime.fromtimestamp(exp_ts, tz=timezone.utc)
        
        # Check if already revoked
        existing = session.exec(select(RevokedToken).where(RevokedToken.jti == jti)).first()
        if not existing:
            revoked = RevokedToken(
                jti=jti,
                token_str=token_str[-12:],  # store only end snippet for reference without logging secrets
                expires_at=expires_at,
            )
            session.add(revoked)
            session.commit()

        return MessageResponse(message="Successfully logged out. Token has been revoked on server.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Logout failed: {str(e)}")


def request_password_reset(session: Session, email: str) -> ForgotPasswordResponse:
    """Generate a single-use time-limited password reset token for the account."""
    email_clean = email.strip().lower()
    user = session.exec(select(User).where(User.email == email_clean)).first()

    if not user:
        # Prevent user enumeration in production, but confirm message
        return ForgotPasswordResponse(
            message="If an account exists with that email, a password reset token has been generated.",
            reset_token=None,
            note="Account not found (safe response).",
        )

    # Invalidate previous unused reset tokens for this user
    old_tokens = session.exec(
        select(PasswordResetToken).where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.is_used == False,
        )
    ).all()
    for ot in old_tokens:
        ot.is_used = True
        session.add(ot)

    raw_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)

    reset_entry = PasswordResetToken(
        user_id=user.id,
        token=raw_token,
        expires_at=expires_at,
        is_used=False,
    )
    session.add(reset_entry)
    session.commit()

    return ForgotPasswordResponse(
        message="Password reset token generated successfully. In production, this is emailed to the user.",
        reset_token=raw_token,
        note="Development mode: Use this reset token in /api/v1/auth/reset-password",
    )


def reset_password(session: Session, data: ResetPasswordRequest) -> MessageResponse:
    """Validate single-use reset token and update user password."""
    reset_entry = session.exec(
        select(PasswordResetToken).where(PasswordResetToken.token == data.token.strip())
    ).first()

    if not reset_entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password reset token.",
        )

    if reset_entry.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token has already been used.",
        )

    now_utc = datetime.now(timezone.utc)
    # Ensure timezone comparison
    token_exp = reset_entry.expires_at
    if token_exp.tzinfo is None:
        token_exp = token_exp.replace(tzinfo=timezone.utc)

    if now_utc > token_exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token has expired. Please request a new one.",
        )

    user = session.get(User, reset_entry.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User account not found.")

    user.hashed_password = hash_password(data.new_password)
    user.updated_at = now_utc
    session.add(user)

    reset_entry.is_used = True
    session.add(reset_entry)

    session.commit()
    return MessageResponse(message="Password has been successfully reset. You may now log in with your new credentials.")
