"""
patterns/factory.py

Factory Pattern: centralises object creation for TourContent and Tour
objects so calling code never has to know which concrete subclass to
instantiate. This keeps construction logic (validation, applying
accessibility wrapping, choosing the right subclass) in one place.
"""

from models.content import (
    AudioGuide, VideoGuide, TextGuide, ImageGuide, ModelGuide,
    AccessibilityContent, TourContent,
)
from models.tour import Tour, TourStop
from models.visitor import Visitor, VisitorPreferences
from models.media import StopMedia


class ContentFactory:
    """Creates the right TourContent subclass from a simple spec dict."""

    @staticmethod
    def create_content(content_type: str, **kwargs) -> TourContent:
        content_type = content_type.lower()
        if content_type == "audio":
            return AudioGuide(
                title=kwargs["title"],
                duration_seconds=kwargs.get("duration_seconds", 60),
                narrator=kwargs.get("narrator", "Museum Staff"),
                script=kwargs.get("script", ""),
                audio_path=kwargs.get("audio_path"),
                translations=kwargs.get("translations"),
            )
        elif content_type == "video":
            return VideoGuide(
                title=kwargs["title"],
                duration_seconds=kwargs.get("duration_seconds", 120),
                resolution=kwargs.get("resolution", "1080p"),
                frames_dir=kwargs.get("frames_dir"),
                frame_count=kwargs.get("frame_count", 0),
                caption=kwargs.get("caption", ""),
                translations=kwargs.get("translations"),
            )
        elif content_type == "text":
            return TextGuide(title=kwargs["title"], body=kwargs.get("body", ""),
                              translations=kwargs.get("translations"))
        elif content_type == "image":
            return ImageGuide(
                title=kwargs["title"],
                image_path=kwargs["image_path"],
                caption=kwargs.get("caption", ""),
                duration_seconds=kwargs.get("duration_seconds", 20),
                translations=kwargs.get("translations"),
            )
        elif content_type == "model":
            return ModelGuide(
                title=kwargs["title"],
                model_path=kwargs["model_path"],
                format=kwargs.get("format", "glb"),
                duration_seconds=kwargs.get("duration_seconds", 45),
                shape=kwargs.get("shape", "vase"),
                translations=kwargs.get("translations"),
            )
        else:
            raise ValueError(f"Unknown content_type: {content_type}")

    @staticmethod
    def wrap_for_accessibility(content: TourContent, mode: str) -> AccessibilityContent:
        return AccessibilityContent(base_content=content, mode=mode)


class TourFactory:
    """
    Builds complete Tour objects (with their stops) from a plain
    dictionary description, e.g. as loaded from the offline SQLite
    cache or a JSON tour definition.
    """

    @staticmethod
    def create_tour(tour_spec: dict) -> Tour:
        tour = Tour(
            tour_id=tour_spec["tour_id"],
            title=tour_spec["title"],
            theme=tour_spec.get("theme", "general"),
            language=tour_spec.get("language", "en"),
        )
        for stop_spec in tour_spec.get("stops", []):
            content = ContentFactory.create_content(
                stop_spec["content_type"], **stop_spec.get("content_kwargs", {})
            )
            media_spec = stop_spec.get("media", {})
            media = StopMedia(
                images=media_spec.get("images", []),
                video_path=media_spec.get("video_path"),
                audio_path=media_spec.get("audio_path"),
                audio_path_translations=media_spec.get("audio_path_translations", {}),
            )
            stop = TourStop(
                name=stop_spec["name"],
                location_id=stop_spec["location_id"],
                content=content,
                order=stop_spec["order"],
                description=stop_spec.get("description", ""),
                description_translations=stop_spec.get("description_translations"),
                media=media,
            )
            tour.add_stop(stop)
        return tour


class VisitorFactory:
    """Creates Visitor objects, applying default preferences."""

    @staticmethod
    def create_visitor(visitor_id: str, name: str, **pref_kwargs) -> Visitor:
        prefs = VisitorPreferences(**pref_kwargs) if pref_kwargs else VisitorPreferences()
        return Visitor(visitor_id=visitor_id, name=name, preferences=prefs)
