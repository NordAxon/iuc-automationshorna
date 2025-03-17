import os
import time

import cv2
from ultralytics import YOLO

from src.logger import setup_logging

logger = setup_logging("inference_service")
model = YOLO(os.getenv("MODEL_PATH")).to(os.getenv("INFERENCE_DEVICE"))
img_size = int(os.getenv("IMAGE_SIZE"))


def run_inference() -> bool:
    start = time.time()
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, img_size)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, img_size)
    if cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            raise Exception("Could not read frame")
        logger.debug(f"Time to capture frame: {time.time() - start}s")
        result = model.predict(frame, imgsz=img_size, verbose=True)[0]
        logger.debug(result.verbose())
        logger.debug(result.speed)
        result = result.probs.top1 == 0
    else:
        raise Exception("Could not open video capture")
    logger.debug(f"Inference result: {result}")
    logger.debug(f"Total inference time: {time.time() - start}s")
    return result
