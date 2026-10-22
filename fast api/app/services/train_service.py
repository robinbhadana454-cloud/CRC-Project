from datetime import datetime, date, timedelta, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.station import Station
from app.models.train import Train
from app.models.schedule import TrainStop
from app.models.inventory import SeatInventory
from app.schemas.train import (
    StationCreate,
    StationResponse,
    TrainCreate,
    TrainUpdate,
    TrainResponse,
    TrainStopResponse,
    SeatInventoryUpdate,
)


def create_station(session: Session, data: StationCreate) -> Station:
    """Create a new railway station."""
    code_clean = data.code.strip().upper()
    existing = session.exec(select(Station).where(Station.code == code_clean)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Station with code '{code_clean}' already exists.",
        )
    station = Station(
        code=code_clean,
        name=data.name.strip(),
        city=data.city.strip(),
        state=data.state.strip(),
    )
    session.add(station)
    session.commit()
    session.refresh(station)
    return station


def list_stations(session: Session) -> List[Station]:
    """Retrieve all configured stations."""
    return session.exec(select(Station).order_by(Station.code)).all()


def format_train_response(session: Session, train: Train) -> TrainResponse:
    """Helper to convert a Train model into a comprehensive TrainResponse schema."""
    source_st = session.get(Station, train.source_station_id)
    dest_st = session.get(Station, train.destination_station_id)

    raw_stops = session.exec(
        select(TrainStop).where(TrainStop.train_id == train.id).order_by(TrainStop.stop_sequence)
    ).all()

    stops_res: List[TrainStopResponse] = []
    for s in raw_stops:
        st = session.get(Station, s.station_id)
        stops_res.append(
            TrainStopResponse(
                id=s.id,
                station_code=st.code if st else "UNKNOWN",
                station_name=st.name if st else "Unknown Station",
                stop_sequence=s.stop_sequence,
                arrival_time=s.arrival_time,
                departure_time=s.departure_time,
                distance_km=s.distance_km,
                fare_from_source=s.fare_from_source,
            )
        )

    return TrainResponse(
        id=train.id,
        train_number=train.train_number,
        train_name=train.train_name,
        source_station_code=source_st.code if source_st else "",
        source_station_name=source_st.name if source_st else "",
        destination_station_code=dest_st.code if dest_st else "",
        destination_station_name=dest_st.name if dest_st else "",
        departure_time=train.departure_time,
        arrival_time=train.arrival_time,
        base_fare=train.base_fare,
        total_seats=train.total_seats,
        is_active=train.is_active,
        stops=stops_res,
        created_at=train.created_at,
    )


def create_train(session: Session, data: TrainCreate) -> TrainResponse:
    """Admin function to create a new train with route stops and initialize seat inventory."""
    train_num_clean = data.train_number.strip().upper()
    existing = session.exec(select(Train).where(Train.train_number == train_num_clean)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Train with number '{train_num_clean}' already exists.",
        )

    src_st = session.exec(select(Station).where(Station.code == data.source_station_code.strip().upper())).first()
    if not src_st:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source station '{data.source_station_code}' not found.",
        )

    dest_st = session.exec(select(Station).where(Station.code == data.destination_station_code.strip().upper())).first()
    if not dest_st:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination station '{data.destination_station_code}' not found.",
        )

    if src_st.id == dest_st.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source and destination stations cannot be the same.",
        )

    train = Train(
        train_number=train_num_clean,
        train_name=data.train_name.strip(),
        source_station_id=src_st.id,
        destination_station_id=dest_st.id,
        departure_time=data.departure_time,
        arrival_time=data.arrival_time,
        base_fare=data.base_fare,
        total_seats=data.total_seats,
        is_active=True,
    )
    session.add(train)
    session.commit()
    session.refresh(train)

    # Add stops if provided, or default origin + destination stops
    if data.stops:
        for stop_in in data.stops:
            st = session.exec(select(Station).where(Station.code == stop_in.station_code.strip().upper())).first()
            if not st:
                continue
            t_stop = TrainStop(
                train_id=train.id,
                station_id=st.id,
                stop_sequence=stop_in.stop_sequence,
                arrival_time=stop_in.arrival_time,
                departure_time=stop_in.departure_time,
                distance_km=stop_in.distance_km,
                fare_from_source=stop_in.fare_from_source,
            )
            session.add(t_stop)
    else:
        # Default stops
        s1 = TrainStop(
            train_id=train.id,
            station_id=src_st.id,
            stop_sequence=1,
            arrival_time=None,
            departure_time=train.departure_time,
            distance_km=0.0,
            fare_from_source=0.0,
        )
        s2 = TrainStop(
            train_id=train.id,
            station_id=dest_st.id,
            stop_sequence=2,
            arrival_time=train.arrival_time,
            departure_time=None,
            distance_km=400.0,
            fare_from_source=train.base_fare,
        )
        session.add_all([s1, s2])

    # Pre-populate 14 days of seat inventory
    today = date.today()
    for offset in range(14):
        j_date = (today + timedelta(days=offset)).isoformat()
        inv = SeatInventory(
            train_id=train.id,
            journey_date=j_date,
            total_seats=train.total_seats,
            available_seats=train.total_seats,
            booked_seats=0,
            version=1,
        )
        session.add(inv)

    session.commit()
    session.refresh(train)
    return format_train_response(session, train)


