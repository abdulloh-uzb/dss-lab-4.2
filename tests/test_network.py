"""Part 4: Network runs the ride: take bike and return bike."""

from datetime import timedelta
from types import SimpleNamespace

import pytest

from bikeshare import (
    BikeStatus,
    Network,
    NoActiveRideError,
    NoBikeError,
    RideActiveError,
    Rider,
    StationFullError,
)
from tests.helpers import T0, make_station


@pytest.fixture
def city():
    chilonzor = make_station("Chilonzor", 10, 4)  # 6 free docks
    yunusobod = make_station("Yunusobod", 10, 2)  # 8 free docks
    sergeli = make_station("Sergeli", 3, 3)       # full
    network = Network([chilonzor, yunusobod, sergeli])
    return SimpleNamespace(
        network=network, chilonzor=chilonzor, yunusobod=yunusobod, sergeli=sergeli, ali=Rider("Ali")
    )


def fail_twice(c):
    c.network.take(c.ali, c.chilonzor, T0)
    with pytest.raises(StationFullError):
        c.network.return_bike(c.ali, c.sergeli, T0 + timedelta(minutes=20))
    with pytest.raises(StationFullError) as error:
        c.network.return_bike(c.ali, c.sergeli, T0 + timedelta(minutes=22))
    return error.value


def test_if_no_active_ride_and_free_bike_new_ride_starts(city):
    ride = city.network.take(city.ali, city.chilonzor, T0)
    assert ride.bike.status is BikeStatus.IN_USE
    assert city.ali.active_ride is ride
    assert ride in city.network.rides
    assert len(city.chilonzor) == 3


def test_if_rider_has_active_ride_raises_ride_active_error(city):
    city.network.take(city.ali, city.chilonzor, T0)
    with pytest.raises(RideActiveError):
        city.network.take(city.ali, city.chilonzor, T0)
    assert len(city.chilonzor) == 3  # no second bike left the station


def test_if_station_without_free_bike_raises_no_bike_error(city):
    for dock in city.sergeli.docks:
        dock.bike.send_to_repair()  # bikes are there, but none can be taken
    with pytest.raises(NoBikeError):
        city.network.take(city.ali, city.sergeli, T0)
    assert city.ali.active_ride is None


def test_if_return_without_ride_raises_no_active_ride_error(city):
    with pytest.raises(NoActiveRideError):
        city.network.return_bike(city.ali, city.yunusobod, T0)


def test_if_return_to_free_dock_receipt_shows_fee(city, capsys):
    city.network.take(city.ali, city.chilonzor, T0)
    ride = city.network.return_bike(city.ali, city.yunusobod, T0 + timedelta(minutes=23))
    assert capsys.readouterr().out == "Chilonzor → Yunusobod, 23 min, 1 000 sum\n"
    assert city.ali.total_charged == 1_000
    assert ride.bike.status is BikeStatus.AVAILABLE


def test_if_station_full_raises_and_ride_keeps_running(city):
    ride = city.network.take(city.ali, city.chilonzor, T0)
    with pytest.raises(StationFullError) as error:
        city.network.return_bike(city.ali, city.sergeli, T0 + timedelta(minutes=20))
    assert error.value.redirect is None  # only 1 failure so far
    assert ride.is_active and city.ali.active_ride is ride
    assert ride.bike.status is BikeStatus.IN_USE
    assert len(city.sergeli) == 3


def test_if_same_ride_fails_twice_error_carries_redirect(city):
    error = fail_twice(city)
    assert error.redirect is city.yunusobod  # most free docks
    assert city.ali.active_ride.failed_returns == 2


def test_if_redirect_tie_picks_name_a_to_z():
    full = make_station("Sergeli", 2, 2)
    yunusobod = make_station("Yunusobod", 10, 2)  # 8 free
    mirobod = make_station("Mirobod", 10, 2)      # 8 free -> tie
    network = Network([full, yunusobod, mirobod])
    assert network.redirect_for(full) is mirobod


def test_if_new_ride_starts_with_zero_failures(city):
    city.network.take(city.ali, city.chilonzor, T0)
    with pytest.raises(StationFullError):
        city.network.return_bike(city.ali, city.sergeli, T0 + timedelta(minutes=5))
    city.network.return_bike(city.ali, city.yunusobod, T0 + timedelta(minutes=10))
    city.network.take(city.ali, city.chilonzor, T0 + timedelta(minutes=30))
    with pytest.raises(StationFullError) as error:
        city.network.return_bike(city.ali, city.sergeli, T0 + timedelta(minutes=35))
    assert error.value.redirect is None  # the counter lived in the old ride


def test_if_return_time_before_start_bike_stays_with_rider(city):
    ride = city.network.take(city.ali, city.chilonzor, T0)
    with pytest.raises(ValueError):
        city.network.return_bike(city.ali, city.yunusobod, T0 - timedelta(minutes=1))
    assert ride.is_active and ride.bike.status is BikeStatus.IN_USE
    assert len(city.yunusobod) == 2


def test_if_return_to_redirected_station_ride_closed_and_charged(city, capsys):
    error = fail_twice(city)
    ride = city.ali.active_ride
    city.network.return_bike(city.ali, error.redirect, T0 + timedelta(minutes=31))
    assert not ride.is_active and ride.end_station is city.yunusobod
    assert city.ali.active_ride is None
    assert city.ali.total_charged == ride.fee() == 2_000
    assert ride.bike.status is BikeStatus.AVAILABLE
    assert any(dock.bike is ride.bike for dock in city.yunusobod.docks)
    assert capsys.readouterr().out == "Chilonzor → Yunusobod, 31 min, 2 000 sum\n"


def test_if_report_prints_stations_biggest_free_first(city, capsys):
    city.network.report()
    assert capsys.readouterr().out == (
        "Yunusobod: 8 free docks\nChilonzor: 6 free docks\nSergeli: 0 free docks\n"
    )
