from datetime import datetime, date, timedelta, timezone
from sqlmodel import Session, select
from app.config import settings
from app.models.user import User
from app.models.station import Station
from app.models.train import Train
from app.models.schedule import TrainStop
from app.models.inventory import SeatInventory
from app.utils.security import hash_password


def seed_initial_data(session: Session) -> None:
    """Seed initial administrator, standard stations, sample trains, and seat inventories."""
    # 1. Admin User
    admin = session.exec(select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL)).first()
    if not admin:
        admin = User(
            email=settings.FIRST_SUPERUSER_EMAIL,
            full_name="System Administrator",
            hashed_password=hash_password(settings.FIRST_SUPERUSER_PASSWORD),
            role="admin",
            is_active=True,
        )
        session.add(admin)
        session.commit()
        session.refresh(admin)

    # 2. Key Railway Stations
    station_data = [
        {"code": "NDLS", "name": "New Delhi Railway Station", "city": "New Delhi", "state": "Delhi"},
        {"code": "CNB", "name": "Kanpur Central", "city": "Kanpur", "state": "Uttar Pradesh"},
        {"code": "LKO", "name": "Lucknow Charbagh", "city": "Lucknow", "state": "Uttar Pradesh"},
        {"code": "BCT", "name": "Mumbai Central", "city": "Mumbai", "state": "Maharashtra"},
        {"code": "HWH", "name": "Howrah Junction", "city": "Kolkata", "state": "West Bengal"},
    ]

    station_map = {}
    for data in station_data:
        station = session.exec(select(Station).where(Station.code == data["code"])).first()
        if not station:
            station = Station(**data)
            session.add(station)
            session.commit()
            session.refresh(station)
        station_map[data["code"]] = station

    # 3. Challenge Train: New Delhi to Kanpur Central (Lucknow Swarna Shatabdi Express)
    shatabdi = session.exec(select(Train).where(Train.train_number == "12004")).first()
    if not shatabdi:
        shatabdi = Train(
            train_number="12004",
            train_name="Lucknow Swarna Shatabdi Express",
            source_station_id=station_map["NDLS"].id,
            destination_station_id=station_map["CNB"].id,
            departure_time="06:10",
            arrival_time="11:20",
            base_fare=750.0,
            total_seats=60,
            is_active=True,
        )
        session.add(shatabdi)
        session.commit()
        session.refresh(shatabdi)

        # Train Stops
        stops = [
            TrainStop(
                train_id=shatabdi.id,
                station_id=station_map["NDLS"].id,
                stop_sequence=1,
                arrival_time=None,
                departure_time="06:10",
                distance_km=0.0,
                fare_from_source=0.0,
            ),
            TrainStop(
                train_id=shatabdi.id,
                station_id=station_map["CNB"].id,
                stop_sequence=2,
                arrival_time="11:20",
                departure_time="11:25",
                distance_km=440.0,
                fare_from_source=750.0,
            ),
            TrainStop(
                train_id=shatabdi.id,
                station_id=station_map["LKO"].id,
                stop_sequence=3,
                arrival_time="12:40",
                departure_time=None,
                distance_km=512.0,
                fare_from_source=860.0,
            ),
        ]
        session.add_all(stops)
        session.commit()

    # 4. Additional Sample Train: New Delhi to Mumbai Central (Rajdhani Express)
    rajdhani = session.exec(select(Train).where(Train.train_number == "12952")).first()
    if not rajdhani:
        rajdhani = Train(
            train_number="12952",
            train_name="Mumbai Tejas Rajdhani Express",
            source_station_id=station_map["NDLS"].id,
            destination_station_id=station_map["BCT"].id,
            departure_time="16:55",
            arrival_time="08:35",
            base_fare=2250.0,
            total_seats=50,
            is_active=True,
        )
        session.add(rajdhani)
        session.commit()
        session.refresh(rajdhani)

    # 5. Pre-populate initial seat inventory for the next 14 days
    today = date.today()
    all_trains = session.exec(select(Train)).all()
    for train in all_trains:
        for offset in range(14):
            journey_date_str = (today + timedelta(days=offset)).isoformat()
            existing_inv = session.exec(
                select(SeatInventory).where(
                    SeatInventory.train_id == train.id,
                    SeatInventory.journey_date == journey_date_str,
                )
            ).first()
            if not existing_inv:
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
