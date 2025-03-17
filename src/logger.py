import logging
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from src.config import LOG_LEVEL

load_dotenv()

CV2_LOG_LEVELS = {
    "VERBOSE": 6,
    "DEBUG": 5,
    "INFO": 4,
    "WARN": 3,
    "WARNING": 3,
    "ERROR": 2,
    "FATAL": 1,
    "CRITICAL": 1,
    "SILENT": 0,
    "NOTSET": 0,
}


def setup_logging(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler("mqtt_service.log", maxBytes=1024 * 1024 * 5)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
