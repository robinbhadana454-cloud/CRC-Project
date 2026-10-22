from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field


class TrainStop(SQLModel, table=True):
    __tablename__ = "train_stops"

    id: Optional[int] = Field(default=None, primary_key=True)
    train_id: int = Field(foreign_key="trains.id", index=True, nullable=False)
    station_id: int = Field(foreign_key="stations.id", index=True, nullable=False)
    stop_sequence: int = Field(nullable=False, description="1-indexed sequence order along the route")
    arrival_time: Optional[str] = Field(default=None, description="HH:MM (24-hour format)")
    departure_time: Optional[str] = Field(default=None, description="HH:MM (24-hour format)")
    distance_km: float = Field(default=0.0, ge=0.0)
    fare_from_source: float = Field(default=0.0, ge=0.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
