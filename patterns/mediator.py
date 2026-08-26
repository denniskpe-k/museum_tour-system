"""
patterns/mediator.py

Mediator Pattern: TourMediator is the single coordinator that sits
between the location-sensing systems (simulated beacons and GPS), the
Observer notification system, and the Visitor's State machine. Without
a mediator, the beacon simulator, GPS simulator, observer subject, and
visitor state would all need direct references to each other. With
it, each of those pieces only needs to know about the mediator.
"""

from patterns.observer import LocationSubject
from patterns.state import ExploringState


class TourMediator:
    """
    Coordinates location signals coming from either the beacon
    simulator or the GPS simulator, updates the visitor's State, and
    fans the event out to every registered Observer (content delivery,
    badges, etc.).
    """

    def __init__(self, tour):
        self.tour = tour
        self.location_subject = LocationSubject()
        self._visitors = {}  # visitor_id -> Visitor

    def register_visitor(self, visitor) -> None:
        self._visitors[visitor.visitor_id] = visitor
        if visitor.state is None:
            ExploringState().enter(visitor)

    def add_observer(self, observer) -> None:
        self.location_subject.subscribe(observer)

    def handle_beacon_signal(self, visitor_id: str, beacon_id: str) -> None:
        """Beacon signals map 1:1 onto a location id in this simulation."""
        self._route_location_update(visitor_id, beacon_id)

    def handle_gps_signal(self, visitor_id: str, location_id: str) -> None:
        """GPS signals also resolve to a location id (outdoor/large spaces)."""
        self._route_location_update(visitor_id, location_id)

    def _route_location_update(self, visitor_id: str, location_id: str) -> None:
        visitor = self._visitors.get(visitor_id)
        if visitor is None:
            return
        # 1. Update the visitor's State (State pattern).
        visitor.state = visitor.state.handle_arrival(visitor, location_id, self.tour)
        # 2. Fan the event out to every Observer (Observer pattern).
        self.location_subject.notify(visitor_id, location_id)
