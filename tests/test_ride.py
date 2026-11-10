"""Part 3: Ride is an event with data and owns the fee rule."""

from datetime import timedelta

import pytest

from bikeshare import Bike, ReceiptPrinter, Ride, Rider, Station
from tests.helpers import T0


def make_ride() -> Ride:
    return Ride(Rider("Ali"), Bike("B1"), Station("Chilonzor", 10), T0)


@pytest.mark.parametrize(
    "duration, fee",
    [
        (timedelta(minutes=15), 0),
        (timedelta(minutes=15, seconds=1), 500),
        (timedelta(minutes=20), 500),
        (timedelta(minutes=20, seconds=1), 1_000),
        (timedelta(hours=10), 20_000),
    ],
    ids=["15:00 -> 0", "15:01 -> 500", "20:00 -> 500", "20:01 -> 1000", "very long -> 20000 cap"],
)
def test_if_ride_lasted_duration_fee_is(duration, fee):
    ride = make_ride()
    ride.finish(Station("Yunusobod", 10), T0 + duration)
    assert ride.fee() == fee


def test_if_end_before_start_raises_value_error():
    ride = make_ride()
    with pytest.raises(ValueError):
        ride.finish(Station("Yunusobod", 10), T0 - timedelta(minutes=1))
    assert ride.is_active


def test_if_ride_not_finished_fee_raises_value_error():
    with pytest.raises(ValueError):
        make_ride().fee()


def test_if_receipt_printed_shows_route_minutes_fee(capsys):
    ride = make_ride()
    ride.finish(Station("Yunusobod", 10), T0 + timedelta(minutes=23))
    ReceiptPrinter.print(ride)
    assert capsys.readouterr().out == "Chilonzor → Yunusobod, 23 min, 1 000 sum\n"
