"""
models/tour.py

Defines TourStop and Tour.

OOP requirements satisfied here:
- Composition: a Tour is built out of TourStops, and each TourStop
  "has-a" TourContent (and optionally an AccessibilityContent wrapping
  it). None of these parts make sense as standalone objects without
  the Tour that owns them, which is the hallmark of composition
  (as opposed to the weaker "references" relationship).
"""

from typing import List, Optional

from models.content import TourContent
from models.media import StopMedia


class TourStop:
    """
    A single stop along a tour: a physical location (e.g. a gallery
    room or exhibit case) paired with the content that should play
    when a visitor arrives there.
    """

    def __init__(
        self,
        name: str,
        location_id: str,
        content: TourContent,
        order: int,
        description: str = "",
        description_translations: dict = None,
        media: "StopMedia" = None,
    ):
        self.name = name
        # location_id matches the id used by the beacon/GPS simulator,
        # so the Mediator can figure out which stop a visitor is near.
        self.location_id = location_id
        self.content = content
        self.order = order
        # A short, plain-language summary of what this stop is about —
        # shown directly in the UI (never a file path or technical detail).
        self.description = description
        self._description_translations = description_translations or {}
        # The full media library for this stop (photos/video/audio),
        # shown behind the "Media" button rather than inline.
        self.media = media or StopMedia()

    def localized_description(self, visitor=None) -> str:
        """Return this stop's description in the visitor's language,
        falling back to English if no translation is available."""
        if visitor is not None:
            lang = getattr(visitor.preferences, "language", "en")
            entry = self._description_translations.get(lang)
            if entry:
                return entry
        return self.description

    def deliver(self, visitor=None) -> str:
        """Present this stop's content to a visitor."""
        return self.content.present_content(visitor)

    def __repr__(self) -> str:
        return f"TourStop(#{self.order} {self.name!r} @ {self.location_id})"


class Tour:
    """
    A curated sequence of TourStops that a visitor can follow through
    the museum. Tour OWNS its stops (composition) — if the Tour is
    deleted, its stops go with it.
    """

    def __init__(self, tour_id: str, title: str, theme: str, language: str = "en"):
        self.tour_id = tour_id
        self.title = title
        self.theme = theme
        self.language = language
        self._stops: List[TourStop] = []  # composed parts, private by convention

    def add_stop(self, stop: TourStop) -> None:
        self._stops.append(stop)
        self._stops.sort(key=lambda s: s.order)

    @property
    def stops(self) -> List[TourStop]:
        """Read-only view of the ordered stops in this tour."""
        return list(self._stops)

    @property
    def total_duration_seconds(self) -> int:
        return sum(stop.content.duration_seconds for stop in self._stops)

    def stop_at_location(self, location_id: str) -> Optional[TourStop]:
        """Find the TourStop matching a given beacon/GPS location id."""
        for stop in self._stops:
            if stop.location_id == location_id:
                return stop
        return None

    def __repr__(self) -> str:
        return f"Tour({self.title!r}, {len(self._stops)} stops, {self.theme})"
