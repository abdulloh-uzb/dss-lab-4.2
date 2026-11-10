# Design: Tashkent Bike Sharing

> Class discovery (Lecture 4). This document contains no code, only nouns, decisions and CRC cards.

## 1. Requirement text

> Tashkent **bike network** has **stations**. Every **station** has a fixed **number of docks** and a **dock** holds at most one **bike**. A **rider** (the **app** calls them **users**) takes a **bike** from any **station** and returns it to any free **dock** of any **station**. Every **ride** is recorded with **start station**, **end station** and **times**. First **15 minutes** are free, after that the rider pays **500 sum** for every started **5 minutes**, but not more than **20 000 sum** per **ride**. One **rider** can have one **active ride** only. A **bike** sent to **repair** stays in its **dock** and nobody can take it. The **manager** sees how many **free docks** each **station** has.

## 2. Noun sorting

Rules:
- data + behaviour → **class**
- only a value → **attribute**
- outside the program → **actor**
- two names for one thing → **merge**
- vague word → **question for the customer**

| # | Noun | Data? | Behaviour? | Decision | Becomes |
|---|------|-------|------------|----------|---------|
| 1 | bike network | list of stations, ride history | take bike, return bike, redirect, report | **class** | `Network` |
| 2 | Tashkent | a name | none | attribute | `Network.city` |
| 3 | station | name, docks | count bikes / free docks, give a bike, park a bike | **class** | `Station` |
| 4 | number of docks | an int | none | attribute | `Station(capacity=…)` |
| 5 | dock | the bike in it (0..1) | park, release, say if free | **class** | `Dock` |
| 6 | bike | id, status | change status by its own rules | **class** | `Bike` |
| 7 | rider | name, active ride | start / end ride, refuse a second ride | **class** | `Rider` |
| 8 | users | same thing as rider | | **merge** into rider | `Rider` |
| 9 | app | it *is* the program | | not a class (system boundary) | `main.py` console |
| 10 | ride | rider, bike, stations, times, failed returns | finish, compute fee | **class (event)** | `Ride` |
| 11 | start station / end station | a reference | none | attribute | `Ride.start_station`, `Ride.end_station` |
| 12 | times | datetimes | none | attribute | `Ride.start_time`, `Ride.end_time` |
| 13 | 15 minutes, 5 minutes | numbers | none | attribute (constant) | `Ride.FREE_MINUTES`, `Ride.BLOCK_MINUTES` |
| 14 | 500 sum, 20 000 sum | numbers | none | attribute (constant) | `Ride.BLOCK_PRICE`, `Ride.MAX_FEE` |
| 15 | sum | currency | none | attribute type | `int` (money is int sum) |
| 16 | fee / pays | a computed value | none | attribute (derived) | `Ride.fee()` |
| 17 | active ride | a reference | none | attribute | `Rider.active_ride` |
| 18 | repair | a state | none | attribute value | `BikeStatus.REPAIR` |
| 19 | manager | a person outside the program | | **actor** | uses `Network.report()` |
| 20 | free docks | a computed count | none | attribute (derived) | `Station.free_docks` |
| 21 | receipt (from lab text, not requirement text) | none of its own | formats a ride | helper class | `ReceiptPrinter` |

**Result: 6 domain classes:** `Network`, `Station`, `Dock`, `Bike`, `Rider`, `Ride`. There is also one helper class (`ReceiptPrinter`) and one enum (`BikeStatus`: `AVAILABLE`, `IN_USE`, `REPAIR`).

### The event class: `Ride`
"Ride" is a noun you cannot touch. It is an **event**, but it has data: rider, bike, start/end station, start/end time and the number of failed returns. So it is a class.
**The money rule is owned by `Ride.fee()`**. All four numbers (15, 5, 500, 20 000) are written once, as class constants of `Ride`.

Fee rule (written once inside `Ride.fee()`):
```
minutes  = duration in seconds / 60
if minutes <= FREE_MINUTES:           fee = 0
else: blocks = ceil((minutes - FREE_MINUTES) / BLOCK_MINUTES)
      fee    = min(blocks * BLOCK_PRICE, MAX_FEE)
```
Check: 15:00 → 0 · 15:01 → 1 block → 500 · 20:00 → 1 block → 500 · 20:01 → 2 blocks → 1 000 · 10 h → 20 000 (cap).

### Questions for the customer (vague words)
1. **"every started 5 minutes"**: are the blocks counted from minute 15 or from minute 0? *(Assumed: from minute 15, so 15:01 → 500.)*
2. **"takes a bike"**: does the rider choose a specific bike, or does the station give any available one? *(Assumed: the station gives the first available bike.)*
3. **"sent to repair"**: who sends a bike to repair (manager, technician, rider)? How does a bike come back from repair? *(Assumed: a staff action `bike.send_to_repair()` / `bike.mark_repaired()`.)*
4. **"fixed number of docks"**: can a station ever be extended? *(Assumed: no. The capacity is set once in the constructor.)*
5. **"pays"**: how is the money taken (card, balance)? *(Assumed: out of scope. We only compute and print the fee.)*
6. **"times"**: only start and end, or also pauses? *(Assumed: start and end only.)*
7. **"returns it to any free dock of any station"**: may the rider return to the same station where the ride started? *(Assumed: yes.)*
8. **"recorded"**: where, and for how long? *(Assumed: in memory in `Network`, since the lab says no files and no database.)*

