from datetime import date, timedelta
from fastapi.testclient import TestClient


def test_search_trains_successful(client: TestClient):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    response = client.get(
        "/api/v1/trains/search",
        params={
            "source_station": "NDLS",
            "destination_station": "CNB",
            "journey_date": tomorrow,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_trains"] >= 1
    train = data["trains"][0]
    assert train["train_number"] == "12004"
    assert train["source_station_code"] == "NDLS"
    assert train["destination_station_code"] == "CNB"
    assert train["departure_time"] == "06:10"
    assert train["arrival_time"] == "11:20"
    assert train["fare"] == 750.0
    assert train["available_seats"] == 10


def test_search_trains_invalid_source_station(client: TestClient):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    response = client.get(
        "/api/v1/trains/search",
        params={
            "source_station": "XYZ999",
            "destination_station": "CNB",
            "journey_date": tomorrow,
        },
    )
    assert response.status_code == 404
    assert "was not found" in response.json()["detail"]


def test_search_trains_invalid_destination_station(client: TestClient):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    response = client.get(
        "/api/v1/trains/search",
        params={
            "source_station": "NDLS",
            "destination_station": "XYZ999",
            "journey_date": tomorrow,
        },
    )
    assert response.status_code == 404
    assert "was not found" in response.json()["detail"]


def test_search_trains_past_date(client: TestClient):
    past_date = (date.today() - timedelta(days=2)).isoformat()
    response = client.get(
        "/api/v1/trains/search",
        params={
            "source_station": "NDLS",
            "destination_station": "CNB",
            "journey_date": past_date,
        },
    )
    assert response.status_code == 400
    assert "cannot be in the past" in response.json()["detail"]


def test_search_trains_same_source_and_destination(client: TestClient):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    response = client.get(
        "/api/v1/trains/search",
        params={
            "source_station": "NDLS",
            "destination_station": "NDLS",
            "journey_date": tomorrow,
        },
    )
    assert response.status_code == 400
    assert "cannot be the same" in response.json()["detail"]


def test_search_trains_no_matching_route(client: TestClient):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    # No train from Kanpur to Mumbai in test database
    response = client.get(
        "/api/v1/trains/search",
        params={
            "source_station": "CNB",
            "destination_station": "BCT",
            "journey_date": tomorrow,
        },
    )
    assert response.status_code == 200
    assert response.json()["total_trains"] == 0
