"""
models/visitor.py

Defines VisitorPreferences and Visitor.

OOP requirements satisfied here:
- Encapsulation: _visitor_path and _preferences are private-by-convention
  attributes. External code cannot reassign them directly; it must go
  through methods (record_visit, update_preferences) that keep the
  object's internal state consistent (e.g. no duplicate path entries).
"""

from typing import List, Optional
from datetime import datetime


class VisitorPreferences:
    """Small value object describing accessibility/language needs."""

    def __init__(
        self,
        language: str = "en",
        needs_audio_description: bool = False,
        needs_sign_language: bool = False,
        needs_large_print: bool = False,
    ):
        self.language = language
        self.needs_audio_description = needs_audio_description
        self.needs_sign_language = needs_sign_language
        self.needs_large_print = needs_large_print

    def accessibility_modes(self) -> List[str]:
        """Return the list of accessibility modes this visitor needs."""
        modes = []
        if self.needs_audio_description:
            modes.append("audio_description")
        if self.needs_sign_language:
            modes.append("sign_language")
        if self.needs_large_print:
            modes.append("large_print")
        return modes


class Visitor:
    """
    Represents a single museum visitor using the guided tour app.
    Holds their current progress through a tour and their preferences.
    """

    def __init__(self, visitor_id: str, name: str, preferences: Optional[VisitorPreferences] = None):
        self.visitor_id = visitor_id
        self.name = name
        self._preferences = preferences or VisitorPreferences()

        # Encapsulated internal state — never mutated directly from
        # outside the class. Other code must call record_visit().
        self._visitor_path: List[str] = []
        # Parallel timestamped log, used for analytics (dwell time,
        # route timing). Kept separate from _visitor_path so existing
        # code that only cares about "where has this visitor been"
        # doesn't need to know about timestamps.
        self._visit_log: List[tuple] = []

        # Points/badges for the gamification feature.
        self._points = 0
        self._badges: List[str] = []

        # Social features: photos taken and comments left (composition —
        # these Photo/Comment objects only make sense as part of this
        # visitor's session).
        self._photos: List["Photo"] = []
        self._comments: List["Comment"] = []

        # Quiz-based gamification: themed collectibles unlocked by
        # scoring perfectly on a stop's quiz.
        self._collectibles: List["Collectible"] = []

        # The visitor's current State object (State design pattern —
        # see patterns/state.py). Stored here so behaviour delegated to
        # the state can still reach back to the visitor if needed.
        self.state = None  # set by VisitorState subclasses on entry

    # -- Encapsulated accessors -------------------------------------

    @property
    def preferences(self) -> VisitorPreferences:
        return self._preferences

    def update_preferences(self, **kwargs) -> None:
        """Controlled way to change preferences after construction."""
        for key, value in kwargs.items():
            if hasattr(self._preferences, key):
                setattr(self._preferences, key, value)

    @property
    def visited_locations(self) -> List[str]:
        """Read-only copy of the path so far — callers can't corrupt it."""
        return list(self._visitor_path)

    def record_visit(self, location_id: str) -> None:
        """The only sanctioned way to extend the visitor's path."""
        if not self._visitor_path or self._visitor_path[-1] != location_id:
            self._visitor_path.append(location_id)
        self._visit_log.append((location_id, datetime.utcnow()))

    @property
    def visit_log(self) -> List[tuple]:
        """Read-only copy of (location_id, timestamp) entries, for analytics."""
        return list(self._visit_log)

    # -- Gamification --------------------------------------------------

    @property
    def points(self) -> int:
        return self._points

    @property
    def badges(self) -> List[str]:
        return list(self._badges)

    def award_points(self, amount: int) -> None:
        self._points += amount

    def award_badge(self, badge_name: str) -> None:
        if badge_name not in self._badges:
            self._badges.append(badge_name)

    # -- Social features -------------------------------------------

    @property
    def photos(self) -> List["Photo"]:
        return list(self._photos)

    def add_photo(self, photo: "Photo") -> None:
        self._photos.append(photo)

    @property
    def comments(self) -> List["Comment"]:
        return list(self._comments)

    def add_comment(self, comment: "Comment") -> None:
        self._comments.append(comment)

    # -- Quiz collectibles -------------------------------------------

    @property
    def collectibles(self) -> List["Collectible"]:
        return list(self._collectibles)

    def award_collectible(self, collectible: "Collectible") -> None:
        if all(c.collectible_id != collectible.collectible_id for c in self._collectibles):
            self._collectibles.append(collectible)

    def __repr__(self) -> str:
        return f"Visitor({self.name!r}, points={self._points}, stops_visited={len(self._visitor_path)})"
