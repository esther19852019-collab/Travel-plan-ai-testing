
from fastapi import FastAPI, status, HTTPException

from app.schemas.trip import TripCreate, TripResponse
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.core.security import hash_password
from app.trip_logic import calculate_trip_days, trips_overlap

app = FastAPI(title="Travel Plan API")

trips: list[TripResponse] = []
users: list[dict] = []


@app.get("/")
def root():
    return {"message": "Travel Plan API is running"}

@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate):
    for existing_user in users:
        if existing_user["email"] == user.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
    user_id = len(users) +1
    hashed_password = hash_password(user.password)
    new_user = UserResponse(
        id=user_id,
        email=user.email,
    )
    users.append(
        {
            "id": user_id,
            "email": user.email,
            "password": hashed_password,
        }
    )

    return new_user



@app.post("/trips", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip(trip: TripCreate):
    for existing_trip in trips:
        if trips_overlap(
            trip.start_date,
            trip.end_date,
            existing_trip.start_date,
            existing_trip.end_date,
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Trip dates overlap with an existing trip",
            )

    trip_id = len(trips) + 1

    days = calculate_trip_days(
        trip.start_date,
        trip.end_date
    )

    new_trip = TripResponse(
        id=trip_id,
        days=days,
        **trip.model_dump(),
    )

    trips.append(new_trip)

    return new_trip

@app.post("/auth/login")
def login_user(user:UserLogin):
    for existing_user in users:
        if existing_user["email"] == user.email:
            if existing_user["password"] == user.password:
                return {
                    "message": "Login successful",
                    "email": existing_user.email,                    
                }

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )
        
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password"
    )

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
            days = calculate_trip_days(
                trip_update.start_date,
                trip_update.end_date
            )
            
            updated_trip = TripResponse(
                id=trip_id,
                days=days,
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