## 3. CRC cards

### First draft: too big, so we split it
The first draft put everything into `Network`:

| Class | Responsibilities | Collaborators |
|-------|------------------|---------------|
| Network (draft) | 1. keep stations · 2. take bike · 3. return bike · 4. compute fee · 5. count failed returns · 6. print receipt · 7. manager report | Station, Rider, Bike |

7 responsibilities is more than 4, so we **split** it:
- *compute fee* moves to **Ride**, because Ride has the start and end times (Information Expert).
- *count failed returns* moves to **Ride**, because the counter belongs to "the same ride" (see scenario below).
- *print receipt* moves to **ReceiptPrinter**, because formatting output is not network logic.

### Final cards (each has 4 or fewer responsibilities)

| Class | Responsibilities | Collaborators |
|-------|------------------|---------------|
| **Bike** | 1. know its id and status (read-only) · 2. become `IN_USE` when taken · 3. become `AVAILABLE` when docked · 4. go to `REPAIR` (only from `AVAILABLE`) and come back | Dock |
| **Dock** | 1. know its bike (at most one) · 2. park a bike, or raise `DockOccupiedError` · 3. release its bike only if it is `AVAILABLE` (not `REPAIR`) · 4. say if it is free | Bike |
| **Station** | 1. know its name and create its own docks · 2. count docked bikes (`len`) and free docks · 3. give out an available bike, or raise `NoBikeError` · 4. park a returned bike in a free dock, or raise `StationFullError` | Dock, Bike |
| **Ride** | 1. know rider, bike, start station and start time · 2. finish: set end station and end time, raise `ValueError` if end < start · 3. compute its fee (**owns the money rule**) · 4. count its failed returns and say when a redirect is needed (n = 2) | Station, Bike, Rider |
| **Rider** | 1. know name and active ride · 2. start a ride, or raise `RideActiveError` · 3. end the active ride, or raise `NoActiveRideError` · 4. keep the total money charged | Ride |
| **Network** | 1. keep its stations and the record of all rides · 2. run *take*: station → bike → new Ride → rider · 3. run *return*: park → finish ride → print receipt, or on full station count the failure and attach a redirect · 4. find the redirect station (most free docks, tie → name A–Z) and the manager report | Station, Rider, Ride, ReceiptPrinter |
| **ReceiptPrinter** | 1. turn a finished ride into one line: `Chilonzor → Yunusobod, 23 min, 1 000 sum` | Ride |

## 4. Scenario walk-through: "rider returns bike to a full station"

Read aloud. Every step must name a card.

| # | Step | Owner (card) |
|---|------|--------------|
| 1 | Rider taps **Return** at station *Chilonzor* | actor (rider) → **Network**.return_bike(rider, station, now) |
| 2 | Find the rider's ride; if none → `NoActiveRideError` | **Rider** (knows active ride) |
| 3 | Try to put the bike into a free dock of Chilonzor | **Station** asks each **Dock** if it is free |
| 4 | No free dock → `StationFullError` | **Station** |
| 5 | Remember that this ride failed once more | **?** see the rounds below |
| 6 | Ride clock keeps running (no end time is set) | **Ride** (end_time stays `None`) |
| 7 | Bike stays `IN_USE`, still with the rider | **Bike** (status not changed because park failed) |
| 8 | If failures reached n = 2 → choose the station with the most free docks (tie → name A–Z) | **Network** (the only card that knows *all* stations) |
| 9 | Raise the error with the redirect station inside it | **Network** raises `StationFullError(station, redirect=…)` |
| 10 | Rider goes to *Yunusobod* and taps **Return** again | **Network**.return_bike |
| 11 | Free dock found, bike parked, bike becomes `AVAILABLE` | **Station** → **Dock** → **Bike** |
| 12 | Ride is closed: end station and end time are set | **Ride**.finish |
| 13 | Fee is computed | **Ride**.fee |
| 14 | Rider no longer has an active ride | **Rider**.end_ride |
| 15 | Receipt is printed | **ReceiptPrinter**.print(ride) |

### Step 5 had no owner
- **Round 1:** No card has "count failed returns". Try **Station**? No. The counter is about *one ride*, but a station is used by many rides, and the two failures may even happen at different stations.
- **Round 2:** Try **Network**? Network would need a dict `{ride: count}`, which keeps data about a ride outside the ride. Try **Rider**? It would have to reset the counter on every new ride, which is easy to forget.
- **Still no good owner after n = 2 rounds**, so we apply **Information Expert**: give it to the class that has the data. The requirement says *"if the **same ride** fails n = 2 times"*, so the counter is a fact about the ride. **`Ride`** gets `failed_returns` and `register_failed_return()`. When the ride ends, the counter goes with it, and a new ride starts again at 0 automatically.

### Step 8: why Network and not Station
Choosing "the station with the most free docks" needs to see **all** stations. Only `Network` holds all of them, so by Information Expert it belongs to `Network`. To compare stations it uses `Station.free_docks` (and `Station.__lt__` for sorting).

## 5. Rule "a bike is in exactly one place"
A bike is **either** in exactly one dock **or** in exactly one active ride, never both and never neither.
- Owners: **Dock** (the bike is docked), **Ride** (the bike is out), **Network** (moves it between the two in one method).
- See README.md for how the code enforces it.
