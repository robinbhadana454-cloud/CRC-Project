import concurrent.futures
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models import SeatInventory


def test_concurrent_booking_prevents_double_booking(session: Session, client: TestClient, passenger_headers: dict):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    # Configure exactly 1 available seat
    inv = session.exec(
        select(SeatInventory).where(SeatInventory.train_id == 1, SeatInventory.journey_date == tomorrow)
    ).first()
    inv.total_seats = 1
    inv.available_seats = 1
    inv.booked_seats = 0
    inv.version = 1
    session.add(inv)
    session.commit()

    def attempt_booking(passenger_name: str):
        # Dedicated client call for this thread
        return client.post(
            "/api/v1/bookings/",
            headers=passenger_headers,
            json={
                "train_id": 1,
                "journey_date": tomorrow,
                "passengers": [{"name": passenger_name, "age": 25, "gender": "M"}],
            },
        )

    # Launch two simultaneous booking requests for the last remaining seat
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(attempt_booking, "Passenger Fast")
        f2 = executor.submit(attempt_booking, "Passenger Furious")
        res1 = f1.result()
        res2 = f2.result()

    statuses = [res1.status_code, res2.status_code]

    # Exactly one request must succeed (201 Created)
    assert 201 in statuses
    # The other request must be rejected (400 Insufficient seats or 409 Conflict)
    assert (400 in statuses) or (409 in statuses)

    # Confirm inventory is never overbooked
    session.refresh(inv)
    assert inv.available_seats == 0
    assert inv.booked_seats == 1
