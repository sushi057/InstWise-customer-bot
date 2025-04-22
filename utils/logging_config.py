import logging
import os
import sys
from logging.handlers import RotatingFileHandler

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
LOG_LEVEL = os.getenv(
    "LOG_LEVEL", "INFO"
).upper()  # Default to INFO, allow override via env var


def setup_logging():
    """Configures logging for the entire application."""

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)

    # --- Console Handler ---
    console_handler = logging.StreamHandler(sys.stdout)  # Log to stdout
    console_handler.setLevel(LOG_LEVEL)
    console_formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(console_formatter)

    # --- File Handler (Optional, but recommended for production) ---
    log_dir = "logs"
    file_handler = None
    try:
        os.makedirs(log_dir, exist_ok=True)  # Create log directory if it doesn't exist
        log_file = os.path.join(log_dir, "app.log")

        # RotatingFileHandler keeps logs from getting too large
        # Max 5MB per file, keep 5 backup files
        # Always start with a fresh log file on server restart
        if os.path.exists(log_file):
            os.remove(log_file)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setLevel(LOG_LEVEL)
        file_formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
    except Exception as e:
        # Log to console if file handler setup fails
        root_logger.warning(f"Failed to set up file logging: {e}")

    # --- Add Handlers to Root Logger ---
    # Avoid adding duplicate handlers if this function is called multiple times
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)
        if file_handler:
            root_logger.addHandler(file_handler)  # Add file handler if created
        root_logger.info("Logging configured successfully.")
    else:
        # If handlers exist, maybe update levels or formatters if needed,
        # but typically setup should only run once.
        root_logger.debug("Logging already configured.")


# Example of silencing overly verbose libraries (adjust as needed)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("boto3").setLevel(logging.WARNING)
logging.getLogger("botocore").setLevel(logging.WARNING)
