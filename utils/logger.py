# utils/logger.py

import logging
import sys
from pathlib import Path

# -----------------------------------
# Base logger configuration
# -----------------------------------

# Ensure log file directory exists
log_file = Path("app.log")
log_file.parent.mkdir(parents=True, exist_ok=True)

# Create formatter (shared)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

# File handler
file_handler = logging.FileHandler(log_file, mode="a")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Root logger config
logging.basicConfig(level=logging.DEBUG, handlers=[console_handler, file_handler])


def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger with the given name,
    already configured with console & file handlers.
    """
    return logging.getLogger(name)


# Example usage when running this file directly
if __name__ == "__main__":
    logger = get_logger("TestLogger")
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

logger = get_logger(__name__)
