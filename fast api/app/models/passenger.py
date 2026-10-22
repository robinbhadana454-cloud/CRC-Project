from typing import Optional
from sqlmodel import SQLModel, Field


class Passenger(SQLModel, table=True):
    __tablename__ = "passengers"

    id: Optional[int] = Field(default=None, primary_key=True)
    booking_id: int = Field(foreign_key="bookings.id", index=True, nullable=False)
    name: str = Field(nullable=False)
    age: int = Field(nullable=False, ge=1, le=120)
    gender: str = Field(nullable=False, max_length=10, description="'M', 'F', 'Other'")
    seat_number: str = Field(nullable=False, max_length=20)
