from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field


class SeatInventory(SQLModel, table=True):
    __tablename__ = "seat_inventories"

    id: Optional[int] = Field(default=None, primary_key=True)
    train_id: int = Field(foreign_key="trains.id", index=True, nullable=False)
    journey_date: str = Field(index=True, nullable=False, description="YYYY-MM-DD")
    total_seats: int = Field(default=60, ge=0)
    available_seats: int = Field(default=60, ge=0)
    booked_seats: int = Field(default=0, ge=0)
    version: int = Field(default=1, nullable=False, description="Optimistic locking version")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
