from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class StationBase(BaseModel):
    code: str = Field(min_length=2, max_length=10, description="Station code, e.g. NDLS")
    name: str = Field(min_length=2, max_length=100, description="Station name, e.g. New Delhi")
    city: str = Field(min_length=2, max_length=100)
    state: str = Field(min_length=2, max_length=100)


class StationCreate(StationBase):
    pass


class StationResponse(StationBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TrainStopCreate(BaseModel):
    station_code: str
    stop_sequence: int = Field(ge=1)
    arrival_time: Optional[str] = Field(None, pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    departure_time: Optional[str] = Field(None, pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    distance_km: float = Field(0.0, ge=0.0)
    fare_from_source: float = Field(0.0, ge=0.0)


class TrainStopResponse(BaseModel):
    id: int
    station_code: str
    station_name: str
    stop_sequence: int
    arrival_time: Optional[str]
    departure_time: Optional[str]
    distance_km: float
    fare_from_source: float
    model_config = ConfigDict(from_attributes=True)


class TrainCreate(BaseModel):
    train_number: str = Field(min_length=3, max_length=20, description="Unique train number, e.g. 12004")
    train_name: str = Field(min_length=3, max_length=100, description="e.g. Lucknow Swarna Shatabdi")
    source_station_code: str = Field(description="Origin station code, e.g. NDLS")
    destination_station_code: str = Field(description="Destination station code, e.g. CNB")
    departure_time: str = Field(pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$", description="HH:MM")
    arrival_time: str = Field(pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$", description="HH:MM")
    base_fare: float = Field(ge=1.0, description="Base ticket fare")
    total_seats: int = Field(default=60, ge=1, le=1000, description="Seat capacity")
    stops: Optional[List[TrainStopCreate]] = None


class TrainUpdate(BaseModel):
    train_name: Optional[str] = None
    departure_time: Optional[str] = Field(None, pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    arrival_time: Optional[str] = Field(None, pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    base_fare: Optional[float] = Field(None, ge=1.0)
    total_seats: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class TrainResponse(BaseModel):
    id: int
    train_number: str
    train_name: str
    source_station_code: str
    source_station_name: str
    destination_station_code: str
    destination_station_name: str
    departure_time: str
    arrival_time: str
    base_fare: float
    total_seats: int
    is_active: bool
    stops: List[TrainStopResponse] = []
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SeatInventoryUpdate(BaseModel):
    train_id: int
    journey_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$", description="YYYY-MM-DD")
    total_seats: int = Field(ge=0)
    available_seats: int = Field(ge=0)
