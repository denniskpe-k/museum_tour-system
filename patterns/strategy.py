"""
patterns/strategy.py

Strategy Pattern: different algorithms for recommending which tour
stop a visitor should go to next, all interchangeable behind a common
interface (RecommendationStrategy.recommend_next_stop). The app can
swap strategies at runtime without changing any calling code.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from models.tour import Tour, TourStop
from models.visitor import Visitor


class RecommendationStrategy(ABC):
    """Common interface every recommendation algorithm must implement."""

    @abstractmethod
    def recommend_next_stop(self, tour: Tour, visitor: Visitor) -> Optional[TourStop]:
        raise NotImplementedError


class SequentialStrategy(RecommendationStrategy):
    """Always recommend the next unvisited stop, in curated order."""

    def recommend_next_stop(self, tour: Tour, visitor: Visitor) -> Optional[TourStop]:
        visited = set(visitor.visited_locations)
        for stop in tour.stops:
            if stop.location_id not in visited:
                return stop
        return None


class PopularityStrategy(RecommendationStrategy):
    """
    Recommend the stop with the shortest content duration among
    unvisited stops — a simple stand-in for 'most people finish this
    one quickly, so it stays popular even near closing time'.
    """

    def recommend_next_stop(self, tour: Tour, visitor: Visitor) -> Optional[TourStop]:
        visited = set(visitor.visited_locations)
        candidates = [s for s in tour.stops if s.location_id not in visited]
        if not candidates:
            return None
        return min(candidates, key=lambda s: s.content.duration_seconds)


class PersonalizedStrategy(RecommendationStrategy):
    """
    Recommend the next unvisited stop, but skip anything whose content
    doesn't match the visitor's language, favouring accessibility fit.
    Falls back to SequentialStrategy if nothing matches.
    """

    def __init__(self):
        self._fallback = SequentialStrategy()

    def recommend_next_stop(self, tour: Tour, visitor: Visitor) -> Optional[TourStop]:
        visited = set(visitor.visited_locations)
        preferred_modes = set(visitor.preferences.accessibility_modes())
        best = None
        for stop in tour.stops:
            if stop.location_id in visited:
                continue
            content_mode = getattr(stop.content, "mode", None)
            if content_mode in preferred_modes:
                return stop
            if best is None:
                best = stop
        return best or self._fallback.recommend_next_stop(tour, visitor)
