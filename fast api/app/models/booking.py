from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field


class Booking(SQLModel, table=True):
    __tablename__ = "bookings"

    id: Optional[int] = Field(default=None, primary_key=True)
    pnr: str = Field(unique=True, index=True, nullable=False, max_length=15)
    user_id: int = Field(foreign_key="users.id", index=True, nullable=False)
    train_id: int = Field(foreign_key="trains.id", index=True, nullable=False)
    source_station_id: int = Field(foreign_key="stations.id", nullable=False)
    destination_station_id: int = Field(foreign_key="stations.id", nullable=False)
    journey_date: str = Field(index=True, nullable=False, description="YYYY-MM-DD")
    num_passengers: int = Field(default=1, ge=1, le=6)
    total_fare: float = Field(default=0.0, ge=0.0)
    status: str = Field(default="CONFIRMED", index=True, description="CONFIRMED, CANCELLED")
    payment_status: str = Field(default="PAID", description="PAID, REFUNDED")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    cancelled_at: Optional[datetime] = Field(default=None)
