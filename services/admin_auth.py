"""
services/admin_auth.py

A minimal authentication gate for the Admin CMS. This is intentionally
simple (a single shared staff PIN, not a real user-account system) —
its purpose is to demonstrate that the Admin CMS is access-controlled
rather than open to any visitor, per the project brief's staff/visitor
role split. A real deployment would replace this with proper staff
accounts and hashed credentials.
"""


class AdminAuthService:
    """Checks a staff-entered PIN against the configured admin PIN."""

    def __init__(self, pin: str = "MUSEUM2026"):
        self._pin = pin
        self._unlocked = False

    def check_pin(self, attempt: str) -> bool:
        """Returns True and unlocks the session if the PIN matches."""
        is_correct = attempt == self._pin
        if is_correct:
            self._unlocked = True
        return is_correct

    @property
    def is_unlocked(self) -> bool:
        return self._unlocked

    def lock(self) -> None:
        """Re-locks the session, e.g. when staff switch back to visitor view."""
        self._unlocked = False
