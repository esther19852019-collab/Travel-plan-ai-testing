from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    destination: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    end_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    travelers: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    budget: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    interests: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    user = relationship(
        "User",
        back_populates="trips",
    )