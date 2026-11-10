# Tashkent Bike Sharing (Lab 4-2)

A console bike-sharing app in Python 3.10+. It shows classes, relationships and encapsulation.
The design (nouns + CRC cards) is in [docs/design.md](docs/design.md).

```bash
python3 -m venv .venv && .venv/bin/pip install pytest
.venv/bin/python main.py happy      # or: failure | recovery | optional | rules | fee | errors | all
.venv/bin/pytest -v                 # 34 tests, test name = the "If" line it proves
```

```
bikeshare/
├── bike.py       Bike + BikeStatus (AVAILABLE, IN_USE, REPAIR)
├── dock.py       Dock: holds at most one bike
├── station.py    Station: creates its own docks
├── ride.py       Ride: event with data, owns the fee rule + failed-return counter
├── rider.py      Rider (@dataclass): one active ride only
├── network.py    Network: take / return / redirect / report
├── receipt.py    ReceiptPrinter
└── errors.py     DockOccupiedError, NoBikeError, RideActiveError, NoActiveRideError, StationFullError, ...
```

---

## Demo videos

> Each video is 40 seconds or less, follows the exact scenario below, and ends with `pytest -v`.
> Demo setup: **Chilonzor** 4/10 bikes · **Yunusobod** 2/10 bikes · **Sergeli** 3/3 bikes (full).

<details>
<summary><b>1. Happy path</b>: take a bike, return it to a free dock, receipt shows the fee</summary>

Command: `python main.py happy`

1. 10:00: Ali taps **Take** at Chilonzor, so the bike becomes `IN_USE` and Ali knows the active ride.
2. 10:23: Ali taps **Return** at Yunusobod (free dock), so the bike becomes `AVAILABLE`.
3. Receipt: `Chilonzor → Yunusobod, 23 min, 1 000 sum`, and Ali is charged 1 000 sum.
4. `pytest -v`

https://github.com/user-attachments/assets/REPLACE-WITH-VIDEO-1

</details>

<details>
<summary><b>2. Failure path</b>: return to a full station, repeated until n = 2 is exhausted</summary>

Command: `python main.py failure`

1. 10:00: Ali takes a bike at Chilonzor.
2. 10:20: Return at Sergeli (full) gives `StationFullError: Sergeli is full` (failure 1). The ride clock keeps running and the bike stays `IN_USE`.
3. 10:22: Return at Sergeli again gives `StationFullError: Sergeli is full, go to Yunusobod (8 free docks)` (failure 2, n = 2 exhausted, so a redirect).
4. `pytest -v`

https://github.com/user-attachments/assets/REPLACE-WITH-VIDEO-2

</details>

<details>
<summary><b>3. Recovery path</b>: return to the redirected station</summary>

Command: `python main.py recovery` (runs the failure path first)

1. 10:31: Ali taps **Return** at the redirected station Yunusobod.
2. The ride is closed, the fee is charged and the receipt is printed: `Chilonzor → Yunusobod, 31 min, 2 000 sum`.
3. Ali has no active ride, and the bike is `AVAILABLE` in a Yunusobod dock.
4. `pytest -v`

https://github.com/user-attachments/assets/REPLACE-WITH-VIDEO-3

</details>

<details>
<summary><b>4. Optional parts</b>: <code>sorted(stations)</code> and <code>network.report()</code></summary>

Command: `python main.py optional`

1. `sorted(stations)` gives Sergeli 0, Chilonzor 6, Yunusobod 8 free docks (uses `__lt__`).
2. `network.report()` is the manager view, biggest first: Yunusobod 8, Chilonzor 6, Sergeli 0.
3. `pytest -v`

https://github.com/user-attachments/assets/REPLACE-WITH-VIDEO-4

</details>

<details>
<summary><b>5. Bike, Dock, Station protect their own rules</b></summary>

Command: `python main.py rules`

1. Park B1 into a free dock, so it becomes `AVAILABLE`.
2. Park B2 into the occupied dock: `DockOccupiedError`, and B2 stays `IN_USE`.
3. `dock.bike = x`, `bike.status = ...` and `station.docks.append(...)` all give `AttributeError`.
4. Two stations do not share docks.
5. A bike in `REPAIR` stays in its dock, and `take` gives `NoBikeError`. A bike that is not docked cannot go to repair.
6. `print(station)` gives `Chilonzor: 4/10 bikes`. `len(station)` gives `4`. `repr(station)` gives `Station(name='Chilonzor', capacity=10, bikes=4, free_docks=6)`.
7. `pytest -v`

https://github.com/user-attachments/assets/REPLACE-WITH-VIDEO-5

</details>

<details>
<summary><b>6. Ride owns the fee rule</b></summary>

Command: `python main.py fee`

1. 15:00 → 0 · 15:01 → 500 · 20:00 → 500 · 20:01 → 1 000 · 10 h → 20 000 (cap).
2. End time before start time gives `ValueError`.
3. `ReceiptPrinter.print(ride)` gives `Chilonzor → Yunusobod, 23 min, 1 000 sum`.
4. `pytest -v`

