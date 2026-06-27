from typing import List
from models import Passenger

def generate_summary_statistics(completed_passengers: List[Passenger]):
    if not completed_passengers:
        print("No passengers were served.")
        return

    wait_times = []
    total_times = []

    for p in completed_passengers:
        wt = p.wait_time()
        tt = p.total_time()
        if wt is not None:
            wait_times.append(wt)
        if tt is not None:
            total_times.append(tt)

    if not wait_times or not total_times:
        print("Insufficient data for statistics.")
        return

    min_wait = min(wait_times)
    max_wait = max(wait_times)
    avg_wait = sum(wait_times) / len(wait_times)

    min_total = min(total_times)
    max_total = max(total_times)
    avg_total = sum(total_times) / len(total_times)

    # Calculate 95th percentiles (useful observation metric)
    sorted_wait = sorted(wait_times)
    p95_wait = sorted_wait[int(len(sorted_wait) * 0.95)] if len(sorted_wait) > 0 else 0
    
    sorted_total = sorted(total_times)
    p95_total = sorted_total[int(len(sorted_total) * 0.95)] if len(sorted_total) > 0 else 0

    print("========================================")
    print("      PASSENGER SUMMARY STATISTICS      ")
    print("========================================")
    print(f"Total Passengers Served: {len(completed_passengers)}")
    print(f"Wait Times:  Min={min_wait}, Max={max_wait}, Avg={avg_wait:.2f} (95th Pctl={p95_wait})")
    print(f"Total Times: Min={min_total}, Max={max_total}, Avg={avg_total:.2f} (95th Pctl={p95_total})")
    print("========================================")
    print("Notable Observations:")
    if max_wait > avg_wait * 3 and max_wait > 5:
        print(f" - Long tail wait times detected. Max wait ({max_wait}) is significantly higher than average ({avg_wait:.2f}). Some passengers experienced starvation.")
    else:
        print(" - Wait times appear relatively balanced across passengers.")
    print("========================================\n")
