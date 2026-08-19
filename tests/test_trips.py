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


@pytest.fixture
def created_trip(trip_data):
    response = client.post("/trips", json=trip_data)

    assert response.status_code == 201

    return response.json()


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
def test_get_trip_by_id(created_trip):
    trip_id = created_trip["id"]

    response = client.get(f"/trips/{trip_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == trip_id
    assert data["destination"] == created_trip["destination"]
    assert data["travelers"] == created_trip["travelers"]
    assert data["budget"] == created_trip["budget"]


# GET /trips/{trip_id} - Trip not found
def test_get_trip_not_found():
    response = client.get("/trips/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Trip not found"


# PUT /trips/{trip_id} - Update a trip
def test_update_trip(created_trip):
    trip_id = created_trip["id"]

    updated_trip_data = {
        "destination": "London",
        "start_date": "2026-11-01",
        "end_date": "2026-11-05",
        "travelers": 3,
        "budget": 1500,
        "interests": ["food", "museum", "shopping"],
    }

    response = client.put(
        f"/trips/{trip_id}",
        json=updated_trip_data,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == trip_id
    assert data["destination"] == updated_trip_data["destination"]
    assert data["start_date"] == updated_trip_data["start_date"]
    assert data["end_date"] == updated_trip_data["end_date"]
    assert data["travelers"] == updated_trip_data["travelers"]
    assert data["budget"] == updated_trip_data["budget"]
    assert data["interests"] == updated_trip_data["interests"]


# GET /trips/{trip_id} - Verify updated trip
def test_get_updated_trip(created_trip):
    trip_id = created_trip["id"]

    updated_trip_data = {
        "destination": "London",
        "start_date": "2026-11-01",
        "end_date": "2026-11-05",
        "travelers": 3,
        "budget": 1500,
        "interests": ["food", "museum", "shopping"],
    }

    update_response = client.put(
        f"/trips/{trip_id}",
        json=updated_trip_data,
    )

    assert update_response.status_code == 200

    response = client.get(f"/trips/{trip_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == trip_id
    assert data["destination"] == updated_trip_data["destination"]
    assert data["start_date"] == updated_trip_data["start_date"]
    assert data["end_date"] == updated_trip_data["end_date"]
    assert data["travelers"] == updated_trip_data["travelers"]
    assert data["budget"] == updated_trip_data["budget"]
    assert data["interests"] == updated_trip_data["interests"]

# PUT /trips/{trip_id} - Trip not found
def test_update_trip_not_found(trip_data):
    response = client.put(
        "/trips/999999",
        json=trip_data,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Trip not found"

# DELETE /trips/{trip_id} - Delete a trip
def test_delete_trip(created_trip):
    trip_id = created_trip["id"]

    response = client.delete(f"/trips/{trip_id}")

    assert response.status_code == 204


# GET /trips/{trip_id} - Verify deleted trip
def test_get_deleted_trip(created_trip):
    trip_id = created_trip["id"]

    delete_response = client.delete(f"/trips/{trip_id}")

    assert delete_response.status_code == 204

    response = client.get(f"/trips/{trip_id}")

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

# GET / - Root endpoint
def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Travel Plan API is running"


# DELETE /trips/{trip_id} - Trip not found
def test_delete_trip_not_found():
    response = client.delete("/trips/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Trip not found"