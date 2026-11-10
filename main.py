"""Console demo of the Tashkent bike sharing network.

Usage:  python main.py [happy | failure | recovery | optional | rules | fee | errors | all]
Times are fixed parameters (never datetime.now() inside a class).
"""

import sys
from datetime import datetime, timedelta

from bikeshare import (
    Bike,
    BikeShareError,
    Dock,
    Network,
    ReceiptPrinter,
    Ride,
    Rider,
    Station,
)

T0 = datetime(2026, 11, 10, 10, 0)


def at(minutes: int, seconds: int = 0) -> datetime:
    return T0 + timedelta(minutes=minutes, seconds=seconds)


def build_city() -> tuple[Network, dict[str, Station]]:
    stations = {}
    for name, capacity, bikes in [("Chilonzor", 10, 4), ("Yunusobod", 10, 2), ("Sergeli", 3, 3)]:
        station = Station(name, capacity)
        for i in range(bikes):
            station.park(Bike(f"{name[:3].upper()}-{i + 1}"))
        stations[name] = station
    return Network(stations.values()), stations


def show(stations: dict[str, Station]) -> None:
    for station in stations.values():
        print(f"   {station}  ({station.free_docks} free docks)")


def step(text: str) -> None:
    print(f"\n>> {text}")


def try_(action) -> BikeShareError | None:
    try:
        action()
    except (BikeShareError, ValueError, AttributeError) as error:
        print(f"   {type(error).__name__}: {error}")
        return error
    return None


def happy() -> None:
    print("=== HAPPY PATH ===")
    network, s = build_city()
    ali = Rider("Ali")
    show(s)
    step("10:00 Ali taps Take at Chilonzor")
    ride = network.take(ali, s["Chilonzor"], at(0))
    print(f"   {ride.bike}, Ali's active ride: {ali.active_ride}")
    step("10:23 Ali taps Return at Yunusobod (free dock)")
    network.return_bike(ali, s["Yunusobod"], at(23))
    print(f"   Ali charged: {ali.total_charged} sum, active ride: {ali.active_ride}")
    show(s)


def failure(network=None, s=None, ali=None):
    print("=== FAILURE PATH ===")
    if network is None:
        network, s = build_city()
        ali = Rider("Ali")
    show(s)
    step("10:00 Ali taps Take at Chilonzor")
    network.take(ali, s["Chilonzor"], at(0))
    step("10:20 Ali taps Return at Sergeli (full) -> failure 1")
    try_(lambda: network.return_bike(ali, s["Sergeli"], at(20)))
    print(f"   ride still active: {ali.active_ride.is_active}, bike: {ali.active_ride.bike}")
    step("10:22 Ali taps Return at Sergeli again -> failure 2 (n = 2 exhausted)")
    error = try_(lambda: network.return_bike(ali, s["Sergeli"], at(22)))
    print(f"   redirect: {error.redirect.name}")
    return network, s, ali, error


def recovery() -> None:
    network, s, ali, error = failure()
    print("\n=== RECOVERY PATH ===")
    step(f"10:31 Ali taps Return at the redirected station {error.redirect.name}")
    network.return_bike(ali, error.redirect, at(31))
    print(f"   Ali charged: {ali.total_charged} sum, active ride: {ali.active_ride}")
    show(s)


def optional() -> None:
    print("=== OPTIONAL: sorted(stations) and manager report ===")
    network, s = build_city()
    step("sorted(stations) -> by free docks (__lt__)")
    for station in sorted(network.stations):
        print(f"   {station.name}: {station.free_docks} free docks")
    step("network.report() -> manager view, biggest first")
    network.report()


def rules() -> None:
    print("=== BIKE, DOCK, STATION PROTECT THEIR RULES ===")
    dock, b1, b2 = Dock(), Bike("B1"), Bike("B2")
    step("park B1 into a free dock")
    dock.park(b1)
    print(f"   {dock}")
    step("park B2 into the occupied dock")
    try_(lambda: dock.park(b2))
    print(f"   {b2}")
    step("outside code: dock.bike = x / bike.status = ... / station.docks.append(...)")
    station = Station("Chilonzor", 10)
    try_(lambda: setattr(dock, "bike", b2))
    try_(lambda: setattr(b1, "status", None))
    try_(lambda: station.docks.append(Dock()))
    step("two stations -> each has its own docks")
    other = Station("Yunusobod", 5)
    print(f"   share a dock? {bool(set(station.docks) & set(other.docks))}")
    step("bike in REPAIR stays in its dock, cannot be taken")
    for i in range(4):
        station.park(Bike(f"CHI-{i + 1}"))
    for d in station.docks[:4]:
        d.bike.send_to_repair()
    try_(station.take_bike)
    print(f"   {station.docks[0]}")
    step("only a docked free bike can go to repair")
    try_(Bike("NEW").send_to_repair)
    step("print / len / repr")
    print(f"   print: {station}")
    print(f"   len:   {len(station)}")
    print(f"   repr:  {station!r}")


def fee() -> None:
    print("=== RIDE OWNS THE FEE RULE ===")
    start, end = Station("Chilonzor", 10), Station("Yunusobod", 10)
    for label, minutes, seconds in [("15:00", 15, 0), ("15:01", 15, 1), ("20:00", 20, 0),
                                    ("20:01", 20, 1), ("10 h", 600, 0)]:
        ride = Ride(Rider("Ali"), Bike("B1"), start, T0)
        ride.finish(end, at(minutes, seconds))
        print(f"   {label:>6} -> {ride.fee()} sum")
    step("end time before start time")
    ride = Ride(Rider("Ali"), Bike("B1"), start, T0)
    try_(lambda: ride.finish(end, at(-1)))
    step("ReceiptPrinter.print(ride)")
    ride.finish(end, at(23))
    ReceiptPrinter.print(ride)


def errors() -> None:
    print("=== NETWORK ERRORS ===")
    network, s = build_city()
    ali = Rider("Ali")
    step("Ali takes a bike, then taps Take again")
    network.take(ali, s["Chilonzor"], at(0))
    try_(lambda: network.take(ali, s["Chilonzor"], at(1)))
    step("Bobur taps Take at a station without a free bike")
    for dock in s["Sergeli"].docks:
        dock.bike.send_to_repair()
    try_(lambda: network.take(Rider("Bobur"), s["Sergeli"], at(2)))
    step("Bobur taps Return without a ride")
    try_(lambda: network.return_bike(Rider("Bobur"), s["Yunusobod"], at(3)))


SCENARIOS = {"happy": happy, "failure": failure, "recovery": recovery, "optional": optional,
             "rules": rules, "fee": fee, "errors": errors}


def main() -> None:
    choice = sys.argv[1] if len(sys.argv) > 1 else "all"
    if choice == "all":
        for scenario in SCENARIOS.values():
            scenario()
            print()
    elif choice in SCENARIOS:
        SCENARIOS[choice]()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
