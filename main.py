import argparse
import csv
from models import Request
from scheduler import NearestCarScheduler, RoundRobinScheduler, ZoneBasedScheduler
from simulation import Simulation
from analytics import generate_summary_statistics

def parse_requests(file_path: str) -> list[Request]:
    requests = []
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        # Skip header if it exists
        # Actually prompt says: 
        # time,id,source,dest
        # 0,passenger1,1,51
        
        # Check first line
        header = next(reader, None)
        if header and header[0].strip().lower() != 'time':
            # Not a header, process it
            requests.append(Request(
                time=int(header[0]),
                id=header[1],
                source=int(header[2]),
                dest=int(header[3])
            ))
            
        for row in reader:
            if not row:
                continue
            requests.append(Request(
                time=int(row[0]),
                id=row[1],
                source=int(row[2]),
                dest=int(row[3])
            ))
    return requests

def main():
    parser = argparse.ArgumentParser(description="Elevator System Simulation")
    parser.add_argument("--requests", type=str, required=True, help="Path to CSV file with requests")
    parser.add_argument("--elevators", type=int, default=3, help="Number of elevators")
    parser.add_argument("--floors", type=int, default=50, help="Number of floors in building")
    parser.add_argument("--capacity", type=int, default=10, help="Max passenger capacity per elevator")
    parser.add_argument("--scheduler", type=str, choices=["nearest", "round_robin", "zone"], default="nearest", help="Scheduling algorithm")
    parser.add_argument("--door-delay", action="store_true", help="Add 1-tick delay for opening/closing doors")
    
    args = parser.parse_args()
    
    requests = parse_requests(args.requests)
    
    if args.scheduler == "nearest":
        scheduler = NearestCarScheduler()
    elif args.scheduler == "round_robin":
        scheduler = RoundRobinScheduler()
    elif args.scheduler == "zone":
        scheduler = ZoneBasedScheduler(num_floors=args.floors)
    
    print(f"Starting simulation with {args.elevators} elevators (cap {args.capacity}) on {args.floors} floors using {args.scheduler} scheduler...")
    
    sim = Simulation(
        requests=requests,
        num_elevators=args.elevators,
        max_capacity=args.capacity,
        scheduler=scheduler,
        door_delay=args.door_delay
    )
    
    sim.run()
    
    print(f"Simulation finished at time={sim.current_time}")
    sim.write_position_log("elevator_positions.csv")
    print("Elevator positions logged to elevator_positions.csv")
    
    generate_summary_statistics(sim.completed_passengers)

if __name__ == "__main__":
    main()
