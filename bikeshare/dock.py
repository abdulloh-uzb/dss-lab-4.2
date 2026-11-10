"""Dock: holds at most one bike."""

from __future__ import annotations

from bikeshare.bike import Bike, BikeStatus
from bikeshare.errors import DockOccupiedError, NoBikeError


class Dock:
    def __init__(self) -> None:
        self._bike: Bike | None = None

    @property
    def bike(self) -> Bike | None:
        return self._bike  # read-only: no setter, so dock.bike = x fails

    @property
    def is_free(self) -> bool:
        return self._bike is None

    @property
    def has_available_bike(self) -> bool:
        return self._bike is not None and self._bike.status is BikeStatus.AVAILABLE

    def park(self, bike: Bike) -> None:
        if self._bike is not None:
            raise DockOccupiedError("dock already holds a bike")  # bike stays IN_USE
        bike.check_in()  # raises if the bike is already in another dock
        self._bike = bike

    def release(self) -> Bike:
        if self._bike is None:
            raise NoBikeError("dock is empty")
        self._bike.check_out()  # raises if the bike is in REPAIR -> it stays here
        bike, self._bike = self._bike, None
        return bike

    def __repr__(self) -> str:
        return f"Dock(bike={self._bike!r})"
