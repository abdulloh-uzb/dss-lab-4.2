"""Network: runs a ride (take bike / return bike) between its stations."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime

from bikeshare.errors import NoActiveRideError, StationFullError
from bikeshare.receipt import ReceiptPrinter
from bikeshare.ride import Ride
from bikeshare.rider import Rider
from bikeshare.station import Station


class Network:
    def __init__(self, stations: Iterable[Station], city: str = "Tashkent") -> None:
        self._city = city
        self._stations = tuple(stations)  # stations come from outside (aggregation)
        if not self._stations:
            raise ValueError("a network needs at least 1 station")
        self._rides: list[Ride] = []  # every ride is recorded here

    @property
    def city(self) -> str:
        return self._city

    @property
    def stations(self) -> tuple[Station, ...]:
        return self._stations

    @property
    def rides(self) -> tuple[Ride, ...]:
        return tuple(self._rides)

    def take(self, rider: Rider, station: Station, now: datetime) -> Ride:
        self._check_station(station)
        rider.ensure_no_active_ride()  # RideActiveError before any bike moves
        bike = station.take_bike()  # NoBikeError; dock -> bike IN_USE
        ride = Ride(rider, bike, station, now)
        rider.start_ride(ride)
        self._rides.append(ride)
        return ride

    def return_bike(self, rider: Rider, station: Station, now: datetime) -> Ride:
        self._check_station(station)
        ride = rider.active_ride
        if ride is None:
            raise NoActiveRideError(f"{rider.name} has no active ride")
        ride.check_end_time(now)  # validate before the bike moves
        try:
            station.park(ride.bike)  # bike -> AVAILABLE in a free dock
        except StationFullError:
            ride.register_failed_return()  # clock keeps running
            if ride.needs_redirect:
                raise StationFullError(station, redirect=self.redirect_for(station)) from None
            raise
        ride.finish(station, now)
        rider.end_ride()
        rider.charge(ride.fee())
        ReceiptPrinter.print(ride)
        return ride

    def redirect_for(self, full_station: Station) -> Station | None:
        """Station with most free docks, tie -> name A-Z. None if all are full."""
        candidates = [s for s in self._stations if s is not full_station and s.free_docks > 0]
        if not candidates:
            return None
        return min(candidates, key=lambda s: (-s.free_docks, s.name))

    def report(self) -> str:
        """Manager view: stations by free docks, biggest first."""
        ordered = sorted(self._stations, key=lambda s: (-s.free_docks, s.name))
        text = "\n".join(f"{s.name}: {s.free_docks} free docks" for s in ordered)
        print(text)
        return text

    def _check_station(self, station: Station) -> None:
        if station not in self._stations:
            raise ValueError(f"{station.name} is not in the {self._city} network")
