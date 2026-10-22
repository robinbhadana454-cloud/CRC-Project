from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.train import Train
from app.models.station import Station
from app.schemas.train import StationResponse, TrainResponse
from app.schemas.search import TrainSearchResponse, SeatAvailabilityResponse
from app.services.search_service import search_trains, get_seat_availability
from app.services.train_service import list_stations, format_train_response

router = APIRouter(prefix="/trains", tags=["Train Discovery & Search"])


@router.get("/search", response_model=TrainSearchResponse)
def search_trains_route(
    source_station: str = Query(..., description="Origin station code or name (e.g. NDLS or New Delhi)"),
    destination_station: str = Query(..., description="Destination station code or name (e.g. CNB or Kanpur Central)"),
    journey_date: str = Query(..., description="Journey date in YYYY-MM-DD format"),
    session: Session = Depends(get_session),
):
    """
    Search available trains between two stations for a specific date.
    Returns timings, fare, and real-time seat availability.
    """
    return search_trains(session, source_station, destination_station, journey_date)


@router.get("/stations", response_model=List[StationResponse])
def get_public_stations(session: Session = Depends(get_session)):
    """Retrieve all available railway stations."""
    stations = list_stations(session)
    return [StationResponse.model_validate(s) for s in stations]


@router.get("/{train_id}", response_model=TrainResponse)
def get_train_details(train_id: int, session: Session = Depends(get_session)):
    """Retrieve full details of a train including scheduled stops."""
    train = session.get(Train, train_id)
    if not train or not train.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Train not found or inactive.",
        )
    return format_train_response(session, train)


@router.get("/{train_id}/availability", response_model=SeatAvailabilityResponse)
def check_train_seat_availability(
    train_id: int,
    journey_date: str = Query(..., description="Journey date in YYYY-MM-DD format"),
    session: Session = Depends(get_session),
):
    """Check seat availability for a specific train and journey date."""
    return get_seat_availability(session, train_id, journey_date)
