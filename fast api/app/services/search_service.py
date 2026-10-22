from datetime import datetime, date
from typing import List, Optional
from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.station import Station
from app.models.train import Train
from app.models.schedule import TrainStop
from app.models.inventory import SeatInventory
from app.schemas.search import TrainSearchResult, TrainSearchResponse, SeatAvailabilityResponse


def find_station_by_query(session: Session, query: str) -> Optional[Station]:
    """Find station by code or case-insensitive name."""
    query_clean = query.strip()
    station = session.exec(select(Station).where(Station.code == query_clean.upper())).first()
    if not station:
        station = session.exec(select(Station).where(Station.name.ilike(f"%{query_clean}%"))).first()
    return station


def get_or_create_seat_inventory(session: Session, train: Train, journey_date_str: str) -> SeatInventory:
    """Get seat inventory for a train on a given date, or lazily initialize if missing."""
    inv = session.exec(
        select(SeatInventory).where(
            SeatInventory.train_id == train.id,
            SeatInventory.journey_date == journey_date_str,
        )
    ).first()

    if not inv:
        inv = SeatInventory(
            train_id=train.id,
            journey_date=journey_date_str,
            total_seats=train.total_seats,
            available_seats=train.total_seats,
            booked_seats=0,
            version=1,
        )
        session.add(inv)
        session.commit()
        session.refresh(inv)
    return inv


def search_trains(
    session: Session,
    source_query: str,
    destination_query: str,
    journey_date_str: str,
) -> TrainSearchResponse:
    """Search trains connecting source and destination stations on a specified date."""
    if not source_query or not destination_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source and destination stations are required.",
        )

    # Validate journey date format and ensure it is not in the past
    try:
        j_date = datetime.strptime(journey_date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid journey date format. Please use YYYY-MM-DD format.",
        )

    if j_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Journey date cannot be in the past.",
        )

    source_station = find_station_by_query(session, source_query)
    if not source_station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source station '{source_query}' was not found in the system.",
        )

    destination_station = find_station_by_query(session, destination_query)
    if not destination_station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination station '{destination_query}' was not found in the system.",
        )

    if source_station.id == destination_station.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source station and destination station cannot be the same.",
        )

    # Retrieve all active trains
    active_trains = session.exec(select(Train).where(Train.is_active == True)).all()
    results: List[TrainSearchResult] = []

    for train in active_trains:
        is_match = False
        dep_time = train.departure_time
        arr_time = train.arrival_time
        fare = train.base_fare

        # Case 1: Direct origin to destination
        if train.source_station_id == source_station.id and train.destination_station_id == destination_station.id:
            is_match = True
        else:
            # Case 2: Intermediate stops evaluation
            stops = session.exec(
                select(TrainStop).where(TrainStop.train_id == train.id).order_by(TrainStop.stop_sequence)
            ).all()

            src_stop = next((s for s in stops if s.station_id == source_station.id), None)
            dst_stop = next((s for s in stops if s.station_id == destination_station.id), None)

            if src_stop and dst_stop and src_stop.stop_sequence < dst_stop.stop_sequence:
                is_match = True
                dep_time = src_stop.departure_time or train.departure_time
                arr_time = dst_stop.arrival_time or train.arrival_time
                if dst_stop.fare_from_source > 0:
                    fare = max(100.0, dst_stop.fare_from_source - src_stop.fare_from_source)

        if is_match:
            inventory = get_or_create_seat_inventory(session, train, journey_date_str)
            seat_status = "AVAILABLE" if inventory.available_seats > 0 else "FULL"

            results.append(
                TrainSearchResult(
                    train_id=train.id,
                    train_number=train.train_number,
                    train_name=train.train_name,
                    source_station_code=source_station.code,
                    source_station_name=source_station.name,
                    destination_station_code=destination_station.code,
                    destination_station_name=destination_station.name,
                    departure_time=dep_time,
                    arrival_time=arr_time,
                    journey_date=journey_date_str,
                    fare=round(fare, 2),
                    total_seats=inventory.total_seats,
                    available_seats=inventory.available_seats,
                    status=seat_status,
                )
            )

    return TrainSearchResponse(
        query_source=source_station.name,
        query_destination=destination_station.name,
        journey_date=journey_date_str,
        total_trains=len(results),
        trains=results,
    )


def get_seat_availability(session: Session, train_id: int, journey_date_str: str) -> SeatAvailabilityResponse:
    """Retrieve current seat availability for a specific train and date."""
    train = session.get(Train, train_id)
    if not train:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Train not found.")

    try:
        datetime.strptime(journey_date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid journey date format. Please use YYYY-MM-DD format.",
        )

    inv = get_or_create_seat_inventory(session, train, journey_date_str)
    return SeatAvailabilityResponse(
        train_id=train.id,
        train_number=train.train_number,
        train_name=train.train_name,
        journey_date=journey_date_str,
        total_seats=inv.total_seats,
        available_seats=inv.available_seats,
        booked_seats=inv.booked_seats,
        is_available=inv.available_seats > 0,
    )