https://github.com/user-attachments/assets/REPLACE-WITH-VIDEO-6

</details>

<details>
<summary><b>7. Network errors</b></summary>

Command: `python main.py errors`

1. Take while a ride is active gives `RideActiveError`.
2. Take at a station without a free bike gives `NoBikeError`.
3. Return without a ride gives `NoActiveRideError`.
4. `pytest -v`

https://github.com/user-attachments/assets/REPLACE-WITH-VIDEO-7

</details>

### Tests ↔ "If" lines

| "If" line from the task | Test |
|---|---|
| dock is free → bike docked, AVAILABLE | `test_if_dock_free_bike_is_docked_and_available` |
| dock is occupied → DockOccupiedError, bike stays IN_USE | `test_if_dock_occupied_raises_and_bike_stays_in_use` |
| outside code writes dock.bike / bike.status / docks.append → fails | `test_if_outside_writes_dock_bike_it_fails`, `test_if_outside_writes_bike_status_it_fails`, `test_if_outside_appends_to_docks_it_fails` |
| two Station objects → each has its own docks | `test_if_two_stations_created_each_has_own_docks` |
| bike in REPAIR → stays in dock, cannot be taken; only docked free bike to repair | `test_if_bike_in_repair_it_stays_and_cannot_be_taken`, `test_if_bike_not_docked_free_cannot_go_to_repair`, `test_if_repaired_bike_can_be_taken_again` |
| print(station) / len / repr | `test_if_print_station_shows_bikes_of_capacity`, `test_if_len_station_is_docked_bikes`, `test_if_repr_station_is_for_logs` |
| sorted(stations) by free docks (optional) | `test_if_sorted_stations_orders_by_free_docks` |
| ride 15:00 / 15:01 / 20:00 / 20:01 / very long | `test_if_ride_lasted_duration_fee_is[...]` (5 cases) |
| end time before start → ValueError | `test_if_end_before_start_raises_value_error`, `test_if_return_time_before_start_bike_stays_with_rider` |
| ReceiptPrinter.print(ride) | `test_if_receipt_printed_shows_route_minutes_fee` |
| no active ride + free bike → new ride | `test_if_no_active_ride_and_free_bike_new_ride_starts` |
| already active ride → RideActiveError | `test_if_rider_has_active_ride_raises_ride_active_error` |
| station without free bike → NoBikeError | `test_if_station_without_free_bike_raises_no_bike_error` |
| return without ride → NoActiveRideError | `test_if_return_without_ride_raises_no_active_ride_error` |
| happy path: return to a free dock, receipt shows fee | `test_if_return_to_free_dock_receipt_shows_fee` |
| station full → StationFullError, clock keeps running | `test_if_station_full_raises_and_ride_keeps_running` |
| same ride fails n = 2 times → redirect (tie → A–Z), counter lives in Ride | `test_if_same_ride_fails_twice_error_carries_redirect`, `test_if_redirect_tie_picks_name_a_to_z`, `test_if_new_ride_starts_with_zero_failures` |
| return to redirected station → closed, fee, receipt | `test_if_return_to_redirected_station_ride_closed_and_charged` |
| network.report() (optional) | `test_if_report_prints_stations_biggest_free_first` |

---

## Relationships table

Legend:
- **dependency** ⇢: only gets the other as a parameter.
- **association** —: keeps a link to an independent object.
- **aggregation** ◇: gets parts from outside, and the parts live on after the whole is gone.
- **composition** ◆: creates its parts inside, and they die with it.

