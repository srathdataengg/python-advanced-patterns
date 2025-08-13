import logging
import sys

# ------------------------------------
# 1. Create a logger instance
# -------------------------------------

logger = logging.getLogger("Python advance project")
logger.setLevel(logging.DEBUG)  # Default level for logging

# -----------------------------------------
# 2. Create a console handler
# ----------------------------------------

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)  # Log everything to console

# -----------------------------------------
# 3. Create a file handler (optional)
# -----------------------------------------

file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.INFO)  # Only Info goes to file

# ---------------------------------------
# 4. Define a log format
# ---------------------------------------

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# ---------------------------------------
# 5. Add handlers to logger
# --------------------------------------

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# ------------------------------
# 6. Now you can use:
#    logger.debug("Debug message")
#    logger.info("Info message")
#    logger.warning("Warning message")
#    logger.error("Error message")
#    logger.critical("Critical message")
# ------------------------------
