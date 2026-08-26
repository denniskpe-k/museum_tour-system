"""
models/media.py

StopMedia bundles the real-world media files (photos, one video, one
audio track) that belong to a single TourStop, independent of which
TourContent type "drives" that stop (audio/video/text/image/model).

This is what powers the "Media" button in the UI: no matter what a
stop's primary content type is, the Media button always opens the
same three-tab viewer (Photos / Video / Audio) built from this class.
Paths are always relative to the project's assets/ folder and are
never shown to the visitor — the UI only ever displays friendly
titles/captions, or a "not added yet" message if a file is missing.
"""

import os
from typing import List, Optional


class StopMedia:
    """A stop's photo gallery, video clip, and audio track."""

    def __init__(
        self,
        images: List[dict] = None,
        video_path: Optional[str] = None,
        audio_path: Optional[str] = None,
        audio_path_translations: Optional[dict] = None,
    ):
        # Each image is a dict: {"path": "assets/images/foo.jpg", "caption": "..."}
        self.images = images or []
        self.video_path = video_path
        self.audio_path = audio_path
        # Optional per-language audio, e.g. {"fr": "assets/audio/foo_fr.mp3"}.
        # Falls back to audio_path when the current language has no
        # translated recording — same fallback pattern TourContent uses
        # for translated text (models/content.py's _localized).
        self.audio_path_translations = audio_path_translations or {}

    def audio_path_for(self, lang: str) -> Optional[str]:
        """The audio file to play for `lang`, falling back to the
        default (English) track if no translated recording exists."""
        return self.audio_path_translations.get(lang) or self.audio_path

    def existing_images(self, project_root: str) -> List[dict]:
        """Only the images whose files are actually present on disk."""
        return [img for img in self.images if os.path.exists(os.path.join(project_root, img["path"]))]

    def video_exists(self, project_root: str) -> bool:
        return bool(self.video_path) and os.path.exists(os.path.join(project_root, self.video_path))

    def audio_exists(self, project_root: str) -> bool:
        return bool(self.audio_path) and os.path.exists(os.path.join(project_root, self.audio_path))

    def audio_exists_for(self, project_root: str, lang: str) -> bool:
        path = self.audio_path_for(lang)
        return bool(path) and os.path.exists(os.path.join(project_root, path))

    def has_any(self) -> bool:
        return bool(self.images or self.video_path or self.audio_path)
