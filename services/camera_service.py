"""
services/camera_service.py

CameraService captures a "photo" for the social features requirement.

It tries a real laptop webcam first (via OpenCV, if installed and a
camera is actually present), and falls back to generating a placeholder
image with PIL if no camera is available — which is always the case in
this project's sandboxed environment, and will also be true whenever
the app is graded/run on a machine with no webcam. Either way, the
result is a models.social.Photo pointing at a real image file on disk,
so the rest of the app (gallery, sharing, storage) never needs to know
which path was taken.
"""

import os
from datetime import datetime

from models.social import Photo

PHOTOS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "photos")


class CameraService:
    def __init__(self, photos_dir: str = PHOTOS_DIR):
        self.photos_dir = photos_dir
        os.makedirs(self.photos_dir, exist_ok=True)

    def capture_photo(self, visitor_id: str, location_id: str, exhibit_title: str) -> Photo:
        """
        Try a real webcam capture first; fall back to a generated
        placeholder image. Always returns a Photo pointing at a real
        file on disk.
        """
        path = self._try_real_camera_capture(visitor_id, location_id)
        if path is not None:
            return Photo(visitor_id, location_id, exhibit_title, path, is_simulated=False)

        path = self._generate_placeholder_photo(visitor_id, location_id, exhibit_title)
        return Photo(visitor_id, location_id, exhibit_title, path, is_simulated=True)

    def _try_real_camera_capture(self, visitor_id: str, location_id: str):
        """
        Attempt to grab one frame from a real webcam using OpenCV.
        Returns a file path on success, or None if no camera/library
        is available (never raises — this is a "best effort" path).
        """
        try:
            import cv2  # optional dependency, not in requirements.txt by default
        except ImportError:
            return None

        capture = cv2.VideoCapture(0)
        try:
            if not capture.isOpened():
                return None
            success, frame = capture.read()
            if not success:
                return None
            filename = f"{visitor_id}_{location_id}_{self._timestamp()}_camera.jpg"
            path = os.path.join(self.photos_dir, filename)
            cv2.imwrite(path, frame)
            return path
        finally:
            capture.release()

    def _generate_placeholder_photo(self, visitor_id: str, location_id: str, exhibit_title: str) -> str:
        """Generate a simple labeled placeholder image with PIL — no camera needed."""
        from PIL import Image, ImageDraw

        width, height = 480, 360
        image = Image.new("RGB", (width, height), color=(40, 60, 90))
        draw = ImageDraw.Draw(image)

        draw.rectangle([20, 20, width - 20, height - 20], outline=(255, 255, 255), width=3)
        draw.text((40, 40), "Simulated Visitor Photo", fill=(255, 255, 255))
        draw.text((40, 70), exhibit_title, fill=(200, 220, 255))
        draw.text((40, height - 60), f"Visitor: {visitor_id}", fill=(200, 200, 200))
        draw.text((40, height - 40), f"Stop: {location_id}", fill=(200, 200, 200))

        filename = f"{visitor_id}_{location_id}_{self._timestamp()}_sim.jpg"
        path = os.path.join(self.photos_dir, filename)
        image.save(path)
        return path

    @staticmethod
    def _timestamp() -> str:
        return datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
