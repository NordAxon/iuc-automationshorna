import random
from src.logger import setup_logging

logger = setup_logging("inference_service")


def run_inference() -> bool:
    result = random.choice([True, False])
    logger.debug(f"Inference result: {result}")
    return result
