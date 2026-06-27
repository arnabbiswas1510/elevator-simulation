import csv
from typing import List
from collections import deque
from models import Request, Passenger, Elevator, Direction, PassengerState
from scheduler import BaseScheduler

class Simulation:
    def __init__(self, 
                 requests: List[Request], 
                 num_elevators: int, 
                 max_capacity: int, 
                 scheduler: BaseScheduler,
                 door_delay: bool = False):
        self.raw_requests = deque(sorted(requests, key=lambda r: r.time))
        self.elevators = [Elevator(f"E{i+1}", max_capacity) for i in range(num_elevators)]
        self.scheduler = scheduler
        self.door_delay = door_delay
        
        self.current_time = 0
        self.completed_passengers: List[Passenger] = []
        
        # Track door delays: mapping from elevator_id to the tick when they are free to move again
        self.door_delay_locks = {el.id: 0 for el in self.elevators}
        
        # Output log
        self.position_log = []

    def run(self):
        """Run the discrete time simulation until all requests are handled."""
        # Condition to keep running: there are unprocessed requests OR any elevator is not IDLE
        while self.raw_requests or self._any_active_elevators():
            self._tick()
            self.current_time += 1

    def _tick(self):
        # 1. Process new requests arriving at this time
        while self.raw_requests and self.raw_requests[0].time == self.current_time:
            req = self.raw_requests.popleft()
            passenger = Passenger(request=req)
            
            # Assign immediately
            assigned_elevator = self.scheduler.assign_elevator(passenger, self.elevators)
            passenger.assigned_elevator_id = assigned_elevator.id
            assigned_elevator.assigned_passengers.append(passenger)
            assigned_elevator.update_direction()
            
        # 2. Process elevator boarding/alighting and movement
        self._process_elevators()
        
        # 3. Log positions
        log_entry = {"time": self.current_time}
        for el in self.elevators:
            log_entry[el.id] = el.current_floor
        self.position_log.append(log_entry)

    def _any_active_elevators(self) -> bool:
        for el in self.elevators:
            if el.direction != Direction.IDLE or len(el.passengers_onboard) > 0 or len(el.assigned_passengers) > 0:
                return True
        return False

    def _process_elevators(self):
        for el in self.elevators:
            # Check if elevator is delayed by doors opening/closing from a previous tick
            if self.door_delay and self.door_delay_locks[el.id] > self.current_time:
                continue

            doors_opened = False

            # Drop off passengers whose destination is current floor
            staying_onboard = []
            for p in el.passengers_onboard:
                if p.dest == el.current_floor:
                    p.state = PassengerState.COMPLETED
                    p.dropoff_time = self.current_time
                    self.completed_passengers.append(p)
                    doors_opened = True
                else:
                    staying_onboard.append(p)
            el.passengers_onboard = staying_onboard

            # Pick up assigned passengers whose source is current floor
            still_waiting = []
            for p in el.assigned_passengers:
                if p.source == el.current_floor and not el.is_full():
                    p.state = PassengerState.ONBOARD
                    p.pickup_time = self.current_time
                    el.passengers_onboard.append(p)
                    doors_opened = True
                else:
                    still_waiting.append(p)
            el.assigned_passengers = still_waiting

            # If doors opened and we have door delay enabled, lock it for the next tick
            if doors_opened and self.door_delay:
                self.door_delay_locks[el.id] = self.current_time + 1
                el.update_direction()
                continue # Don't move on the tick doors open/close

            # Move elevator
            el.update_direction()
            if el.direction == Direction.UP:
                el.current_floor += 1
            elif el.direction == Direction.DOWN:
                el.current_floor -= 1

    def write_position_log(self, filename: str):
        if not self.position_log:
            return
        
        keys = list(self.position_log[0].keys())
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.position_log)
