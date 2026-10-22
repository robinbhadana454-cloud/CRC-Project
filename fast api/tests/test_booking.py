from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models import User, SeatInventory
from app.utils.security import create_access_token


def test_book_ticket_success_and_seat_decrement(client: TestClient, passenger_headers: dict, session: Session):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    booking_payload = {
        "train_id": 1,
        "journey_date": tomorrow,
        "source_station_code": "NDLS",
        "destination_station_code": "CNB",
        "passengers": [
            {"name": "Amit Sharma", "age": 32, "gender": "M"},
            {"name": "Sneha Sharma", "age": 29, "gender": "F"},
        ],
    }

    response = client.post("/api/v1/bookings/", headers=passenger_headers, json=booking_payload)
    assert response.status_code == 201
    data = response.json()

    assert "pnr" in data
    assert len(data["pnr"]) == 10
    assert data["status"] == "CONFIRMED"
    assert data["payment_status"] == "PAID"
    assert data["total_fare"] == 1500.0  # 750 * 2
    assert len(data["passengers"]) == 2
    assert data["passengers"][0]["seat_number"] == "S-1"
    assert data["passengers"][1]["seat_number"] == "S-2"

    # Verify inventory was decremented in database
    inv = session.exec(
        select(SeatInventory).where(SeatInventory.train_id == 1, SeatInventory.journey_date == tomorrow)
    ).first()
    assert inv.available_seats == 8
    assert inv.booked_seats == 2


def test_view_own_bookings(client: TestClient, passenger_headers: dict):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    client.post(
        "/api/v1/bookings/",
        headers=passenger_headers,
        json={
            "train_id": 1,
            "journey_date": tomorrow,
            "passengers": [{"name": "Passenger One", "age": 25, "gender": "M"}],
        },
    )

    response = client.get("/api/v1/bookings/my-bookings", headers=passenger_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["train_number"] == "12004"


def test_view_and_cancel_booking_restores_seats(client: TestClient, passenger_headers: dict, session: Session):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    # Book ticket for 1 passenger
    book_res = client.post(
        "/api/v1/bookings/",
        headers=passenger_headers,
        json={
            "train_id": 1,
            "journey_date": tomorrow,
            "passengers": [{"name": "Single Passenger", "age": 40, "gender": "M"}],
        },
    )
    pnr = book_res.json()["pnr"]

    # Check available seats decreased
    inv_before = session.exec(
        select(SeatInventory).where(SeatInventory.train_id == 1, SeatInventory.journey_date == tomorrow)
    ).first()
    seats_before_cancel = inv_before.available_seats

    # View booking by PNR
    view_res = client.get(f"/api/v1/bookings/{pnr}", headers=passenger_headers)
    assert view_res.status_code == 200
    assert view_res.json()["pnr"] == pnr

    # Cancel booking
    cancel_res = client.post(f"/api/v1/bookings/{pnr}/cancel", headers=passenger_headers)
    assert cancel_res.status_code == 200
    cancel_data = cancel_res.json()
    assert cancel_data["status"] == "CANCELLED"
    assert cancel_data["refunded_amount"] == 750.0
    assert cancel_data["restored_seats"] == 1

    # Verify seat was restored in database
    session.refresh(inv_before)
    assert inv_before.available_seats == seats_before_cancel + 1

    # Attempting to cancel again must be rejected (prevent repeated seat release)
    repeat_cancel = client.post(f"/api/v1/bookings/{pnr}/cancel", headers=passenger_headers)
    assert repeat_cancel.status_code == 400
    assert "already cancelled" in repeat_cancel.json()["detail"]


def test_passenger_cannot_view_or_cancel_other_user_booking(client: TestClient, passenger_headers: dict, session: Session):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    # User 1 books ticket
    book_res = client.post(
        "/api/v1/bookings/",
        headers=passenger_headers,
        json={
            "train_id": 1,
            "journey_date": tomorrow,
            "passengers": [{"name": "User 1 Passenger", "age": 22, "gender": "F"}],
        },
    )
    pnr = book_res.json()["pnr"]

    # Create User 2
    user2 = User(
        email="user2@test.com",
        full_name="Second Passenger",
        hashed_password="somehash",
        role="passenger",
        is_active=True,
    )
    session.add(user2)
    session.commit()
    session.refresh(user2)

    user2_token = create_access_token({"sub": str(user2.id), "email": user2.email, "role": "passenger"})
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    # User 2 tries to view User 1's booking
    view_res = client.get(f"/api/v1/bookings/{pnr}", headers=user2_headers)
    assert view_res.status_code == 403
    assert "Access forbidden" in view_res.json()["detail"]

    # User 2 tries to cancel User 1's booking
    cancel_res = client.post(f"/api/v1/bookings/{pnr}/cancel", headers=user2_headers)
    assert cancel_res.status_code == 403
    assert "Access forbidden" in cancel_res.json()["detail"]


def test_booking_when_train_is_full_fails(client: TestClient, passenger_headers: dict, session: Session):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    # Set available seats to 1
    inv = session.exec(
        select(SeatInventory).where(SeatInventory.train_id == 1, SeatInventory.journey_date == tomorrow)
    ).first()
    inv.available_seats = 1
    session.add(inv)
    session.commit()

    # Try to book 2 seats
    response = client.post(
        "/api/v1/bookings/",
        headers=passenger_headers,
        json={
            "train_id": 1,
            "journey_date": tomorrow,
            "passengers": [
                {"name": "P1", "age": 30, "gender": "M"},
                {"name": "P2", "age": 28, "gender": "F"},
            ],
        },
    )
    assert response.status_code == 400
    assert "fully booked or insufficient seats" in response.json()["detail"]
