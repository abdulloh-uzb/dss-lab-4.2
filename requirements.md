
Bike sharing network: classes, relationships and encapsulation.
Build console bike sharing app in Python 3.10+ with classes that you find yourself from the requirement text below (Lecture 4). 
Requirement text: Tashkent bike network has stations. Every station has a fixed number of docks and a dock holds at most one bike. A rider (the app calls them users) takes a bike from any station and returns it to any free dock of any station. Every ride is recorded with start station, end station and times. First 15 minutes are free, after that the rider pays 500 sum for every started 5 minutes, but not more than 20 000 sum per ride. One rider can have one active ride only. A bike sent to repair stays in its dock and nobody can take it. The manager sees how many free docks each station has.
    • Class discovery in docs/design.md  Python classes
        ◦ Once requirement text is read, sort every noun and write CRC cards:
            ▪ If noun has data and behaviour → class (6 expected); only a value → attribute; outside the program → actor; two names for one thing → merge; vague word → write the question for the customer.
            ▪ If you find an event with data (the noun you cannot touch) → it is a class, write which of its methods owns the money rule.
            ▪ If one CRC card has more than 4 responsibilities → split the class.
            ▪ Read scenario “rider returns bike to a full station” aloud, every step must name a card. If a step has no owner → add card or move the responsibility; if still no owner after n = 2 rounds → give it to the class that has the data (Information Expert) and write why.
Note: paper or markdown only, no code yet. Cards table: Class | Responsibilities | Collaborators.
    • Bike, Dock and Station protect their own rules  property | dataclasses
        ◦ Once bike is parked into a dock:
            ▪ If dock is free → bike is docked and its status is AVAILABLE.
            ▪ If dock is occupied → DockOccupiedError, bike stays IN_USE (failure).
            ▪ If outside code writes dock.bike = x, bike.status = ... or station.docks.append(...) → it must fail (read-only property, tuple copy).
            ▪ If two Station objects are created → each has its own docks (no mutable class attribute).
            ▪ If bike is in REPAIR → it stays in the dock but cannot be taken; only a docked free bike can be sent to repair.
            ▪ If print(station) → Chilonzor: 4/10 bikes; len(station) = docked bikes; repr is for logs (__str__ vs __repr__).
            ▪ (this part is optional) sorted(stations) orders stations by free docks (__lt__).
Note: no getX()/setX(). Inside data starts with _. @dataclass only for classes that mostly hold data.
    • Ride is an event with data and owns the fee rule  datetime
        ◦ Once ride is finished, the ride itself calculates the fee:
            ▪ If ride lasted 15:00 → 0 sum; 15:01 → 500; 20:00 → 500; 20:01 → 1 000; very long ride → 20 000 (cap).
            ▪ If end time is before start time → ValueError.
            ▪ If the fee formula or one of its numbers (15, 5, 500, 20 000) lives outside Ride → move it (Information Expert); each number is written once, as a constant (DRY).
            ▪ If ReceiptPrinter.print(ride) is called → Chilonzor → Yunusobod, 23 min, 1 000 sum.
Note: time comes as parameter now, never datetime.now() inside a class. Money is int sum.
    • Network runs the ride: take bike and return bike  exceptions
        ◦ Once rider taps “Take” or “Return” at a station:
            ▪ If rider has no active ride and station has a free bike → new Ride starts, bike is IN_USE, rider knows the active ride.
            ▪ If rider already has an active ride → RideActiveError; station without free bike → NoBikeError; return without a ride → NoActiveRideError.
            ▪ If station is full on return → StationFullError, ride clock keeps running, rider can try again (failure).
            ▪ If the same ride fails n = 2 times → error carries the redirect: station with most free docks (tie → name A–Z). The counter lives in the class that has its data.
            ▪ If rider returns the bike to the redirected station → ride is closed, fee is charged, receipt is printed (recovery).
            ▪ (this part is optional) network.report() prints stations by free docks, biggest first: the manager view.
Note: console only: no files, no database, no threads.
    • Relationships table in README.md  UML specification
        ◦ Once all code works, write one row per connected pair: pair | relationship | multiplicity at both ends | file:line that proves it:
            ▪ If a class only gets the other as parameter → dependency; keeps a link to an independent object → association; gets parts from outside, parts live on → aggregation; creates parts inside, they die with it → composition.
            ▪ If you cannot point to one line of code for a row → the row is wrong: fix the table or the code.
            ▪ For every aggregation and composition write the lifetime test: “If I delete X, do Y disappear?”
            ▪ If a multiplicity is not enforced by code (find at least one) → enforce it, or write why it is fine.

Submission.
    1. Upload project to GitHub account to TTPU organizations
        1.1. Private repo, only teacher invited
        1.2. README.md: expandable & collapsable demo video, max 40 seconds, with the exact scenario step by step; run pytest -v at the end (test name = the “If” line it proves):
            1.2.1. happy path: take a bike, return it to a free dock, receipt shows the fee
            1.2.2. failure path: return to a full station, repeated until n = 2 is exhausted
            1.2.3. recovery path: return to the redirected station
            1.2.4. optional part (if done)
        1.3. Do the same for all left items
        1.4. README.md must also contain the relationships table and a code block with your own explanation of how the rule “a bike is in exactly one place” is handled in the repo; docs/design.md must contain nouns and CRC cards. If the readme lacks any asked requirement, the project is considered incomplete (failed).