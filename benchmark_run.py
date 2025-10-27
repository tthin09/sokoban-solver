import pandas as pd
import os
import tracemalloc
import time
import sys
from datetime import datetime

try:
    from solve import solve_and_print as original_solve_func
except ImportError:
    print("ERROR: File not found. ")
    exit()


def run_solve_with_metrics(map_name, method='A*'):
    """
    Hàm này bọc hàm solve gốc để đo lường thời gian và bộ nhớ.
    """
    print(f"--- Running {method} on {map_name} ---")
    
    tracemalloc.start()
    start_time = time.time() # timestamp

    try:
        solution_str = original_solve_func(map_name, method=method, printout=False)
    except Exception as e:
        print(f"   ERROR: {e}")
        tracemalloc.stop()
        return {
            "map": map_name, "method": method, "time_sec": -1,
            "mem_peak_mb": -1, "solution_len": -1
        }

    # stop
    elapsed = time.time() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    solution_length = -1
    status = "No solution"
    if solution_str is not None:
        solution_length = len(solution_str)
        status = "Solved"

    print(f"   Status: {status}, Time: {elapsed:.3f}s, Peak Mem: {peak / 10**6:.3f} MB, Length: {solution_length}")
    
    return {
        "map": map_name,
        "method": method,
        "time_sec": elapsed,
        "mem_peak_mb": peak / 10**6,
        "solution_len": solution_length
    }

def run_benchmark_for_single_map(map_name):
    """
    Hàm này chạy benchmark cho 1 map duy nhất.
    (Giữ nguyên hàm này)
    """
    all_results = []
    print(f"\n=========================================")
    print(f"BENCHMARKING MAP: {map_name}")
    
    if not os.path.exists(f"maps/{map_name}.png"):
        print(f"WARNING: Map 'maps/{map_name}.png' not found. Skipping.")
        return []

    # Test A*
    stats_astar = run_solve_with_metrics(map_name, method='A*')
    all_results.append(stats_astar)

    # Test BFS
    stats_bfs = run_solve_with_metrics(map_name, method='bfs')
    all_results.append(stats_bfs)
    
    return all_results

if __name__ == "__main__":
    
    if len(sys.argv) != 2:
        print("ERROR: Invalid usage.")
        print("Usage: python benchmark_run.py <map_name>")
        print("Example: python benchmark_run.py map_18")
        sys.exit(1)
        
    # map name
    map_name_from_arg = sys.argv[1]
    
    # run benchmark
    all_results = run_benchmark_for_single_map(map_name_from_arg)


    print("\n\n=========================================")
    print("           FINAL BENCHMARK RESULTS")
    print("=========================================")
    # save result
    if not all_results:
        print(f"No results for {map_name_from_arg}. Did the map exist?")
    else:
        df = pd.DataFrame(all_results)
        df = df.round(3)
        
        print(df.to_string())

        output_dir = "benchmark_results"
        os.makedirs(output_dir, exist_ok=True)
    
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_only = f"benchmark_result_{timestamp}_{map_name_from_arg}.csv"
        

        output_csv_path = os.path.join(output_dir, filename_only)
        
        # save file to CSV
        df.to_csv(output_csv_path, index=False)
        print(f"\nResults also saved to {output_csv_path}")