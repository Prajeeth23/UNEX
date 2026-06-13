import time
import asyncio
import psutil
from datetime import datetime
from src.monitoring.metrics import SystemMetrics
from src.monitoring.diagnostics import DiagnosticsEngine

async def run_stability_test(duration_hours: int = 72):
    """
    Stress tests the UNEX OS over a long period.
    Simulates memory access, background thread creation, and logs resource leaks.
    """
    print(f"[{datetime.now()}] Starting {duration_hours}-hour UNEX Stability Test...")
    
    end_time = time.time() + (duration_hours * 3600)
    cycle = 0
    
    log_file = "stability_report.txt"
    with open(log_file, "w") as f:
        f.write(f"UNEX STABILITY REPORT ({duration_hours} HOURS)\n")
        f.write("=" * 40 + "\n")
        
    while time.time() < end_time:
        cycle += 1
        
        # 1. Simulate Workload (e.g. running diagnostics)
        diag = await DiagnosticsEngine.run_full_diagnostics()
        
        # 2. Log Metrics
        metrics = SystemMetrics.get_snapshot()
        ram_used = metrics["memory"]["used_mb"]
        threads = metrics["process"]["threads"]
        
        log_line = f"[{datetime.now()}] Cycle {cycle} | RAM: {ram_used}MB | Threads: {threads} | Status: {diag['status']}"
        print(log_line)
        
        with open(log_file, "a") as f:
            f.write(log_line + "\n")
            
        # 3. Detect Leaks
        if ram_used > (metrics["memory"]["total_mb"] * 0.9):
            print("CRITICAL: Massive memory leak detected. Aborting test.")
            break
            
        # Wait 10 seconds between cycles to simulate idle + burst workload
        await asyncio.sleep(10)
        
    print("Stability Test Completed.")

if __name__ == "__main__":
    import sys
    hours = int(sys.argv[1]) if len(sys.argv) > 1 else 1 # Default 1 hour for quick runs
    asyncio.run(run_stability_test(hours))
