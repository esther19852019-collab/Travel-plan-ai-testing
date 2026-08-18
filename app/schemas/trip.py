from datetime import date

from pydantic import BaseModel, Field

class TripCreate(BaseModel):
    destination: str = Field(min_length=1)
    start_date: date
    end_date: date
    travelers: int = Field(gt=0)
    budget: float|None = Field(default=None,ge=0)
    interests: list[str] = Field(default_factory=list)

class TripResponse(TripCreate):
    id: int