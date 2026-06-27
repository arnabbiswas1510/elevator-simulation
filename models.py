from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

class Direction(Enum):
    UP = 1
    DOWN = -1
    IDLE = 0

class PassengerState(Enum):
    WAITING = "WAITING"
    ONBOARD = "ONBOARD"
    COMPLETED = "COMPLETED"

@dataclass
class Request:
    time: int
    id: str
    source: int
    dest: int

@dataclass
class Passenger:
    request: Request
    state: PassengerState = PassengerState.WAITING
    assigned_elevator_id: Optional[str] = None
    pickup_time: Optional[int] = None
    dropoff_time: Optional[int] = None

    @property
    def id(self) -> str:
        return self.request.id

    @property
    def source(self) -> int:
        return self.request.source

    @property
    def dest(self) -> int:
        return self.request.dest

    @property
    def direction(self) -> Direction:
        return Direction.UP if self.dest > self.source else Direction.DOWN

    def wait_time(self) -> Optional[int]:
        if self.pickup_time is not None:
            return self.pickup_time - self.request.time
        return None

    def total_time(self) -> Optional[int]:
        if self.dropoff_time is not None:
            return self.dropoff_time - self.request.time
        return None

class Elevator:
    def __init__(self, elevator_id: str, max_capacity: int, current_floor: int = 1):
        self.id = elevator_id
        self.max_capacity = max_capacity
        self.current_floor = current_floor
        self.direction = Direction.IDLE
        self.passengers_onboard: List[Passenger] = []
        self.assigned_passengers: List[Passenger] = []

    @property
    def current_capacity(self) -> int:
        return len(self.passengers_onboard)

    def is_full(self) -> bool:
        return self.current_capacity >= self.max_capacity

    def get_stops(self) -> List[int]:
        """Returns a list of all floors this elevator needs to stop at."""
        stops = set()
        for p in self.passengers_onboard:
            stops.add(p.dest)
        for p in self.assigned_passengers:
            stops.add(p.source)
        return sorted(list(stops))

    def update_direction(self):
        """Update direction based on remaining stops."""
        stops = self.get_stops()
        if not stops:
            self.direction = Direction.IDLE
            return

        if self.direction == Direction.IDLE:
            # Pick a direction based on the first assigned passenger or nearest stop
            # Simplest logic: move towards the nearest stop
            nearest = min(stops, key=lambda x: abs(x - self.current_floor))
            if nearest > self.current_floor:
                self.direction = Direction.UP
            elif nearest < self.current_floor:
                self.direction = Direction.DOWN
            else:
                self.direction = Direction.IDLE # Already at stop
        elif self.direction == Direction.UP:
            # If there are no stops above us, we must switch direction
            if not any(s > self.current_floor for s in stops):
                self.direction = Direction.DOWN if any(s < self.current_floor for s in stops) else Direction.IDLE
        elif self.direction == Direction.DOWN:
            # If there are no stops below us, we must switch direction
            if not any(s < self.current_floor for s in stops):
                self.direction = Direction.UP if any(s > self.current_floor for s in stops) else Direction.IDLE
