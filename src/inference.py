import os
import time

import cv2
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
    if frame is None:
        logger.error("Frame capture timed out. Throwing exception.")
        raise Exception("Could not read frame")
    logger.debug(f"Frame size: {frame.shape[1]}x{frame.shape[0]}")
    logger.debug(f"Time to capture frame: {(time.time() - start)*1000}ms")
    result = model.predict(frame, imgsz=img_height, verbose=False)[0]
    logger.debug(f"Inference speed: {result.speed}")
    logger.debug(f"Inference probabilities: {result.verbose()}")
    result = result.probs.top1 == 0
    logger.debug(f"Inference result: {result}")

    if os.getenv("LOG_LEVEL") == "DEBUG":
        color = (0, 0, 255) if result else (0, 255, 0)
        height, width = frame.shape[:2]
        thickness = 10
        cv2.rectangle(frame, (0, 0,),  (width-1, height-1), color, thickness)
        cv2.imshow("debug", frame)
        cv2.waitKey(1)

    return result
