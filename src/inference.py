import os
import time

from ultralytics import YOLO

from src.camera import FrameGrabber
from src.logger import setup_logging

logger = setup_logging("inference")
model = YOLO(os.getenv("MODEL_PATH")).to(os.getenv("INFERENCE_DEVICE"))
img_height = int(os.getenv("IMAGE_HEIGHT"))
img_width = int(os.getenv("IMAGE_WIDTH"))
get_image_timeout = float(os.getenv("GET_IMAGE_TIMEOUT"))
try:
    image_source = int(os.getenv("IMAGE_SOURCE"))
except ValueError:
    image_source = os.getenv("IMAGE_SOURCE")


frame_grabber = FrameGrabber(image_source, img_height, img_width, get_image_timeout)


def run_inference() -> bool:
    start = time.time()
    frame = frame_grabber.retrieve_frame()
    if not frame:
        logger.error("Frame capture timed out. Throwing exception.")
        raise Exception("Could not read frame")
    logger.debug(f"Time to capture frame: {time.time() - start}s")
    result = model.predict(frame, imgsz=img_height, verbose=False)[0]
    logger.debug(f"Inference probabilities: {result.verbose()}")
    logger.debug(f"Inference speed: {result.speed}")
    result = result.probs.top1 == 0
    logger.debug(f"Inference result: {result}")
    logger.debug(f"Total inference time: {time.time() - start}s")
    return result
