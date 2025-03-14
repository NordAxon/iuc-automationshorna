from src.logger import setup_logging

logger = setup_logging("mqtt_service")


def bool_to_bytes(value: bool) -> bytes:
    """Convert a boolean to bytes representation."""
    return b"1" if value else b"0"


def bytes_to_bool(value: bytes) -> bool:
    """Convert bytes to boolean.

    Args:
        value: Bytes containing either b"1" or b"0"

    Raises:
        ValueError: If value is neither b"1" nor b"0"
    """
    if value not in (b"0", b"1"):
        logger.error(f"Invalid bytes value: {value}")
        raise ValueError(f"Invalid boolean bytes value: {value}. Expected b'0' or b'1'")
    return value == b"1"
