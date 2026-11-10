"""ReceiptPrinter: turns a finished ride into one console line."""

from bikeshare.ride import Ride


class ReceiptPrinter:
    @staticmethod
    def format(ride: Ride) -> str:
        if ride.end_station is None:
            raise ValueError("ride is not finished yet")
        fee = f"{ride.fee():,}".replace(",", " ")
        return f"{ride.start_station.name} → {ride.end_station.name}, {ride.minutes} min, {fee} sum"

    @staticmethod
    def print(ride: Ride) -> str:
        line = ReceiptPrinter.format(ride)
        print(line)
        return line
