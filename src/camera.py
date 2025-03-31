import threading
import time

import cv2

from src.logger import setup_logging
from src.config import IMAGE_ROTATION

logger = setup_logging("camera")


class FrameGrabber:
    """A threaded camera frame grabber that continuously captures frames in the background.

    Args:
        source (str | int): Camera source (device index or video file path)
        height (int): Desired frame height
        width (int): Desired frame width
        timeout (float): Maximum time to wait for frame retrieval
    """

    def __init__(self, source: str | int, height: int, width: int, timeout: float):
        logger.info(f"Starting frame grabber on video source {source}")
        try:
            self.cap = cv2.VideoCapture(source)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.running = False
            self.lock = threading.Lock()
            self.timeout = timeout
            self.rotate_mode = IMAGE_ROTATION
            self.thread = threading.Thread(target=self._grab_frames, daemon=True)
            self.start()
        except Exception as e:
            logger.exception("Error starting frame grabber")
            raise e

    def start(self):
        """Start the frame grabbing thread."""
        self.running = True
        self.thread.start()

    def stop(self):
        """Stop the frame grabbing thread and release camera resources."""
        self.running = False
        self.thread.join()
        self.cap.release()

    def _grab_frames(self):
        """Background thread that continuously grabs frames from the camera."""
        while self.running:
            with self.lock:
                grabbed = self.cap.grab()
                if not grabbed:
                    logger.error("Could not grab frame from camera")
            time.sleep(0.030)

    def _try_retrieve_frame(self) -> cv2.typing.MatLike | None:
        """Attempt to retrieve a single frame from the camera.

        Returns:
            cv2.typing.MatLike | None: The captured frame or None if retrieval failed
        """
        with self.lock:
            ret, frame = self.cap.read()
            if not ret:
                logger.error("Could not retrieve frame from camera")
            else:
                return frame if ret else None

    def retrieve_frame(self) -> cv2.typing.MatLike | None:
        """Retrieve a frame within the timeout period.

        Returns:
            cv2.typing.MatLike | None: The captured and rotated frame or None if retrieval timed out
        """
        start = time.time()
        while time.time() - start < self.timeout:
            frame = self._try_retrieve_frame()
            if frame is not None:
                return cv2.rotate(frame, self.rotate_mode)
            time.sleep(0.001)
        return None
