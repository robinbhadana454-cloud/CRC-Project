from typing import List
from pydantic import BaseModel, Field


class TrainSearchResult(BaseModel):
    train_id: int
    train_number: str
    train_name: str
    source_station_code: str
    source_station_name: str
    destination_station_code: str
    destination_station_name: str
    departure_time: str
    arrival_time: str
    journey_date: str
    fare: float
    total_seats: int
    available_seats: int
    status: str = "AVAILABLE"  # AVAILABLE or FULL


class TrainSearchResponse(BaseModel):
    query_source: str
    query_destination: str
    journey_date: str
    total_trains: int
    trains: List[TrainSearchResult]


class SeatAvailabilityResponse(BaseModel):
    train_id: int
    train_number: str
    train_name: str
    journey_date: str
    total_seats: int
    available_seats: int
    booked_seats: int
    is_available: bool
