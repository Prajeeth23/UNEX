import time
import asyncio
import psutil
import sys
import os
from datetime import datetime

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.monitoring.metrics import SystemMetrics
from src.monitoring.diagnostics import DiagnosticsEngine


async def run_stability_test(duration_hours: float = 72, max_cycles: int = None):
    """
    Stress tests the UNEX OS over a long period or target cycle count.
    Simulates memory access, background thread creation, and logs resource leaks.
    """
    mode_desc = f"{max_cycles} cycles" if max_cycles else f"{duration_hours} hours"
    print(f"[{datetime.now()}] Starting UNEX Stability Test ({mode_desc})...")
    
    end_time = time.time() + (duration_hours * 3600)
    cycle = 0
    
    log_file = "stability_report.txt"
    with open(log_file, "w") as f:
        f.write(f"UNEX STABILITY REPORT ({mode_desc})\n")
        f.write("=" * 40 + "\n")
        
    proc = psutil.Process()
    initial_rss = proc.memory_info().rss / (1024 * 1024)
    
    while time.time() < end_time:
        cycle += 1
        
        # 1. Simulate Workload (e.g. running diagnostics)
        diag = await DiagnosticsEngine.run_full_diagnostics()
        
        # 2. Log Metrics
        metrics = SystemMetrics.get_snapshot()
        ram_used = metrics["memory"]["used_mb"]
        threads = metrics["process"]["threads"]
        current_rss = proc.memory_info().rss / (1024 * 1024)
        
        log_line = f"[{datetime.now()}] Cycle {cycle} | Proc RSS: {current_rss:.2f}MB | Sys RAM: {ram_used}MB | Threads: {threads} | Status: {diag['status']}"
        print(log_line)
        
        with open(log_file, "a") as f:
            f.write(log_line + "\n")
            
        # 3. Detect Process-Specific Leaks
        delta_rss = current_rss - initial_rss
        if delta_rss > 250:
            print(f"CRITICAL: Process memory leak detected (+{delta_rss:.2f} MB). Aborting test.")
            return False
            
        if max_cycles and cycle >= max_cycles:
            break
            
        # Short sleep between cycles
        await asyncio.sleep(2)
        
    final_rss = proc.memory_info().rss / (1024 * 1024)
    delta_rss = final_rss - initial_rss
    print(f"Stability Test Completed. Process RSS Delta: {delta_rss:+.2f} MB (Status: Nominal)")
    return True


if __name__ == "__main__":
    import sys
    import argparse
    parser = argparse.ArgumentParser(description="UNEX Stability & Stress Test Runner")
    parser.add_argument("--hours", type=float, default=1.0, help="Test duration in hours")
    parser.add_argument("--cycles", type=int, default=None, help="Maximum number of test cycles")
    args = parser.parse_args()
    asyncio.run(run_stability_test(duration_hours=args.hours, max_cycles=args.cycles))

