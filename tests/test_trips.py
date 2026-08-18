from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# POST/trips - Create a new trip
def test_create_trip():
    response = client.post(
        "/trips",
        json={
            "destination": "London",
            "start_date": "2026-10-01",
            "end_date": "2026-10-05",
            "travelers": 2,
            "budget": 1200,
            "interests": ["food", "museum"],
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["destination"] == "London"
    assert data["travelers"] == 2
    assert data["budget"] == 1200

# GET/trips - Get all trips
def test_get_trips():
    response = client.get("/trips")

    assert response.status_code == 200
    assert isinstance(response.json(), list)

# GET/trips/{trip_id} - Get a trip by ID
def test_get_trip_by_id():
    response = client.get("/trips/1")

    assert response.status_code == 200
    data = response.json()

    assert data["destination"] == "London"

# GET/trips/{trip_id} - Get a trip by ID (not found)
def test_get_trip_not_found():
    response = client.get("/trips/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Trip not found"

# PUT/trips/{trip_id} - Update a trip
def test_update_trip():
    response = client.put(
        "/trips/1",
        json={
            "destination": "Paris",
            "start_date": "2026-10-01",
            "end_date": "2026-10-05",
            "travelers": 3,
            "budget": 1500,
            "interests": ["food", "museum"]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["destination"] == "Paris"
    assert data["travelers"] == 3
    assert data["budget"] == 1500

# DELETE/trips/{trip_id} - Delete a trip
def test_delete_trip():
    response = client.delete("/trips/1")

    assert response.status_code == 204

# DELETE/trips/{trip_id} - Delete a trip (not found)
def test_get_deleted_trip():
    response = client.get("/trips/1")

    assert response.status_code == 404
    assert response.json()["detail"] == "Trip not found"