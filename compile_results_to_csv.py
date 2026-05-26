#!/usr/bin/env python3
# compile_results_to_csv.py
# Scans the results/ subdirectories, extracts trial run metrics, and aggregates them into a clean CSV.

import os
import json
import csv
import glob

def main():
    results_dir = "results"
    csv_file = os.path.join(results_dir, "sweep_metrics_summary.csv")
    
    headers = [
        "gpu_memory_utilization",
        "max_num_seqs",
        "max_num_batched_tokens",
        "run_number",
        "total_token_throughput",
        "request_throughput",
        "output_throughput",
        "median_ttft_ms",
        "p99_ttft_ms",
        "median_tpot_ms",
        "p99_tpot_ms",
        "mean_itl_ms",
        "mean_e2el_ms",
        "completed",
        "failed"
    ]
    
    rows = []
    
    # Find all run=*.json files inside the results subdirectories
    json_pattern = os.path.join(results_dir, "SERVE--*", "run=*.json")
    for filepath in glob.glob(json_pattern):
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                
            # If it's a list, take the first element
            if isinstance(data, list):
                data = data[0]
                
            row = {
                "gpu_memory_utilization": data.get("gpu_memory_utilization"),
                "max_num_seqs": data.get("max_num_seqs"),
                "max_num_batched_tokens": data.get("max_num_batched_tokens"),
                "run_number": data.get("run_number"),
                "total_token_throughput": data.get("total_token_throughput"),
                "request_throughput": data.get("request_throughput"),
                "output_throughput": data.get("output_throughput"),
                "median_ttft_ms": data.get("median_ttft_ms"),
                "p99_ttft_ms": data.get("p99_ttft_ms"),
                "median_tpot_ms": data.get("median_tpot_ms"),
                "p99_tpot_ms": data.get("p99_tpot_ms"),
                "mean_itl_ms": data.get("mean_itl_ms"),
                "mean_e2el_ms": data.get("mean_e2el_ms"),
                "completed": data.get("completed"),
                "failed": data.get("failed")
            }
            rows.append(row)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            
    # Sort rows by memory limit, then seq concurrency, then run number
    rows.sort(key=lambda x: (x["gpu_memory_utilization"] or 0, x["max_num_seqs"] or 0, x["run_number"] or 0))
    
    # Write to CSV
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            
    print(f"Successfully compiled {len(rows)} runs into {csv_file}")

if __name__ == "__main__":
    main()
