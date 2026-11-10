"""Station: creates and owns its docks (composition)."""

from __future__ import annotations

from bikeshare.bike import Bike
from bikeshare.dock import Dock
from bikeshare.errors import NoBikeError, StationFullError


class Station:
    def __init__(self, name: str, capacity: int) -> None:
        if capacity < 1:
            raise ValueError("a station needs at least 1 dock")
        self._name = name
        self._docks = tuple(Dock() for _ in range(capacity))  # own docks per object

    @property
    def name(self) -> str:
        return self._name

    @property
    def capacity(self) -> int:
        return len(self._docks)

    @property
    def docks(self) -> tuple[Dock, ...]:
        return self._docks  # tuple: no append, no remove

    @property
    def free_docks(self) -> int:
        return sum(1 for dock in self._docks if dock.is_free)

    @property
    def available_bikes(self) -> int:
        return sum(1 for dock in self._docks if dock.has_available_bike)

    def take_bike(self) -> Bike:
        for dock in self._docks:
            if dock.has_available_bike:
                return dock.release()
        raise NoBikeError(f"{self._name} has no free bike")

    def park(self, bike: Bike) -> Dock:
        for dock in self._docks:
            if dock.is_free:
                dock.park(bike)
                return dock
        raise StationFullError(self)

    def __len__(self) -> int:
        return self.capacity - self.free_docks  # docked bikes (REPAIR ones too)

    def __str__(self) -> str:
        return f"{self._name}: {len(self)}/{self.capacity} bikes"

    def __repr__(self) -> str:
        return (
            f"Station(name={self._name!r}, capacity={self.capacity}, "
            f"bikes={len(self)}, free_docks={self.free_docks})"
        )

    def __lt__(self, other: Station) -> bool:
        return self.free_docks < other.free_docks
