"""
ui/video_widget.py

Plays a pre-generated frame sequence (see services/video_generator.py)
as a "video" by swapping a Kivy Image widget's source on a timer. This
avoids depending on Kivy's optional Video widget, which needs an extra
codec backend (gstreamer or ffpyplayer) that isn't guaranteed to
install cleanly on every machine — this widget only needs base Kivy.
"""

import os

from kivy.uix.image import Image
from kivy.clock import Clock


class VideoPlayerWidget(Image):
    """An Image that cycles through a directory of frame_NNN.png files."""

    def __init__(self, fps: float = 8.0, **kwargs):
        super().__init__(**kwargs)
        self.fps = fps
        self._frame_paths = []
        self._frame_index = 0
        self._clock_event = None
        self._playing = False

    def load(self, frames_dir: str, frame_count: int) -> None:
        self.stop()
        self._frame_paths = [
            os.path.join(frames_dir, f"frame_{i:03d}.png") for i in range(frame_count)
        ]
        self._frame_paths = [p for p in self._frame_paths if os.path.exists(p)]
        self._frame_index = 0
        if self._frame_paths:
            self.source = self._frame_paths[0]
            self.reload()

    def play(self) -> None:
        if not self._frame_paths or self._playing:
            return
        self._playing = True
        self._clock_event = Clock.schedule_interval(self._advance, 1.0 / self.fps)

    def pause(self) -> None:
        self._playing = False
        if self._clock_event is not None:
            self._clock_event.cancel()
            self._clock_event = None

    def stop(self) -> None:
        self.pause()
        self._frame_index = 0

    @property
    def is_playing(self) -> bool:
        return self._playing

    def _advance(self, dt):
        if not self._frame_paths:
            return
        self._frame_index = (self._frame_index + 1) % len(self._frame_paths)
        self.source = self._frame_paths[self._frame_index]
        self.reload()
