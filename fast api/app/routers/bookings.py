from typing import List
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.database import get_session
from app.models.user import User
from app.schemas.booking import (
    BookingCreate,
    BookingResponse,
    CancelBookingResponse,
)
from app.services.booking_service import (
    book_ticket,
    cancel_booking,
    get_user_bookings,
    get_booking_by_pnr,
)
from app.utils.security import get_current_user

router = APIRouter(prefix="/bookings", tags=["Bookings & Ticketing"])


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    data: BookingCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Book tickets for a train journey within an atomic database transaction.
    Allocates seat numbers and generates a unique PNR.
    Employs optimistic concurrency control to prevent overbooking.
    """
    return book_ticket(session, current_user, data)


@router.get("/my-bookings", response_model=List[BookingResponse])
def view_my_bookings(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Retrieve booking history for the authenticated passenger.
    Passengers can only view their own bookings.
    """
    return get_user_bookings(session, current_user)


@router.get("/{pnr}", response_model=BookingResponse)
def view_booking_by_pnr(
    pnr: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    View details and status of a specific booking by PNR.
    Passengers are restricted to viewing only their own bookings.
    """
    return get_booking_by_pnr(session, current_user, pnr)


@router.post("/{pnr}/cancel", response_model=CancelBookingResponse)
def cancel_ticket(
    pnr: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Cancel an eligible ticket and restore seat availability in the database.
    Prevents repeated cancellation and unauthorized access.
    """
    return cancel_booking(session, current_user, pnr)
