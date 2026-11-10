"""Ride: an event with data. It owns the fee rule and its failed-return counter."""

from __future__ import annotations

import math
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bikeshare.bike import Bike
    from bikeshare.rider import Rider
    from bikeshare.station import Station


class Ride:
    FREE_MINUTES = 15
    BLOCK_MINUTES = 5
    BLOCK_PRICE = 500  # sum
    MAX_FEE = 20_000  # sum
    MAX_FAILED_RETURNS = 2  # n: after this many full-station returns -> redirect

    def __init__(self, rider: Rider, bike: Bike, start_station: Station, start_time: datetime) -> None:
        self._rider = rider
        self._bike = bike
        self._start_station = start_station
        self._start_time = start_time
        self._end_station: Station | None = None
        self._end_time: datetime | None = None
        self._failed_returns = 0

    @property
    def rider(self) -> Rider:
        return self._rider

    @property
    def bike(self) -> Bike:
        return self._bike

    @property
    def start_station(self) -> Station:
        return self._start_station

    @property
    def start_time(self) -> datetime:
        return self._start_time

    @property
    def end_station(self) -> Station | None:
        return self._end_station

    @property
    def end_time(self) -> datetime | None:
        return self._end_time

    @property
    def is_active(self) -> bool:
        return self._end_time is None  # clock keeps running until finish()

    # --- failed returns (Information Expert: "the same ride fails n times") ---

    @property
    def failed_returns(self) -> int:
        return self._failed_returns

    def register_failed_return(self) -> None:
        self._failed_returns += 1

    @property
    def needs_redirect(self) -> bool:
        return self._failed_returns >= self.MAX_FAILED_RETURNS

    # --- finishing and the money rule ---

    def check_end_time(self, end_time: datetime) -> None:
        if end_time < self._start_time:
            raise ValueError("end time is before start time")

    def finish(self, end_station: Station, end_time: datetime) -> None:
        if not self.is_active:
            raise ValueError("ride is already finished")
        self.check_end_time(end_time)
        self._end_station = end_station
        self._end_time = end_time

    @property
    def duration(self) -> timedelta:
        if self._end_time is None:
            raise ValueError("ride is not finished yet")
        return self._end_time - self._start_time

    @property
    def minutes(self) -> int:
        return int(self.duration.total_seconds() // 60)

    def fee(self) -> int:
        seconds = self.duration.total_seconds()
        free_seconds = self.FREE_MINUTES * 60
        if seconds <= free_seconds:
            return 0
        blocks = math.ceil((seconds - free_seconds) / (self.BLOCK_MINUTES * 60))
        return min(blocks * self.BLOCK_PRICE, self.MAX_FEE)

    def __repr__(self) -> str:
        return (
            f"Ride(rider={self._rider.name!r}, bike={self._bike.bike_id!r}, "
            f"start={self._start_station.name!r}, active={self.is_active}, "
            f"failed_returns={self._failed_returns})"
        )
