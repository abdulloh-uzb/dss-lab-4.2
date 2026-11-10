"""Part 2: Bike, Dock and Station protect their own rules."""

import pytest

from bikeshare import (
    Bike,
    BikeNotAvailableError,
    BikeStatus,
    Dock,
    DockOccupiedError,
    NoBikeError,
    Station,
)
from tests.helpers import make_station


def test_if_dock_free_bike_is_docked_and_available():
    dock, bike = Dock(), Bike("B1")
    dock.park(bike)
    assert dock.bike is bike
    assert bike.status is BikeStatus.AVAILABLE


def test_if_dock_occupied_raises_and_bike_stays_in_use():
    dock = Dock()
    dock.park(Bike("B1"))
    other = Bike("B2")
    with pytest.raises(DockOccupiedError):
        dock.park(other)
    assert other.status is BikeStatus.IN_USE
    assert dock.bike is not other


def test_if_outside_writes_dock_bike_it_fails():
    dock = Dock()
    with pytest.raises(AttributeError):
        dock.bike = Bike("B1")
    assert dock.bike is None


def test_if_outside_writes_bike_status_it_fails():
    bike = Bike("B1")
    with pytest.raises(AttributeError):
        bike.status = BikeStatus.AVAILABLE
    assert bike.status is BikeStatus.IN_USE


def test_if_outside_appends_to_docks_it_fails():
    station = Station("Chilonzor", 2)
    with pytest.raises(AttributeError):
        station.docks.append(Dock())
    assert len(station.docks) == 2


def test_if_two_stations_created_each_has_own_docks():
    a, b = Station("Chilonzor", 3), Station("Yunusobod", 5)
    assert len(a.docks) == 3 and len(b.docks) == 5
    assert not {id(d) for d in a.docks} & {id(d) for d in b.docks}
    a.park(Bike("B1"))
    assert len(a) == 1 and len(b) == 0


def test_if_bike_in_repair_it_stays_and_cannot_be_taken():
    station, bike = Station("Chilonzor", 2), Bike("B1")
    station.park(bike)
    bike.send_to_repair()
    with pytest.raises(NoBikeError):
        station.take_bike()
    with pytest.raises(BikeNotAvailableError):
        station.docks[0].release()
    assert station.docks[0].bike is bike
    assert bike.status is BikeStatus.REPAIR


def test_if_bike_not_docked_free_cannot_go_to_repair():
    bike = Bike("B1")  # not in any dock -> IN_USE
    with pytest.raises(BikeNotAvailableError):
        bike.send_to_repair()
    assert bike.status is BikeStatus.IN_USE


def test_if_repaired_bike_can_be_taken_again():
    station, bike = Station("Chilonzor", 1), Bike("B1")
    station.park(bike)
    bike.send_to_repair()
    bike.mark_repaired()
    assert station.take_bike() is bike


def test_if_print_station_shows_bikes_of_capacity(capsys):
    print(make_station("Chilonzor", 10, 4))
    assert capsys.readouterr().out == "Chilonzor: 4/10 bikes\n"


def test_if_len_station_is_docked_bikes():
    station = make_station("Chilonzor", 10, 4)
    station.docks[0].bike.send_to_repair()  # still docked -> still counted
    assert len(station) == 4


def test_if_repr_station_is_for_logs():
    station = make_station("Chilonzor", 10, 4)
    assert repr(station) == "Station(name='Chilonzor', capacity=10, bikes=4, free_docks=6)"


def test_if_capacity_below_one_raises_value_error():
    with pytest.raises(ValueError):
        Station("Empty", 0)


def test_if_sorted_stations_orders_by_free_docks():
    full = make_station("Sergeli", 3, 3)        # 0 free
    half = make_station("Chilonzor", 10, 4)     # 6 free
    empty = make_station("Yunusobod", 5, 0)     # 5 free
    assert [s.name for s in sorted([half, full, empty])] == ["Sergeli", "Yunusobod", "Chilonzor"]
