import logging

logger = logging.getLogger(__name__)

file_handler = logging.FileHandler("logs/logs.log", mode="w")
formatter = logging.Formatter(
    "%(asctime)s - %(name)s [%(lineno)d] - %(levelname)s - %(message)s",
    datefmt="%b-%d %H:%M:%S",
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

logger.warning("This is a warning message")
