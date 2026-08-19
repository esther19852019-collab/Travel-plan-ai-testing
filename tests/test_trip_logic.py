from datetime import date

import pytest

from app.trip_logic import calculate_trip_days, trips_overlap


# calculate_trip_days tests

def test_calculate_trip_days_normal_trip():
    result = calculate_trip_days(
        date(2026, 10, 1),
        date(2026, 10, 5),
    )

    assert result == 5


def test_calculate_trip_days_same_day():
    result = calculate_trip_days(
        date(2026, 10, 1),
        date(2026, 10, 1),
    )

    assert result == 1


def test_calculate_trip_days_invalid_range():
    with pytest.raises(ValueError):
        calculate_trip_days(
            date(2026, 10, 5),
            date(2026, 10, 1),
        )


# trips_overlap tests

def test_trips_overlap_when_dates_overlap():
    result = trips_overlap(
        date(2026, 10, 1),
        date(2026, 10, 5),
        date(2026, 10, 4),
        date(2026, 10, 8),
    )

    assert result is True


def test_trips_do_not_overlap():
    result = trips_overlap(
        date(2026, 10, 1),
        date(2026, 10, 5),
        date(2026, 10, 6),
        date(2026, 10, 8),
    )

    assert result is False


def test_trips_overlap_on_boundary_date():
    result = trips_overlap(
        date(2026, 10, 1),
        date(2026, 10, 5),
        date(2026, 10, 5),
        date(2026, 10, 8),
    )

    assert result is True


def test_trips_overlap_invalid_first_range():
    with pytest.raises(ValueError):
        trips_overlap(
            date(2026, 10, 5),
            date(2026, 10, 1),
            date(2026, 10, 8),
            date(2026, 10, 10),
        )


def test_trips_overlap_invalid_second_range():
    with pytest.raises(ValueError):
        trips_overlap(
            date(2026, 10, 1),
            date(2026, 10, 5),
            date(2026, 10, 10),
            date(2026, 10, 8),
        )