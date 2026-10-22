from datetime import datetime, date, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import update
from sqlmodel import Session, select

from app.models.user import User
from app.models.train import Train
from app.models.station import Station
from app.models.inventory import SeatInventory
from app.models.booking import Booking
from app.models.passenger import Passenger
from app.schemas.booking import (
    BookingCreate,
    BookingResponse,
    PassengerResponse,
    CancelBookingResponse,
)
from app.services.search_service import get_or_create_seat_inventory, find_station_by_query
from app.utils.pnr import generate_unique_pnr


def format_booking_response(session: Session, booking: Booking) -> BookingResponse:
    """Helper to convert a Booking DB record into a comprehensive BookingResponse."""
    train = session.get(Train, booking.train_id)
    source_st = session.get(Station, booking.source_station_id)
    dest_st = session.get(Station, booking.destination_station_id)

    raw_passengers = session.exec(
        select(Passenger).where(Passenger.booking_id == booking.id)
    ).all()

    passengers_out = [
        PassengerResponse(
            id=p.id,
            name=p.name,
            age=p.age,
            gender=p.gender,
            seat_number=p.seat_number,
        )
        for p in raw_passengers
    ]

    return BookingResponse(
        id=booking.id,
        pnr=booking.pnr,
        train_id=booking.train_id,
        train_number=train.train_number if train else "UNKNOWN",
        train_name=train.train_name if train else "Unknown Train",
        journey_date=booking.journey_date,
        source_station_code=source_st.code if source_st else "",
        source_station_name=source_st.name if source_st else "",
        destination_station_code=dest_st.code if dest_st else "",
        destination_station_name=dest_st.name if dest_st else "",
        num_passengers=booking.num_passengers,
        total_fare=booking.total_fare,
        status=booking.status,
        payment_status=booking.payment_status,
        passengers=passengers_out,
        created_at=booking.created_at,
        cancelled_at=booking.cancelled_at,
    )


def book_ticket(session: Session, current_user: User, data: BookingCreate) -> BookingResponse:
    """
    Book train tickets for passengers within an atomic database transaction.
    Includes optimistic concurrency control to prevent overbooking and race conditions.
    """
    train = session.get(Train, data.train_id)
    if not train:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Train not found.")

    if not train.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This train is currently deactivated and not accepting bookings.",
        )

    # Validate journey date
    try:
        j_date = datetime.strptime(data.journey_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid journey date format. Please use YYYY-MM-DD format.",
        )

    if j_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot book tickets for past dates.",
        )

    # Determine source and destination stations
    if data.source_station_code:
        src_st = find_station_by_query(session, data.source_station_code)
        if not src_st:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source station '{data.source_station_code}' not found.",
            )
    else:
        src_st = session.get(Station, train.source_station_id)

    if data.destination_station_code:
        dest_st = find_station_by_query(session, data.destination_station_code)
        if not dest_st:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Destination station '{data.destination_station_code}' not found.",
            )
    else:
        dest_st = session.get(Station, train.destination_station_id)

    if src_st.id == dest_st.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source and destination stations cannot be the same.",
        )

    num_passengers = len(data.passengers)
    if num_passengers <= 0 or num_passengers > 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A booking must have between 1 and 6 passengers.",
        )

    # Ensure inventory exists
    inv = get_or_create_seat_inventory(session, train, data.journey_date)

    if inv.available_seats < num_passengers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Train is fully booked or insufficient seats available. Requested: {num_passengers}, Available: {inv.available_seats}.",
        )

    # Optimistic Concurrency Control (OCC): Atomically decrement available seats
    current_version = inv.version
    current_booked = inv.booked_seats

    stmt = (
        update(SeatInventory)
        .where(SeatInventory.id == inv.id)
        .where(SeatInventory.version == current_version)
        .where(SeatInventory.available_seats >= num_passengers)
        .values(
            available_seats=SeatInventory.available_seats - num_passengers,
            booked_seats=SeatInventory.booked_seats + num_passengers,
            version=SeatInventory.version + 1,
            updated_at=datetime.now(timezone.utc),
        )
    )

    result = session.execute(stmt)
    if result.rowcount == 0:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Concurrent booking conflict detected: seats were modified by another transaction. Please try again.",
        )

    # Generate unique PNR
    pnr = generate_unique_pnr(session)
    total_fare = round(train.base_fare * num_passengers, 2)

    booking = Booking(
        pnr=pnr,
        user_id=current_user.id,
        train_id=train.id,
        source_station_id=src_st.id,
        destination_station_id=dest_st.id,
        journey_date=data.journey_date,
        num_passengers=num_passengers,
        total_fare=total_fare,
        status="CONFIRMED",
        payment_status="PAID",
    )
    session.add(booking)
    session.commit()
    session.refresh(booking)

    # Allocate sequential seat numbers
    passengers_to_add = []
    for idx, p_in in enumerate(data.passengers):
        seat_num = f"S-{current_booked + idx + 1}"
        passenger = Passenger(
            booking_id=booking.id,
            name=p_in.name.strip(),
            age=p_in.age,
            gender=p_in.gender,
            seat_number=seat_num,
        )
        passengers_to_add.append(passenger)

    session.add_all(passengers_to_add)
    session.commit()

    return format_booking_response(session, booking)


