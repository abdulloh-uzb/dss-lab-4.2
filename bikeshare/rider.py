"""Rider (the app calls them users). Mostly data, so it is a dataclass."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from bikeshare.errors import NoActiveRideError, RideActiveError

if TYPE_CHECKING:
    from bikeshare.ride import Ride


@dataclass(eq=False)
class Rider:
    name: str
    _active_ride: Ride | None = field(default=None, init=False, repr=False)
    _total_charged: int = field(default=0, init=False)

    @property
    def active_ride(self) -> Ride | None:
        return self._active_ride

    @property
    def total_charged(self) -> int:
        return self._total_charged

    def ensure_no_active_ride(self) -> None:
        if self._active_ride is not None:
            raise RideActiveError(f"{self.name} already has an active ride")

    def start_ride(self, ride: Ride) -> None:
        self.ensure_no_active_ride()  # one rider -> at most one active ride
        self._active_ride = ride

    def end_ride(self) -> Ride:
        if self._active_ride is None:
            raise NoActiveRideError(f"{self.name} has no active ride")
        ride, self._active_ride = self._active_ride, None
        return ride

    def charge(self, amount: int) -> None:
        self._total_charged += amount
