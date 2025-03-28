import time

from ultralytics import YOLO

from src.camera import FrameGrabber, debug_imshow
from src.logger import setup_logging
from src.config import (
    GET_IMAGE_TIMEOUT,
    IMAGE_HEIGHT,
    IMAGE_WIDTH,
    INFERENCE_DEVICE,
    LOG_LEVEL,
    MODEL_PATH,
)

logger = setup_logging("inference")
model = YOLO(MODEL_PATH).to(INFERENCE_DEVICE)
frame_grabber = FrameGrabber(IMAGE_HEIGHT, IMAGE_WIDTH, GET_IMAGE_TIMEOUT)


def run_inference() -> bool:
    start = time.time()
    frame = frame_grabber.retrieve_frame()
    if frame is None:
        logger.error("Frame capture timed out. Throwing exception.")
        raise TimeoutError("Frame retrieval timed out. Is the camera working?")
    logger.debug(f"Frame size: {frame.shape[1]}x{frame.shape[0]}")
    logger.debug(f"Time to capture frame: {(time.time() - start) * 1000} ms")
    result = model.predict(frame, imgsz=IMAGE_HEIGHT, verbose=False)[0]
    logger.debug(f"Inference speed: {result.speed}")
    logger.debug(f"Inference probabilities: {result.verbose()}")
    result = result.probs.top1 == 0
    logger.debug(f"Inference result: {result}")

    if LOG_LEVEL == "DEBUG":
        debug_imshow(frame, result)

    return result
