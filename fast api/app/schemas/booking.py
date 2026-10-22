from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class PassengerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=60)
    age: int = Field(ge=1, le=120)
    gender: str = Field(pattern=r"^(M|F|Other)$", description="'M', 'F', or 'Other'")


class PassengerResponse(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    seat_number: str
    model_config = ConfigDict(from_attributes=True)


class BookingCreate(BaseModel):
    train_id: int
    journey_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$", description="YYYY-MM-DD")
    source_station_code: Optional[str] = None
    destination_station_code: Optional[str] = None
    passengers: List[PassengerCreate] = Field(min_length=1, max_length=6)


class BookingResponse(BaseModel):
    id: int
    pnr: str
    train_id: int
    train_number: str
    train_name: str
    journey_date: str
    source_station_code: str
    source_station_name: str
    destination_station_code: str
    destination_station_name: str
    num_passengers: int
    total_fare: float
    status: str
    payment_status: str
    passengers: List[PassengerResponse]
    created_at: datetime
    cancelled_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class CancelBookingResponse(BaseModel):
    message: str
    pnr: str
    status: str
    refunded_amount: float
    cancelled_at: datetime
    restored_seats: int
