def bool_to_bytes(value: bool) -> bytes:
    """Convert a boolean to bytes representation."""
    return b"1" if value else b"0"


def bytes_to_bool(value: bytes) -> bool:
    """Convert bytes to boolean."""
    return value == b"1"
