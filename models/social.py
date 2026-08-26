"""
models/social.py

Small value objects for the "social features" requirement: visitors
can capture a photo at an exhibit and leave comments on a stop.

These are kept as plain data classes (no behaviour beyond formatting)
because the interesting logic — how a photo actually gets captured —
lives in services/camera_service.py, and how photos/comments attach
to a Visitor is handled through Visitor's own encapsulated methods
(see models/visitor.py).
"""

from datetime import datetime


class Photo:
    """A photo a visitor has taken at a tour stop."""

    def __init__(
        self,
        visitor_id: str,
        location_id: str,
        exhibit_title: str,
        image_path: str,
        is_simulated: bool = True,
        taken_at: datetime = None,
    ):
        self.visitor_id = visitor_id
        self.location_id = location_id
        self.exhibit_title = exhibit_title
        self.image_path = image_path
        self.is_simulated = is_simulated
        self.taken_at = taken_at or datetime.utcnow()

    def __repr__(self) -> str:
        source = "simulated" if self.is_simulated else "camera"
        return f"Photo({self.exhibit_title!r}, {source}, {self.image_path})"


class Comment:
    """A short comment a visitor left on a tour stop."""

    def __init__(self, visitor_id: str, location_id: str, text: str, posted_at: datetime = None):
        self.visitor_id = visitor_id
        self.location_id = location_id
        self.text = text
        self.posted_at = posted_at or datetime.utcnow()

    def __repr__(self) -> str:
        return f"Comment({self.location_id!r}, {self.text[:30]!r})"


def build_share_text(exhibit_title: str, photo: "Photo" = None, comment: "Comment" = None) -> str:
    """
    Builds a plain-text "share card" for an exhibit, combining an
    optional photo reference and an optional comment. This is the
    software-only stand-in for the brief's "sharing" requirement: on
    desktop it is copied to the clipboard for the visitor to paste
    anywhere; on a real device build this same text could be handed to
    the OS's native share sheet instead.
    """
    lines = [f"Check out this exhibit: {exhibit_title}"]
    if photo is not None:
        source = "a photo I took" if not photo.is_simulated else "a snapshot"
        lines.append(f"({source}: {photo.image_path})")
    if comment is not None:
        lines.append(f'"{comment.text}"')
    lines.append("— shared from the Museum Guided Tour System")
    return "\n".join(lines)
