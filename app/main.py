from fastapi import FastAPI, status, HTTPException, Depends
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.trip import TripCreate, TripResponse
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.core.database import get_db
from app.models.user import User
from app.models.trip import Trip
from app.trip_logic import calculate_trip_days, trips_overlap


app = FastAPI(title="Travel Plan API")


# ============================================================
# AUTHENTICATION
# ============================================================

def get_current_user(
    email: str = Depends(decode_access_token),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Travel Plan API is running"
    }


# ============================================================
# AUTH - REGISTER
# ============================================================

@app.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    hashed_password = hash_password(user.password)

    new_user = User(
        email=user.email,
        password=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ============================================================
# AUTH - LOGIN
# ============================================================

@app.post("/auth/login")
def login_user(
    user: UserLogin,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not verify_password(
        user.password,
        existing_user.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(
        data={
            "sub": existing_user.email
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# ============================================================
# AUTH - CURRENT USER
# ============================================================

@app.get("/auth/me")
def get_me(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "email": current_user.email,
    }


# ============================================================
# TRIPS - CREATE
# ============================================================

@app.post(
    "/trips",
    response_model=TripResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_trip(
    trip: TripCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Check overlapping trips belonging to the current user
    existing_trips = (
        db.query(Trip)
        .filter(Trip.user_id == current_user.id)
        .all()
    )

    for existing_trip in existing_trips:
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

    days = calculate_trip_days(
        trip.start_date,
        trip.end_date,
    )

    new_trip = Trip(
        destination=trip.destination,
        start_date=trip.start_date,
        end_date=trip.end_date,
        travelers=trip.travelers,
        budget=trip.budget,
        interests=trip.interests,
        user_id=current_user.id,
    )

    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)

    return TripResponse(
        id=new_trip.id,
        user_id=new_trip.user_id,
        destination=new_trip.destination,
        start_date=new_trip.start_date,
        end_date=new_trip.end_date,
        travelers=new_trip.travelers,
        budget=new_trip.budget,
        interests=new_trip.interests,
        days=days,
    )


# ============================================================
# TRIPS - GET ALL CURRENT USER'S TRIPS
# ============================================================

@app.get(
    "/trips",
    response_model=list[TripResponse],
)
def get_trips(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_trips = (
        db.query(Trip)
        .filter(Trip.user_id == current_user.id)
        .all()
    )

    return [
        TripResponse(
            id=trip.id,
            user_id=trip.user_id,
            destination=trip.destination,
            start_date=trip.start_date,
            end_date=trip.end_date,
            travelers=trip.travelers,
            budget=trip.budget,
            interests=trip.interests,
            days=calculate_trip_days(
                trip.start_date,
                trip.end_date,
            ),
        )
        for trip in user_trips
    ]


# ============================================================
# TRIPS - GET ONE
# ============================================================

@app.get(
    "/trips/{trip_id}",
    response_model=TripResponse,
)
def get_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    trip = (
        db.query(Trip)
        .filter(
            Trip.id == trip_id,
            Trip.user_id == current_user.id,
        )
        .first()
    )

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )

    return TripResponse(
        id=trip.id,
        user_id=trip.user_id,
        destination=trip.destination,
        start_date=trip.start_date,
        end_date=trip.end_date,
        travelers=trip.travelers,
        budget=trip.budget,
        interests=trip.interests,
        days=calculate_trip_days(
            trip.start_date,
            trip.end_date,
        ),
    )


# ============================================================
# TRIPS - UPDATE
# ============================================================

@app.put(
    "/trips/{trip_id}",
    response_model=TripResponse,
)
def update_trip(
    trip_id: int,
    trip_update: TripCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    trip = (
        db.query(Trip)
        .filter(
            Trip.id == trip_id,
            Trip.user_id == current_user.id,
        )
        .first()
    )

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )

    # Check overlap with other trips belonging to this user
    existing_trips = (
        db.query(Trip)
        .filter(
            Trip.user_id == current_user.id,
            Trip.id != trip_id,
        )
        .all()
    )

    for existing_trip in existing_trips:
        if trips_overlap(
            trip_update.start_date,
            trip_update.end_date,
            existing_trip.start_date,
            existing_trip.end_date,
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Trip dates overlap with an existing trip",
            )

    trip.destination = trip_update.destination
    trip.start_date = trip_update.start_date
    trip.end_date = trip_update.end_date
    trip.travelers = trip_update.travelers
    trip.budget = trip_update.budget
    trip.interests = trip_update.interests

    db.commit()
    db.refresh(trip)

    days = calculate_trip_days(
        trip.start_date,
        trip.end_date,
    )

    return TripResponse(
        id=trip.id,
        user_id=trip.user_id,
        destination=trip.destination,
        start_date=trip.start_date,
        end_date=trip.end_date,
        travelers=trip.travelers,
        budget=trip.budget,
        interests=trip.interests,
        days=days,
    )


# ============================================================
# TRIPS - DELETE
# ============================================================

@app.delete(
    "/trips/{trip_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    trip = (
        db.query(Trip)
        .filter(
            Trip.id == trip_id,
            Trip.user_id == current_user.id,
        )
        .first()
    )

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )

    db.delete(trip)
    db.commit()

    return