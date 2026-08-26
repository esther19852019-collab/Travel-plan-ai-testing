from datetime import date

from pydantic import BaseModel, Field, model_validator

class TripCreate(BaseModel):
    destination: str = Field(min_length=1)
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def check_date_range(self):
        if self.start_date > self.end_date:
            raise ValueError("start_date must be before or equal to end_date")
        return self
        
    travelers: int = Field(gt=0)
    budget: float|None = Field(default=None,ge=0)
    interests: list[str] = Field(default_factory=list)

class TripResponse(TripCreate):
    id: int
    days: int