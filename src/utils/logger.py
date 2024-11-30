import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Create the logger at module level
logger = logging.getLogger("paper_service")
logger.setLevel(logging.INFO)

# Set up handlers (same configuration as before)
def setup_logging():
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )

    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    # Add file handler
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    file_handler = RotatingFileHandler(
        logs_dir / "paper_service.log",
        maxBytes=10*1024*1024,
        backupCount=5
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)


