"""
# logger types:
#     logger.info("Only shown if basicConfig is enabled")
#     logger.warning("this is a warning")
#     logger.debug("a debug one")
#     logger.critical("a scary critical one 😅")
#     ----
#     print(datetime.datetime.utcnow().date().isoformat())
"""

import logging.handlers
import datetime

from constants import LOG_FILE_MAX_SIZE, LOG_BACKUP_COUNT


def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Dynamically generate the filename based on the current date
    current_date = (
        datetime.date.today().isoformat()
    )  # returns date in the format YYYY-MM-DD
    filename = f"logs/app-{current_date}.txt"

    # Create a rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        filename, maxBytes=LOG_FILE_MAX_SIZE, backupCount=LOG_BACKUP_COUNT
    )

    # Create a StreamHandler for console output
    console_handler = logging.StreamHandler()

    # Create a formatter and set it for the handler
    formatter = logging.Formatter(
        # "%(asctime)s %(levelname)-8s: [%(name)s] [%(filename)s:%(lineno)d] %(message)s",
        "%(asctime)s %(levelname)-8s: [%(name)s.py:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Set formatter for both handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add both handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()
