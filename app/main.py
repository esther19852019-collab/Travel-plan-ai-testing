
from fastapi import FastAPI, status, HTTPException

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

@app.get("/trips", response_model=list[TripResponse])
def get_trips():
    return trips

@app.get("/trips/{trip_id}", response_model=TripResponse)
def get_trip(trip_id: int):
    for trip in trips:
        if trip.id == trip_id:
            return trip

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Trip not found"
    )


@app.put("/trips/{trip_id}", response_model=TripResponse)
def update_trip(trip_id: int, trip_update: TripCreate):
    for index, trip in enumerate(trips):
        if trip.id == trip_id:
            updated_trip = TripResponse(
                id=trip_id,
                **trip_update.model_dump()
            )

            trips[index]= updated_trip
            return updated_trip

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Trip not found"
    )

@app.delete("/trips/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(trip_id: int):
    for index, trip in enumerate(trips):
        if trip.id == trip_id:
            trips.pop(index)
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Trip not found"
    )