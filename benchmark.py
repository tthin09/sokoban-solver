import pandas as pd
import os
import tracemalloc
import time
import sys
from datetime import datetime
import matplotlib.pyplot as plt
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
        solution_str, expanded = original_solve_func(map_name, method=method, printout=False)  
    except Exception as e:
        print(f" ERROR: {e}")
        tracemalloc.stop()
        return {
            "map": map_name, "method": method, "time_sec": -1,
            "mem_peak_mb": -1, "solution_len": -1, "nodes_expanded": -1
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
    print(f" Status: {status}, Time: {elapsed:.3f}s, Peak Mem: {peak / 10**6:.3f} MB, Length: {solution_length}, Nodes Expanded: {expanded}")
   
    return {
        "map": map_name,
        "method": method,
        "time_sec": elapsed,
        "mem_peak_mb": peak / 10**6,
        "solution_len": solution_length,
        "nodes_expanded": expanded 
    }

def run_benchmark_for_single_map(map_name):
    """
    Hàm này chạy benchmark cho 1 map duy nhất.
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

def run_benchmark_all_maps():
    """
    Hàm này chạy benchmark cho tất cả maps trong thư mục maps/.
    """
    all_results = []
    maps_dir = "maps"
    if not os.path.exists(maps_dir):
        print(f"ERROR: Directory '{maps_dir}' not found.")
        return []
   
    map_files = [f for f in os.listdir(maps_dir) if f.endswith('.png')]
    if not map_files:
        print("WARNING: No .png maps found in 'maps/' directory.")
        return []
   
    for map_file in sorted(map_files):  # Sort để thứ tự ổn định
        map_name = map_file[:-4]  # remove .png
        print(f"\n=========================================")
        print(f"BENCHMARKING MAP: {map_name}")
       
        if not os.path.exists(f"tile_maps/{map_name}.csv"):
            print(f"WARNING: CSV for '{map_name}' not found. Skipping.")
            continue
       
        # Test A*
        stats_astar = run_solve_with_metrics(map_name, method='A*')
        all_results.append(stats_astar)
        # Test BFS
        stats_bfs = run_solve_with_metrics(map_name, method='bfs')
        all_results.append(stats_bfs)
   
    return all_results

def plot_comparison(df):
    """
    Vẽ đồ thị so sánh A* vs BFS cho từng metric.
    """
    if df.empty:
        print("No data to plot.")
        return
   
    metrics = ['time_sec', 'mem_peak_mb', 'solution_len', 'nodes_expanded']
    output_dir = "benchmark_results"
    os.makedirs(output_dir, exist_ok=True)
   
    for metric in metrics:
        plt.figure(figsize=(12, 6))
        maps = df['map'].unique()
        x = range(len(maps))
        width = 0.35
   
        astar_data = df[df['method'] == 'A*'][metric]
        bfs_data = df[df['method'] == 'bfs'][metric]
       
        plt.bar([i - width/2 for i in x], astar_data, width, label='A*')
        plt.bar([i + width/2 for i in x], bfs_data, width, label='BFS')
       
        plt.xlabel('Maps')
        plt.ylabel(metric.replace('_', ' ').title())
        plt.title(f'Comparison of {metric.replace("_", " ").title()} between A* and BFS')
        plt.xticks(x, maps, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
       
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_filename = f"comparison_{metric}_{timestamp}.png"
        plot_path = os.path.join(output_dir, plot_filename)
        plt.savefig(plot_path)
        plt.close()
        print(f"Plot saved to {plot_path}")

if __name__ == "__main__":
   
    all_results = []
    if len(sys.argv) == 2:  
        map_name_from_arg = sys.argv[1]
        all_results = run_benchmark_for_single_map(map_name_from_arg)
    else:  
        print("No map arg provided. Running benchmark on ALL maps in 'maps/' directory.")
        all_results = run_benchmark_all_maps()
   
    print("\n\n=========================================")
    print(" FINAL BENCHMARK RESULTS")
    print("=========================================")
    # save result
    if not all_results:
        print(f"No results. Check if maps exist.")
    else:
        df = pd.DataFrame(all_results)
        df = df.round(3)
       
        print(df.to_string())
        output_dir = "benchmark_results"
        os.makedirs(output_dir, exist_ok=True)
   
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if len(sys.argv) == 2:
            filename_only = f"benchmark_result_{timestamp}_{sys.argv[1]}.csv"
        else:
            filename_only = f"benchmark_result_all_maps_{timestamp}.csv"
       
        output_csv_path = os.path.join(output_dir, filename_only)
       
        # save file to CSV
        df.to_csv(output_csv_path, index=False)
        print(f"\nResults also saved to {output_csv_path}")
        
        # plot
        plot_comparison(df)