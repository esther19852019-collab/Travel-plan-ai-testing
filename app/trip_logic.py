from datetime import date


def calculate_trip_days(start_date: date, end_date: date) -> int:
    """Calculate the number of days in a trip.

    The start date is included in the calculation.
    """
    if start_date > end_date:
        raise ValueError("start_date must be before or equal to end_date")

    return (end_date - start_date).days + 1


def trips_overlap(
    start_date: date,
    end_date: date,
    other_start_date: date,
    other_end_date: date,
) -> bool:
    """Check whether two trips overlap."""

    if start_date > end_date:
        raise ValueError("Invalid first trip date range")

    if other_start_date > other_end_date:
        raise ValueError("Invalid second trip date range")

    return (
        start_date <= other_end_date
        and other_start_date <= end_date
    )