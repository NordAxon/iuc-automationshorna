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
            self.latest_grabbed = False
            self.lock = threading.Lock()
            self.timeout = timeout
            self.thread = threading.Thread(target=self._grab_frames, daemon=True)
            self.thread.start()
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
                self.latest_grabbed = self.cap.grab()
                if not self.latest_grabbed:
                    logger.error("Could not grab frame from camera")
            time.sleep(0.01)

    def _try_retrieve_frame(self) -> cv2.typing.MatLike | None:
        with self.lock:
            if not self.latest_grabbed:
                return None
            ret, frame = self.cap.retrieve()
            self.latest_grabbed = False
            return frame if ret else None

    def retrieve_frame(self) -> cv2.typing.MatLike | None:
        start = time.time()
        while time.time() - start < self.timeout:
            frame = self._try_retrieve_frame()
            if frame:
                return frame
            time.sleep(0.005)
        return None
