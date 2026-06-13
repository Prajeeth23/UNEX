import logging
import sys
from pathlib import Path

def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [UNEX] [%(levelname)s] %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "agent.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