def update_train(session: Session, train_id: int, data: TrainUpdate) -> TrainResponse:
    """Update train attributes such as fare, timing, seats, or active status."""
    train = session.get(Train, train_id)
    if not train:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Train not found.")

    if data.train_name is not None:
        train.train_name = data.train_name.strip()
    if data.departure_time is not None:
        train.departure_time = data.departure_time
    if data.arrival_time is not None:
        train.arrival_time = data.arrival_time
    if data.base_fare is not None:
        train.base_fare = data.base_fare
    if data.total_seats is not None:
        diff = data.total_seats - train.total_seats
        train.total_seats = data.total_seats
        # Adjust future inventories where seats are available
        today_str = date.today().isoformat()
        future_invs = session.exec(
            select(SeatInventory).where(
                SeatInventory.train_id == train.id,
                SeatInventory.journey_date >= today_str,
            )
        ).all()
        for inv in future_invs:
            inv.total_seats = data.total_seats
            inv.available_seats = max(0, inv.available_seats + diff)
            session.add(inv)
    if data.is_active is not None:
        train.is_active = data.is_active

    train.updated_at = datetime.now(timezone.utc)
    session.add(train)
    session.commit()
    session.refresh(train)
    return format_train_response(session, train)


def deactivate_train(session: Session, train_id: int) -> TrainResponse:
    """Deactivate a train from booking and discovery."""
    train = session.get(Train, train_id)
    if not train:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Train not found.")
    train.is_active = False
    train.updated_at = datetime.now(timezone.utc)
    session.add(train)
    session.commit()
    session.refresh(train)
    return format_train_response(session, train)


def set_seat_inventory(session: Session, data: SeatInventoryUpdate) -> SeatInventory:
    """Manually update or set seat availability for a train on a specific journey date."""
    train = session.get(Train, data.train_id)
    if not train:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Train not found.")

    inv = session.exec(
        select(SeatInventory).where(
            SeatInventory.train_id == data.train_id,
            SeatInventory.journey_date == data.journey_date,
        )
    ).first()

    if inv:
        inv.total_seats = data.total_seats
        inv.available_seats = data.available_seats
        inv.booked_seats = max(0, data.total_seats - data.available_seats)
        inv.version += 1
        inv.updated_at = datetime.now(timezone.utc)
    else:
        inv = SeatInventory(
            train_id=data.train_id,
            journey_date=data.journey_date,
            total_seats=data.total_seats,
            available_seats=data.available_seats,
            booked_seats=max(0, data.total_seats - data.available_seats),
            version=1,
        )
    session.add(inv)
    session.commit()
    session.refresh(inv)
    return inv
