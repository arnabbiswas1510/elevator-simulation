# Elevator System Simulation

This is a Python-based discrete-time simulation of a Destination Dispatch elevator system.

## Features
- Models time in discrete units (1 tick = 1 floor of travel).
- Configurable number of elevators, maximum capacity, and total floors.
- Configurable scheduling algorithms (`nearest`, `round_robin`, `zone`).
- Optional 1-tick door delay configuration (`--door-delay`).
- Outputs an elevator positions log (`elevator_positions.csv`) and prints passenger summary statistics.

## Requirements
- Python 3.9+
- No external dependencies (uses standard library).

## Usage

Create a CSV file with your elevator requests (e.g. `requests.csv`):
```csv
time,id,source,dest
0,passenger1,1,51
0,passenger2,1,37
10,passenger3,20,1
```

Run the simulation:
```bash
python main.py --requests requests.csv --elevators 3 --floors 50 --capacity 10 --scheduler nearest --door-delay
```

### Arguments:
- `--requests`: Path to the CSV file containing requests (required).
- `--elevators`: Number of elevators in the building (default: 3).
- `--floors`: Number of floors in the building (default: 50).
- `--capacity`: Max passenger capacity per elevator (default: 10).
- `--scheduler`: The dispatch algorithm to use (`nearest`, `round_robin`, `zone`) (default: `nearest`).
- `--door-delay`: Flag to enable a 1-tick delay when doors open/close for boarding.

## Output
1. **`elevator_positions.csv`**: A row-by-row log of elevator positions at every time step.
2. **Summary Statistics**: Min, Max, Average Wait Times and Total Times printed to the console.

## Architecture
- `models.py`: Defines the `Request`, `Passenger`, and `Elevator` data models.
- `scheduler.py`: Contains the dispatch logic (`NearestCarScheduler`, `RoundRobinScheduler`, `ZoneBasedScheduler`).
- `simulation.py`: The discrete-time simulation engine.
- `analytics.py`: Helper functions to generate summary statistics.
- `main.py`: CLI interface.

## Trade-offs and Assumptions
- **Instantaneous Boarding vs Door Delays**: Boarding and alighting takes 0 ticks by default to simplify math, but the `--door-delay` flag was added to introduce a realistic 1-tick penalty when opening/closing doors.
- **Simplistic Direction Changes**: Elevators will continue in their current direction as long as there is a pending stop in that direction. This mimics the standard SCAN algorithm.
- **Nearest Car Edge Cases**: The `NearestCarScheduler` is a greedy algorithm. It attempts to find a car moving in the same direction, but if multiple requests arrive simultaneously, it might lead to sub-optimal global routing (starvation of distant floors) compared to a more advanced cost-based zone optimizer.
