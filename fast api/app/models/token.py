from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field


class RevokedToken(SQLModel, table=True):
    __tablename__ = "revoked_tokens"

    id: Optional[int] = Field(default=None, primary_key=True)
    jti: str = Field(unique=True, index=True, nullable=False, description="JWT ID or token hash")
    token_str: Optional[str] = Field(default=None, index=True)
    revoked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(nullable=False)


class PasswordResetToken(SQLModel, table=True):
    __tablename__ = "password_reset_tokens"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, nullable=False)
    token: str = Field(unique=True, index=True, nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(nullable=False)
    is_used: bool = Field(default=False, index=True)
