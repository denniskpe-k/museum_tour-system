"""
patterns/observer.py

Observer Pattern: the LocationSubject broadcasts "a visitor is now
near location X" events to every subscribed Observer, without knowing
or caring who's listening. This is what lets visitor movement
(simulated GPS/beacon signals) trigger location-based content, badge
awards, etc., independently of each other.
"""

from abc import ABC, abstractmethod
from typing import List


class LocationObserver(ABC):
    """Anything that wants to react to a visitor entering a location."""

    @abstractmethod
    def on_location_update(self, visitor_id: str, location_id: str) -> None:
        raise NotImplementedError


class LocationSubject:
    """
    The observable/publisher. The beacon and GPS simulators call
    notify() whenever a visitor's position changes; every registered
    observer gets called in turn.
    """

    def __init__(self):
        self._observers: List[LocationObserver] = []

    def subscribe(self, observer: LocationObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: LocationObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, visitor_id: str, location_id: str) -> None:
        for observer in self._observers:
            observer.on_location_update(visitor_id, location_id)


class ContentTriggerObserver(LocationObserver):
    """
    Concrete observer: when a visitor arrives at a location that has a
    tour stop, deliver that stop's content and log it to the console
    (in the desktop UI this would push it to the screen instead).
    """

    def __init__(self, tour, on_deliver=None):
        self.tour = tour
        self._on_deliver = on_deliver  # optional callback, e.g. UI update

    def on_location_update(self, visitor_id: str, location_id: str) -> None:
        stop = self.tour.stop_at_location(location_id)
        if stop is None:
            return
        message = stop.deliver()
        if self._on_deliver:
            self._on_deliver(visitor_id, stop, message)


class BadgeObserver(LocationObserver):
    """
    Concrete observer: awards gamification points/badges as a visitor
    checks in to new locations, and records the visit on the Visitor.
    """

    def __init__(self, visitor, tour):
        self.visitor = visitor
        self.tour = tour

    def on_location_update(self, visitor_id: str, location_id: str) -> None:
        if visitor_id != self.visitor.visitor_id:
            return
        already_visited = location_id in self.visitor.visited_locations
        self.visitor.record_visit(location_id)
        if not already_visited:
            self.visitor.award_points(10)
            if len(self.visitor.visited_locations) == len(self.tour.stops):
                self.visitor.award_badge(f"Completed: {self.tour.title}")


class AnalyticsObserver(LocationObserver):
    """
    Concrete observer: logs every location update to the
    AnalyticsService so dwell-time, popular-stops, and route reports
    can be generated later — across any visitor, not just the one in
    the current session.
    """

    def __init__(self, analytics_service, tour_id: str):
        self.analytics_service = analytics_service
        self.tour_id = tour_id

    def on_location_update(self, visitor_id: str, location_id: str) -> None:
        self.analytics_service.log_visit(visitor_id, self.tour_id, location_id)


class QuizObserver(LocationObserver):
    """
    Concrete observer: when a visitor arrives at a location that has a
    Quiz attached, triggers a callback so the UI (or console demo) can
    present that quiz. Scoring itself happens elsewhere (Quiz.score);
    this observer only detects the trigger.
    """

    def __init__(self, quizzes_by_location: dict, on_quiz_triggered=None):
        self.quizzes_by_location = quizzes_by_location
        self._on_quiz_triggered = on_quiz_triggered

    def on_location_update(self, visitor_id: str, location_id: str) -> None:
        quiz = self.quizzes_by_location.get(location_id)
        if quiz and self._on_quiz_triggered:
            self._on_quiz_triggered(visitor_id, quiz)
