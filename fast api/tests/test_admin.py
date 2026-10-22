from fastapi.testclient import TestClient


def test_non_admin_cannot_create_station(client: TestClient, passenger_headers: dict):
    response = client.post(
        "/api/v1/admin/stations",
        headers=passenger_headers,
        json={"code": "PUNE", "name": "Pune Junction", "city": "Pune", "state": "Maharashtra"},
    )
    assert response.status_code == 403
    assert "Administrative privileges required" in response.json()["detail"]


def test_admin_can_create_station(client: TestClient, admin_headers: dict):
    response = client.post(
        "/api/v1/admin/stations",
        headers=admin_headers,
        json={"code": "BSB", "name": "Varanasi Junction", "city": "Varanasi", "state": "Uttar Pradesh"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "BSB"
    assert data["city"] == "Varanasi"


def test_admin_can_create_train(client: TestClient, admin_headers: dict):
    response = client.post(
        "/api/v1/admin/trains",
        headers=admin_headers,
        json={
            "train_number": "22436",
            "train_name": "Vande Bharat Express",
            "source_station_code": "NDLS",
            "destination_station_code": "CNB",
            "departure_time": "06:00",
            "arrival_time": "10:08",
            "base_fare": 1150.0,
            "total_seats": 52,
            "stops": [
                {"station_code": "NDLS", "stop_sequence": 1, "departure_time": "06:00", "distance_km": 0.0, "fare_from_source": 0.0},
                {"station_code": "CNB", "stop_sequence": 2, "arrival_time": "10:08", "distance_km": 440.0, "fare_from_source": 1150.0},
            ],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["train_number"] == "22436"
    assert data["base_fare"] == 1150.0
    assert data["total_seats"] == 52
    assert len(data["stops"]) == 2


def test_admin_can_update_train(client: TestClient, admin_headers: dict):
    response = client.put(
        "/api/v1/admin/trains/1",
        headers=admin_headers,
        json={"train_name": "Updated Shatabdi Express", "base_fare": 820.0},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["train_name"] == "Updated Shatabdi Express"
    assert data["base_fare"] == 820.0


def test_admin_can_deactivate_train(client: TestClient, admin_headers: dict):
    response = client.patch(
        "/api/v1/admin/trains/1/deactivate",
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_admin_can_update_seat_inventory(client: TestClient, admin_headers: dict):
    from datetime import date, timedelta
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    response = client.post(
        "/api/v1/admin/inventory",
        headers=admin_headers,
        json={
            "train_id": 1,
            "journey_date": tomorrow,
            "total_seats": 25,
            "available_seats": 25,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["available_seats"] == 25
