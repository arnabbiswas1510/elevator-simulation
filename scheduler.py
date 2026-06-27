import math
from typing import List
from models import Elevator, Passenger, Direction

class BaseScheduler:
    def assign_elevator(self, passenger: Passenger, elevators: List[Elevator]) -> Elevator:
        raise NotImplementedError

class NearestCarScheduler(BaseScheduler):
    """
    Assigns the passenger to the nearest elevator moving in the same direction 
    that hasn't passed them yet and has capacity. If none, finds the nearest idle car.
    Otherwise, picks the car with the smallest queue.
    """
    def assign_elevator(self, passenger: Passenger, elevators: List[Elevator]) -> Elevator:
        best_car = None
        best_dist = float('inf')

        # 1. Look for a car moving in the same direction that hasn't passed the source
        for el in elevators:
            if not el.is_full() and len(el.assigned_passengers) + el.current_capacity < el.max_capacity:
                if el.direction == passenger.direction:
                    if (el.direction == Direction.UP and el.current_floor <= passenger.source) or \
                       (el.direction == Direction.DOWN and el.current_floor >= passenger.source):
                        dist = abs(el.current_floor - passenger.source)
                        if dist < best_dist:
                            best_dist = dist
                            best_car = el

        if best_car:
            return best_car

        # 2. Look for the nearest IDLE car
        best_dist = float('inf')
        for el in elevators:
            if el.direction == Direction.IDLE:
                # Idle car could pick them up. Check capacity just in case (should be empty if idle)
                if len(el.assigned_passengers) < el.max_capacity:
                    dist = abs(el.current_floor - passenger.source)
                    if dist < best_dist:
                        best_dist = dist
                        best_car = el
        
        if best_car:
            return best_car

        # 3. Fallback: pick the car with the fewest total passengers (onboard + assigned)
        return min(elevators, key=lambda e: len(e.passengers_onboard) + len(e.assigned_passengers))


class RoundRobinScheduler(BaseScheduler):
    """
    Assigns passengers to elevators in a round-robin fashion, ignoring distance,
    but respecting capacity.
    """
    def __init__(self):
        self.last_assigned_idx = -1

    def assign_elevator(self, passenger: Passenger, elevators: List[Elevator]) -> Elevator:
        n = len(elevators)
        for i in range(1, n + 1):
            idx = (self.last_assigned_idx + i) % n
            el = elevators[idx]
            # Simple capacity check (rough estimate)
            if len(el.passengers_onboard) + len(el.assigned_passengers) < el.max_capacity * 2: # Give it some leeway
                self.last_assigned_idx = idx
                return el
        
        # Fallback
        self.last_assigned_idx = (self.last_assigned_idx + 1) % n
        return elevators[self.last_assigned_idx]


class ZoneBasedScheduler(BaseScheduler):
    """
    Assigns passengers to elevators based on their destination zones.
    E.g., if there are 2 elevators and 10 floors, Elevator 0 handles floors 1-5,
    Elevator 1 handles floors 6-10.
    """
    def __init__(self, num_floors: int):
        self.num_floors = num_floors

    def assign_elevator(self, passenger: Passenger, elevators: List[Elevator]) -> Elevator:
        n = len(elevators)
        zone_size = math.ceil(self.num_floors / n)
        
        # Determine zone based on destination floor
        target_zone = (passenger.dest - 1) // zone_size
        
        # Clamp target zone
        target_zone = max(0, min(target_zone, n - 1))
        
        return elevators[target_zone]
