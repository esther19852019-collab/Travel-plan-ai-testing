import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@pytest.fixture
def trip_data():
    return {
        "destination": "Paris",
        "start_date": "2026-10-01",
        "end_date": "2026-10-05",
        "travelers": 2,
        "budget": 1000,
        "interests": ["food", "museum"],
    }


# POST /trips - Create a new trip
def test_create_trip(trip_data):
    response = client.post("/trips", json=trip_data)

    assert response.status_code == 201

    data = response.json()

    assert data["destination"] == trip_data["destination"]
    assert data["travelers"] == trip_data["travelers"]
    assert data["budget"] == trip_data["budget"]


# GET /trips - Get all trips
def test_get_trips():
    response = client.get("/trips")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


# GET /trips/{trip_id} - Get one trip
def test_get_trip_by_id(trip_data):
    response = client.get("/trips/1")

    assert response.status_code == 200

    data = response.json()

    assert data["destination"] == trip_data["destination"]
    assert data["travelers"] == trip_data["travelers"]
    assert data["budget"] == trip_data["budget"]


# GET /trips/{trip_id} - Trip not found
def test_get_trip_not_found():
    response = client.get("/trips/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Trip not found"


# PUT /trips/{trip_id} - Update a trip
def test_update_trip(trip_data):
    response = client.put(
        "/trips/1",
        json={
            "destination": "Paris",
            "start_date": "2026-10-01",
            "end_date": "2026-10-05",
            "travelers": 3,
            "budget": 1500,
            "interests": ["food", "museum"],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["destination"] == "Paris"
    assert data["travelers"] == 3
    assert data["budget"] == 1500


# DELETE /trips/{trip_id} - Delete a trip
def test_delete_trip():
    response = client.delete("/trips/1")

    assert response.status_code == 204


# GET /trips/{trip_id} - Verify deleted trip
def test_get_deleted_trip():
    response = client.get("/trips/1")

    assert response.status_code == 404
    assert response.json()["detail"] == "Trip not found"


# Negative tests - invalid input
@pytest.mark.parametrize(
    "overrides",
    [
        {"travelers": 0},
        {"destination": None},
        {"budget": -100},
    ],
)
def test_create_trip_invalid_input(trip_data, overrides):
    data = trip_data.copy()

    for key, value in overrides.items():
        if value is None:
            data.pop(key)
        else:
            data[key] = value

    response = client.post("/trips", json=data)

    assert response.status_code == 422


# Negative test - invalid date range
def test_create_trip_invalid_date_range(trip_data):
    data = trip_data.copy()

    data["start_date"] = "2026-10-05"
    data["end_date"] = "2026-10-01"

    response = client.post("/trips", json=data)

    assert response.status_code == 422