def cancel_booking(session: Session, current_user: User, pnr: str) -> CancelBookingResponse:
    """
    Cancel an existing booking and restore seat inventory within an atomic transaction.
    Prevents repeated seat release and unauthorized cancellation.
    """
    clean_pnr = pnr.strip().upper()
    booking = session.exec(select(Booking).where(Booking.pnr == clean_pnr)).first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with PNR '{clean_pnr}' not found.",
        )

    # Authorization check: only owner or admin can cancel
    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you can only cancel your own bookings.",
        )

    # Check idempotency / double cancellation prevention
    if booking.status == "CANCELLED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Booking with PNR '{clean_pnr}' is already cancelled. Repeated seat release is prohibited.",
        )

    now_utc = datetime.now(timezone.utc)
    booking.status = "CANCELLED"
    booking.payment_status = "REFUNDED"
    booking.cancelled_at = now_utc
    session.add(booking)

    # Restore seats in inventory atomically
    stmt = (
        update(SeatInventory)
        .where(SeatInventory.train_id == booking.train_id)
        .where(SeatInventory.journey_date == booking.journey_date)
        .values(
            available_seats=SeatInventory.available_seats + booking.num_passengers,
            booked_seats=SeatInventory.booked_seats - booking.num_passengers,
            version=SeatInventory.version + 1,
            updated_at=now_utc,
        )
    )
    session.execute(stmt)
    session.commit()

    return CancelBookingResponse(
        message=f"Booking with PNR {clean_pnr} has been successfully cancelled and simulated refund processed.",
        pnr=clean_pnr,
        status="CANCELLED",
        refunded_amount=booking.total_fare,
        cancelled_at=now_utc,
        restored_seats=booking.num_passengers,
    )


def get_user_bookings(session: Session, current_user: User) -> List[BookingResponse]:
    """Retrieve booking history for the current user."""
    bookings = session.exec(
        select(Booking).where(Booking.user_id == current_user.id).order_by(Booking.created_at.desc())
    ).all()
    return [format_booking_response(session, b) for b in bookings]


def get_booking_by_pnr(session: Session, current_user: User, pnr: str) -> BookingResponse:
    """Retrieve details of a specific booking by PNR, ensuring access controls."""
    clean_pnr = pnr.strip().upper()
    booking = session.exec(select(Booking).where(Booking.pnr == clean_pnr)).first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with PNR '{clean_pnr}' not found.",
        )

    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you can only view your own bookings.",
        )

    return format_booking_response(session, booking)
