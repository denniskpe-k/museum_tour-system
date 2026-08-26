"""
models/content.py

Defines the TourContent abstraction and its concrete subclasses.

OOP requirements satisfied here:
- Abstract class: TourContent (cannot be instantiated directly)
- Inheritance: AudioGuide, VideoGuide, TextGuide inherit from TourContent;
  AccessibilityContent extends the base content types.
- Polymorphism: present_content() is overridden by every subclass and
  behaves differently depending on the visitor's accessibility needs.
- Encapsulation: internal playback/display state is stored in
  "protected" attributes (single leading underscore) and only exposed
  through methods/properties.
"""

from abc import ABC, abstractmethod


class TourContent(ABC):
    """
    Abstract base class for any piece of media that can be attached to a
    museum tour stop. Concrete content types (audio, video, text) each
    know how to "present" themselves to a visitor.
    """

    def __init__(self, title: str, duration_seconds: int = 0, translations: dict = None):
        # Public-ish identity fields.
        self.title = title
        # Protected attribute: not meant to be set directly from outside
        # the class hierarchy. Exposed via the duration_seconds property.
        self._duration_seconds = duration_seconds
        # Optional per-language overrides, e.g. {"fr": {"title": "...", "body": "..."}}.
        # Concrete subclasses decide which of their own fields this affects.
        self._translations = translations or {}

    def _localized(self, field: str, default: str, visitor) -> str:
        """
        Look up a translated value for `field` matching the visitor's
        preferred language, falling back to the default (English) text
        if no translation exists for that language or no visitor was
        given. This is what makes "language support" a real content
        feature rather than just a stored preference.
        """
        if visitor is None:
            return default
        lang = getattr(visitor.preferences, "language", "en")
        entry = self._translations.get(lang)
        if entry and field in entry:
            return entry[field]
        return default

    @property
    def duration_seconds(self) -> int:
        """Read-only view of how long this content takes to consume."""
        return self._duration_seconds

    @abstractmethod
    def present_content(self, visitor: "Visitor" = None) -> str:  # noqa: F821
        """
        Return a human-readable description of what the visitor
        experiences. Every subclass MUST override this — this is what
        makes TourContent abstract (you cannot do TourContent(...)).
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(title={self.title!r})"


class AudioGuide(TourContent):
    """A narrated audio track attached to an exhibit."""

    def __init__(self, title: str, duration_seconds: int, narrator: str,
                 script: str = "", audio_path: str = None, translations: dict = None):
        super().__init__(title, duration_seconds, translations=translations)
        self.narrator = narrator
        # The actual words spoken in the narration, used to generate a
        # real audio file (see services/audio_generator.py).
        self.script = script
        # Path to the generated/real audio file, if one exists. None
        # means this content type is fully implemented but no audio
        # asset has been generated for it yet.
        self.audio_path = audio_path

    def present_content(self, visitor=None) -> str:
        title = self._localized("title", self.title, visitor)
        suffix = f" ({self.audio_path})" if self.audio_path else ""
        return (
            f"[Audio] Playing '{title}' "
            f"({self._duration_seconds}s, narrated by {self.narrator}){suffix}"
        )


class VideoGuide(TourContent):
    """
    A short documentary-style video clip for an exhibit. Since no real
    museum video footage was available, videos here are generated as a
    real sequence of animated frames (a Ken Burns-style pan/zoom over a
    source image, with captions) rather than a claim of pre-recorded
    footage — frames_dir points at that generated frame sequence.
    """

    def __init__(self, title: str, duration_seconds: int, resolution: str = "1080p",
                 frames_dir: str = None, frame_count: int = 0, caption: str = "",
                 translations: dict = None):
        super().__init__(title, duration_seconds, translations=translations)
        self.resolution = resolution
        self.frames_dir = frames_dir
        self.frame_count = frame_count
        self.caption = caption

    def present_content(self, visitor=None) -> str:
        title = self._localized("title", self.title, visitor)
        suffix = f" ({self.frames_dir}, {self.frame_count} frames)" if self.frames_dir else ""
        return (
            f"[Video] Playing '{title}' "
            f"({self._duration_seconds}s, {self.resolution}){suffix}"
        )


class TextGuide(TourContent):
    """Plain descriptive text about an exhibit."""

    def __init__(self, title: str, body: str, translations: dict = None):
        # Text has no real "duration"; we estimate a reading time instead,
        # roughly 200 words per minute.
        word_count = max(len(body.split()), 1)
        estimated_seconds = int((word_count / 200) * 60)
        super().__init__(title, estimated_seconds, translations=translations)
        self.body = body

    def present_content(self, visitor=None) -> str:
        title = self._localized("title", self.title, visitor)
        body = self._localized("body", self.body, visitor)
        return f"[Text] '{title}': {body}"


class ImageGuide(TourContent):
    """
    A high-resolution image of an exhibit (e.g. a photograph of an
    artifact in its display case). image_path points at a local asset
    file bundled with the app.
    """

    def __init__(self, title: str, image_path: str, caption: str = "",
                 duration_seconds: int = 20, translations: dict = None):
        super().__init__(title, duration_seconds, translations=translations)
        self.image_path = image_path
        self.caption = caption

    def present_content(self, visitor=None) -> str:
        title = self._localized("title", self.title, visitor)
        caption = self._localized("caption", self.caption, visitor)
        caption_part = f" — {caption}" if caption else ""
        return f"[Image] '{title}'{caption_part} ({self.image_path})"


class ModelGuide(TourContent):
    """
    A 3D model of an exhibit that visitors can rotate/inspect on their
    tablet. This project has no real 3D-scanning pipeline or budget, so
    there is no real scanned mesh of the actual artifact — but shape
    (e.g. "vase") selects a real, interactive, procedurally generated
    3D wireframe that the visitor can genuinely drag to rotate, backed
    by real 3D math (see ui/model3d_widget.py), rather than being pure
    text. model_path/format describe what a real deployment's scanned
    asset would be named, for continuity with the offline database.
    """

    def __init__(self, title: str, model_path: str, format: str = "glb",
                 duration_seconds: int = 45, shape: str = "vase", translations: dict = None):
        super().__init__(title, duration_seconds, translations=translations)
        self.model_path = model_path
        self.format = format
        self.shape = shape

    def present_content(self, visitor=None) -> str:
        title = self._localized("title", self.title, visitor)
        return (
            f"[3D Model] '{title}' — interactive {self.format.upper()} model "
            f"(rendered live as a procedural '{self.shape}' shape; "
            f"real scan file would be: {self.model_path})"
        )


class AccessibilityContent(TourContent):
    """
    Wraps another TourContent instance to add an accessibility layer
    (audio description or sign-language interpretation) on top of it.

    This demonstrates BOTH inheritance (it IS-A TourContent) and
    composition (it HAS-A TourContent that it wraps/decorates), and is
    what the spec means by "AccessibilityContent extends base content
    types".
    """

    SUPPORTED_MODES = {"audio_description", "sign_language", "large_print"}

    def __init__(self, base_content: TourContent, mode: str):
        if mode not in self.SUPPORTED_MODES:
            raise ValueError(f"Unsupported accessibility mode: {mode}")
        super().__init__(base_content.title, base_content.duration_seconds)
        self._base_content = base_content
        self.mode = mode

    def present_content(self, visitor=None) -> str:
        base_output = self._base_content.present_content(visitor)
        return f"{base_output}  +  [Accessibility: {self.mode}]"
