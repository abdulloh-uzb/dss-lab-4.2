"""Bike and its status. The status changes only through Bike's own methods."""

from enum import Enum

from bikeshare.errors import BikeNotAvailableError


class BikeStatus(Enum):
    AVAILABLE = "available"  # in a dock, can be taken
    IN_USE = "in use"        # not in any dock (with a rider, or brand new)
    REPAIR = "repair"        # in a dock, nobody can take it


class Bike:
    def __init__(self, bike_id: str) -> None:
        self._bike_id = bike_id
        self._status = BikeStatus.IN_USE  # a new bike is not in any dock yet

    @property
    def bike_id(self) -> str:
        return self._bike_id

    @property
    def status(self) -> BikeStatus:
        return self._status  # read-only: no setter, so bike.status = ... fails

    def check_in(self) -> None:
        """Called by Dock.park(): the bike goes into a dock."""
        if self._status is not BikeStatus.IN_USE:
            raise BikeNotAvailableError(f"bike {self._bike_id} is already in a dock")
        self._status = BikeStatus.AVAILABLE

    def check_out(self) -> None:
        """Called by Dock.release(): the bike leaves its dock."""
        if self._status is not BikeStatus.AVAILABLE:
            raise BikeNotAvailableError(
                f"bike {self._bike_id} is {self._status.value}, it cannot be taken"
            )
        self._status = BikeStatus.IN_USE

    def send_to_repair(self) -> None:
        """Only a docked free bike can go to repair. It stays in its dock."""
        if self._status is not BikeStatus.AVAILABLE:
            raise BikeNotAvailableError(
                f"bike {self._bike_id} is {self._status.value}, only a docked free bike can go to repair"
            )
        self._status = BikeStatus.REPAIR

    def mark_repaired(self) -> None:
        if self._status is not BikeStatus.REPAIR:
            raise BikeNotAvailableError(f"bike {self._bike_id} is not in repair")
        self._status = BikeStatus.AVAILABLE

    def __repr__(self) -> str:
        return f"Bike(bike_id={self._bike_id!r}, status={self._status.name})"
