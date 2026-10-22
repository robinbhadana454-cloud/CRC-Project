from typing import List
from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.user import User
from app.models.train import Train
from app.models.station import Station
from app.models.booking import Booking
from app.schemas.train import (
    StationCreate,
    StationResponse,
    TrainCreate,
    TrainUpdate,
    TrainResponse,
    SeatInventoryUpdate,
)
from app.schemas.booking import BookingResponse
from app.services.train_service import (
    create_station,
    list_stations,
    create_train,
    update_train,
    deactivate_train,
    set_seat_inventory,
    format_train_response,
)
from app.services.booking_service import format_booking_response
from app.utils.security import get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin Control"])


@router.post("/stations", response_model=StationResponse, status_code=status.HTTP_201_CREATED)
def admin_create_station(
    data: StationCreate,
    session: Session = Depends(get_session),
    admin: User = Depends(get_current_admin),
):
    """Admin: Add a new railway station."""
    station = create_station(session, data)
    return StationResponse.model_validate(station)


@router.get("/stations", response_model=List[StationResponse])
def admin_list_stations(
    session: Session = Depends(get_session),
    admin: User = Depends(get_current_admin),
):
    """Admin: List all railway stations."""
    stations = list_stations(session)
    return [StationResponse.model_validate(s) for s in stations]


@router.post("/trains", response_model=TrainResponse, status_code=status.HTTP_201_CREATED)
def admin_create_train(
    data: TrainCreate,
    session: Session = Depends(get_session),
    admin: User = Depends(get_current_admin),
):
    """Admin: Add a new train with timings, route, fare, and seat capacity."""
    return create_train(session, data)


@router.put("/trains/{train_id}", response_model=TrainResponse)
def admin_update_train(
    train_id: int,
    data: TrainUpdate,
    session: Session = Depends(get_session),
    admin: User = Depends(get_current_admin),
):
    """Admin: Update train timings, fare, total seats, or details."""
    return update_train(session, train_id, data)


@router.patch("/trains/{train_id}/deactivate", response_model=TrainResponse)
def admin_deactivate_train(
    train_id: int,
    session: Session = Depends(get_session),
    admin: User = Depends(get_current_admin),
):
    """Admin: Deactivate a train to prevent future bookings."""
    return deactivate_train(session, train_id)


@router.get("/trains/{train_id}", response_model=TrainResponse)
def admin_get_train(
    train_id: int,
    session: Session = Depends(get_session),
    admin: User = Depends(get_current_admin),
):
    """Admin: Retrieve full configuration of a train."""
    train = session.get(Train, train_id)
    if not train:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Train not found.")
    return format_train_response(session, train)


@router.post("/inventory", status_code=status.HTTP_200_OK)
def admin_update_seat_inventory(
    data: SeatInventoryUpdate,
    session: Session = Depends(get_session),
    admin: User = Depends(get_current_admin),
):
    """Admin: Directly adjust available seats and capacity for a train on a given date."""
    inv = set_seat_inventory(session, data)
    return {
        "message": "Seat inventory updated successfully.",
        "train_id": inv.train_id,
        "journey_date": inv.journey_date,
        "total_seats": inv.total_seats,
        "available_seats": inv.available_seats,
        "booked_seats": inv.booked_seats,
    }


@router.get("/bookings", response_model=List[BookingResponse])
def admin_list_all_bookings(
    session: Session = Depends(get_session),
    admin: User = Depends(get_current_admin),
):
    """Admin: View all passenger bookings across the entire railway system."""
    bookings = session.exec(select(Booking).order_by(Booking.created_at.desc())).all()
    return [format_booking_response(session, b) for b in bookings]
