from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field


class Train(SQLModel, table=True):
    __tablename__ = "trains"

    id: Optional[int] = Field(default=None, primary_key=True)
    train_number: str = Field(unique=True, index=True, nullable=False, max_length=20)
    train_name: str = Field(index=True, nullable=False)
    source_station_id: int = Field(foreign_key="stations.id", nullable=False)
    destination_station_id: int = Field(foreign_key="stations.id", nullable=False)
    departure_time: str = Field(nullable=False, description="HH:MM (24-hour format)")
    arrival_time: str = Field(nullable=False, description="HH:MM (24-hour format)")
    base_fare: float = Field(default=500.0, ge=0.0)
    total_seats: int = Field(default=60, gt=0)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
