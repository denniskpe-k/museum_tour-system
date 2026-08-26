"""
patterns/state.py

State Pattern: a Visitor's behaviour (what "arriving somewhere" means)
changes depending on which state they're currently in — Exploring
(walking between exhibits), AtStop (standing at a tour stop consuming
content), or InGallery (browsing freely within a themed room without a
specific stop active). Each state knows how to transition to the next
one; the Visitor object just delegates to whichever state it currently
holds.
"""

from abc import ABC, abstractmethod


class VisitorState(ABC):
    """Common interface for every state a Visitor can be in."""

    name = "base"

    @abstractmethod
    def enter(self, visitor) -> None:
        """Called when the visitor transitions into this state."""
        raise NotImplementedError

    @abstractmethod
    def handle_arrival(self, visitor, location_id: str, tour) -> "VisitorState":
        """
        Called when a location update arrives while the visitor is in
        this state. Returns the VisitorState the visitor should be in
        next (which may be the same state instance's class, or a new
        one).
        """
        raise NotImplementedError


class ExploringState(VisitorState):
    """Visitor is moving between exhibits with no active content."""

    name = "exploring"

    def enter(self, visitor) -> None:
        visitor.state = self

    def handle_arrival(self, visitor, location_id: str, tour) -> VisitorState:
        stop = tour.stop_at_location(location_id)
        if stop is not None:
            next_state = AtStopState()
            next_state.enter(visitor)
            return next_state
        gallery_state = InGalleryState()
        gallery_state.enter(visitor)
        return gallery_state


class AtStopState(VisitorState):
    """Visitor is standing at a tour stop, actively consuming content."""

    name = "at_stop"

    def enter(self, visitor) -> None:
        visitor.state = self

    def handle_arrival(self, visitor, location_id: str, tour) -> VisitorState:
        # Any further movement means they've left the stop.
        stop = tour.stop_at_location(location_id)
        if stop is not None:
            # Moved directly to a different stop — stay AtStop.
            return self
        exploring = ExploringState()
        exploring.enter(visitor)
        return exploring


class InGalleryState(VisitorState):
    """Visitor is browsing freely inside a gallery, not at a specific stop."""

    name = "in_gallery"

    def enter(self, visitor) -> None:
        visitor.state = self

    def handle_arrival(self, visitor, location_id: str, tour) -> VisitorState:
        stop = tour.stop_at_location(location_id)
        if stop is not None:
            at_stop = AtStopState()
            at_stop.enter(visitor)
            return at_stop
        return self
