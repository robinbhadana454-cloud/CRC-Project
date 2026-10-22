from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field


class Station(SQLModel, table=True):
    __tablename__ = "stations"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True, nullable=False, max_length=10)
    name: str = Field(index=True, nullable=False)
    city: str = Field(index=True, nullable=False)
    state: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
