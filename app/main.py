from fastapi import FastAPI

app = FastAPI(title="Travel Plan API")


from fastapi import FastAPI, status

from app.schemas.trip import TripCreate, TripResponse

app = FastAPI(title="Travel Plan API")

trips: list[TripResponse] = []


@app.get("/")
def root():
    return {"message": "Travel Plan API is running"}


@app.post("/trips", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip(trip: TripCreate):
    trip_id = len(trips) + 1

    new_trip = TripResponse(
        id=trip_id,
        **trip.model_dump(),
    )

    trips.append(new_trip)

    return new_trip