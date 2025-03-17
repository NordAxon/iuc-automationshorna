import os
import threading
import time

import cv2

from src.logger import setup_logging

logger = setup_logging("camera")


class FrameGrabber:
    def __init__(self, source: str | int, height: int, width: int, timeout: float):
        logger.info(f"Starting frame grabber on video source {source}")
        try:
            self.cap = cv2.VideoCapture(source)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.running = False
            self.lock = threading.Lock()
            self.timeout = timeout
            self.rotate_mode = int(os.getenv("IMAGE_ROTATION"))
            self.thread = threading.Thread(target=self._grab_frames, daemon=True)
            self.start()
        except Exception as e:
            logger.exception("Error starting frame grabber")
            raise e

    def start(self):
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()
        self.cap.release()

    def _grab_frames(self):
        while self.running:
            with self.lock:
                grabbed = self.cap.grab()
                if not grabbed:
                    logger.error("Could not grab frame from camera")
            time.sleep(0.015)

    def _try_retrieve_frame(self) -> cv2.typing.MatLike | None:
        with self.lock:
            ret, frame = self.cap.read()
            if not ret:
                logger.error("Could not retrieve frame from camera")
            else:
                return frame if ret else None

    def retrieve_frame(self) -> cv2.typing.MatLike | None:
        start = time.time()
        while time.time() - start < self.timeout:
            frame = self._try_retrieve_frame()
            if frame is not None:
                return cv2.rotate(frame, self.rotate_mode)
            time.sleep(0.001)
        return None
