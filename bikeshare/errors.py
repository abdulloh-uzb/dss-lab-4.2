"""All errors of the bike sharing app."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bikeshare.station import Station


class BikeShareError(Exception):
    """Base class for every broken rule in the app."""


class DockOccupiedError(BikeShareError):
    """The dock already holds a bike."""


class BikeNotAvailableError(BikeShareError):
    """The bike is in the wrong status for this action (e.g. it is in REPAIR)."""


class NoBikeError(BikeShareError):
    """The station has no bike that can be taken."""


class RideActiveError(BikeShareError):
    """The rider already has an active ride."""


class NoActiveRideError(BikeShareError):
    """The rider tries to return a bike without an active ride."""


class StationFullError(BikeShareError):
    """No free dock at the station. After n failed returns it carries a redirect."""

    def __init__(self, station: Station, redirect: Station | None = None) -> None:
        self.station = station
        self.redirect = redirect
        message = f"{station.name} is full"
        if redirect is not None:
            message += f", go to {redirect.name} ({redirect.free_docks} free docks)"
        super().__init__(message)