| Pair | Relationship | Multiplicity (A — B) | file:line that proves it |
|---|---|---|---|
| Station ◆ Dock | composition | 1 — 1..* | [bikeshare/station.py:15](bikeshare/station.py#L15) `self._docks = tuple(Dock() for _ in range(capacity))` |
| Network ◇ Station | aggregation | 1 — 1..* | [bikeshare/network.py:18](bikeshare/network.py#L18) `self._stations = tuple(stations)` |
| Network ◆ Ride | composition | 1 — 0..* | [bikeshare/network.py:39](bikeshare/network.py#L39) `ride = Ride(rider, bike, station, now)` (stored at line 41) |
| Dock — Bike | association | 0..1 — 0..1 | [bikeshare/dock.py:29](bikeshare/dock.py#L29) `self._bike = bike` |
| Rider — Ride (active) | association | 1 — 0..1 | [bikeshare/rider.py:34](bikeshare/rider.py#L34) `self._active_ride = ride` |
| Ride — Rider | association | 0..* — 1 | [bikeshare/ride.py:23](bikeshare/ride.py#L23) `self._rider = rider` |
| Ride — Bike | association | 0..* — 1 | [bikeshare/ride.py:24](bikeshare/ride.py#L24) `self._bike = bike` |
| Ride — Station (start) | association | 0..* — 1 | [bikeshare/ride.py:25](bikeshare/ride.py#L25) `self._start_station = start_station` |
| Ride — Station (end) | association | 0..* — 0..1 | [bikeshare/ride.py:82](bikeshare/ride.py#L82) `self._end_station = end_station` |
| Network ⇢ Rider | dependency | — | [bikeshare/network.py:35](bikeshare/network.py#L35) `def take(self, rider: Rider, station: Station, now: datetime)` |
| Network ⇢ ReceiptPrinter | dependency | — | [bikeshare/network.py:60](bikeshare/network.py#L60) `ReceiptPrinter.print(ride)` |
| ReceiptPrinter ⇢ Ride | dependency | — | [bikeshare/receipt.py:15](bikeshare/receipt.py#L15) `def print(ride: Ride) -> str:` |
| Station ⇢ Bike | dependency | — | [bikeshare/station.py:43](bikeshare/station.py#L43) `def park(self, bike: Bike) -> Dock:` (passes it to a Dock, keeps no link) |

### Lifetime tests (aggregation and composition)

| Pair | "If I delete X, do Y disappear?" | Answer |
|---|---|---|
| Station ◆ Dock | If I delete a **Station**, do its **Docks** disappear? | **Yes.** The docks are created inside `Station.__init__` (station.py:15). Nobody else creates them or keeps them, so a dock without its station means nothing → composition. |
| Network ◆ Ride | If I delete the **Network**, do its **Rides** disappear? | **Yes.** Rides are created inside `Network.take()` (network.py:39) and the record list lives only in Network (network.py:21). The ride history goes with it. (Python keeps an object alive while something points to it. A rider still on a ride points to it, but that ride can never be finished without the network.) |
| Network ◇ Station | If I delete the **Network**, do the **Stations** disappear? | **No.** Stations are built outside (`main.py`, `build_city()`) and passed in (network.py:18). They live on and can be given to a new Network → aggregation. |

### Multiplicities: enforced or not

| Multiplicity | Enforced? | Where / why |
|---|---|---|
| Dock — Bike **0..1** (a dock holds at most one bike) | ✅ | [dock.py:27](bikeshare/dock.py#L27) raises `DockOccupiedError` |
| Bike — Dock **0..1** (a bike is in at most one dock) | ✅ | [dock.py:28](bikeshare/dock.py#L28) `bike.check_in()` refuses a bike that is not `IN_USE` ([bike.py:29](bikeshare/bike.py#L29)), so an already-docked bike cannot be parked twice |
| Rider — active Ride **0..1** | ✅ | [rider.py:30](bikeshare/rider.py#L30) raises `RideActiveError`, checked before any bike moves ([network.py:37](bikeshare/network.py#L37)) |
| Station — Dock **1..\*** | ✅ | [station.py:13](bikeshare/station.py#L13) `ValueError` if capacity < 1. The tuple keeps the number fixed. |
| Network — Station **1..\*** | ✅ | [network.py:20](bikeshare/network.py#L20) `ValueError` if no stations |
| **Station — Network 1** (a station belongs to exactly one network) | ❌ **not enforced** | You *could* pass the same `Station` object into two `Network`s. **Why it is fine:** the app builds exactly one Network for Tashkent and has no files or database, so a second network never appears. Enforcing it would need a back-link `station.network`, which adds two-way coupling for a case that cannot happen. |

---

## Rule: "a bike is in exactly one place"

```text
A bike has exactly two possible places:
  (a) inside ONE dock         -> status AVAILABLE or REPAIR, dock._bike is this bike
  (b) inside ONE active ride  -> status IN_USE, ride._bike is this bike, no dock holds it
  (a brand new Bike starts IN_USE = "not in a dock" until it is parked for the first time)

1. Nobody outside can put a bike somewhere by hand:
   - dock.bike and bike.status are read-only @property, no setter   (dock.py:15, bike.py:25)
   - station.docks is a tuple -> no .append(), no new docks          (station.py:27)

2. The bike changes place ONLY inside Network, one method each way:
   - take():        dock.release() empties the dock and bike -> IN_USE, then
                    a new Ride gets the bike.             dock -> ride  (network.py:38-39)
   - return_bike(): station.park(bike) puts it in a free dock, bike -> AVAILABLE,
                    then ride.finish() closes the ride.   ride -> dock  (network.py:51-57)

3. Every check runs BEFORE the bike moves, so a failure keeps the old place:
   - second ride      -> RideActiveError before take_bike()       (network.py:37)
   - end < start      -> ValueError before park()                 (network.py:49)
   - station full     -> StationFullError, bike stays IN_USE in the ride (station.py:48)
   - dock occupied    -> DockOccupiedError, bike stays IN_USE     (dock.py:27)
   - bike in REPAIR   -> check_out() refuses, bike stays in its dock (dock.py:34)

4. Dock.park() calls bike.check_in(), which only accepts an IN_USE bike, so a bike that
   is already docked can never be parked into a second dock    (dock.py:28, bike.py:29)

=> At every moment the bike is in one dock OR one ride, never both and never neither.
```
# dss-lab-4.2
