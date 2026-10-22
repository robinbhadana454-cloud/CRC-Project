import os
from datetime import date, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine, select

from app.main import app
from app.database import get_session
from app.models import User, Station, Train, TrainStop, SeatInventory
from app.utils.security import hash_password, create_access_token

TEST_DB_FILE = "test_railconnect.db"
TEST_DATABASE_URL = f"sqlite:///./{TEST_DB_FILE}"


@pytest.fixture(name="engine", scope="function")
def engine_fixture():
    """Create a clean isolated SQLite database per test function."""
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass

    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False, "timeout": 30},
    )
    SQLModel.metadata.create_all(engine)

    # Seed baseline test data
    with Session(engine) as session:
        admin = User(
            email="admin@test.com",
            full_name="Test Admin",
            hashed_password=hash_password("AdminPass123!"),
            role="admin",
            is_active=True,
        )
        passenger = User(
            email="passenger@test.com",
            full_name="Rahul Sharma",
            hashed_password=hash_password("PassengerPass123!"),
            role="passenger",
            is_active=True,
        )
        session.add_all([admin, passenger])
        session.commit()

        ndls = Station(code="NDLS", name="New Delhi", city="New Delhi", state="Delhi")
        cnb = Station(code="CNB", name="Kanpur Central", city="Kanpur", state="Uttar Pradesh")
        lko = Station(code="LKO", name="Lucknow Charbagh", city="Lucknow", state="Uttar Pradesh")
        bct = Station(code="BCT", name="Mumbai Central", city="Mumbai", state="Maharashtra")
        session.add_all([ndls, cnb, lko, bct])
        session.commit()
        session.refresh(ndls)
        session.refresh(cnb)

        train = Train(
            train_number="12004",
            train_name="Lucknow Shatabdi",
            source_station_id=ndls.id,
            destination_station_id=cnb.id,
            departure_time="06:10",
            arrival_time="11:20",
            base_fare=750.0,
            total_seats=10,
            is_active=True,
        )
        session.add(train)
        session.commit()
        session.refresh(train)

        s1 = TrainStop(train_id=train.id, station_id=ndls.id, stop_sequence=1, departure_time="06:10", distance_km=0.0, fare_from_source=0.0)
        s2 = TrainStop(train_id=train.id, station_id=cnb.id, stop_sequence=2, arrival_time="11:20", distance_km=440.0, fare_from_source=750.0)
        session.add_all([s1, s2])

        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        inv = SeatInventory(
            train_id=train.id,
            journey_date=tomorrow,
            total_seats=10,
            available_seats=10,
            booked_seats=0,
            version=1,
        )
        session.add(inv)
        session.commit()

    yield engine

    engine.dispose()
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass


@pytest.fixture(name="session")
def session_fixture(engine):
    """Provide a database session for test verification."""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(engine):
    """Test client where each request creates its own fresh session from the engine."""
    def get_session_override():
        with Session(engine) as s:
            yield s

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="admin_token")
def admin_token_fixture(session: Session):
    admin = session.exec(select(User).where(User.email == "admin@test.com")).first()
    return create_access_token({"sub": str(admin.id), "email": admin.email, "role": "admin"})


@pytest.fixture(name="passenger_token")
def passenger_token_fixture(session: Session):
    passenger = session.exec(select(User).where(User.email == "passenger@test.com")).first()
    return create_access_token({"sub": str(passenger.id), "email": passenger.email, "role": "passenger"})


@pytest.fixture(name="admin_headers")
def admin_headers_fixture(admin_token: str):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(name="passenger_headers")
def passenger_headers_fixture(passenger_token: str):
    return {"Authorization": f"Bearer {passenger_token}"}
