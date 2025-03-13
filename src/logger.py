import logging
from logging.handlers import RotatingFileHandler


def setup_logging(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler("mqtt_service.log", maxBytes=1024 * 1024 * 5)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
