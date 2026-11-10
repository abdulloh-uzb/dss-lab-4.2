from datetime import datetime

from bikeshare import Bike, Station

T0 = datetime(2026, 11, 10, 10, 0, 0)


def make_station(name: str = "Chilonzor", capacity: int = 10, bikes: int = 4) -> Station:
    station = Station(name, capacity)
    for i in range(bikes):
        station.park(Bike(f"{name[:3].upper()}-{i + 1}"))
    return station
