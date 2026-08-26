"""
services/analytics.py

Visitor analytics requirement: dwell time per stop, most popular
stops across all visitors, and route analysis (the order a visitor
actually took vs. what a recommendation Strategy would have suggested).

Visit events are persisted to their own SQLite table (via SQLAlchemy)
so that "popular stops" can be computed across every visitor who has
ever used the app, not just the one currently in memory.
"""

from collections import Counter
from datetime import datetime
from typing import List, Dict

from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

AnalyticsBase = declarative_base()


class VisitLogRecord(AnalyticsBase):
    __tablename__ = "visit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    visitor_id = Column(String, nullable=False)
    tour_id = Column(String, nullable=False)
    location_id = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)


class AnalyticsService:
    def __init__(self, db_path: str = "museum_tours.db"):
        self.engine = create_engine(f"sqlite:///{db_path}")
        AnalyticsBase.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def log_visit(self, visitor_id: str, tour_id: str, location_id: str, timestamp: datetime = None) -> None:
        session = self.Session()
        try:
            session.add(VisitLogRecord(
                visitor_id=visitor_id, tour_id=tour_id, location_id=location_id,
                timestamp=timestamp or datetime.utcnow(),
            ))
            session.commit()
        finally:
            session.close()

    def dwell_times(self, visitor_id: str) -> Dict[str, float]:
        """
        Approximate seconds spent at each stop, computed as the time
        between consecutive visit-log entries for this visitor. The
        final stop has no "next" entry to measure against, so it is
        left out of the result.
        """
        session = self.Session()
        try:
            rows = (
                session.query(VisitLogRecord)
                .filter_by(visitor_id=visitor_id)
                .order_by(VisitLogRecord.timestamp)
                .all()
            )
        finally:
            session.close()

        dwell = {}
        for current, nxt in zip(rows, rows[1:]):
            seconds = (nxt.timestamp - current.timestamp).total_seconds()
            dwell.setdefault(current.location_id, 0.0)
            dwell[current.location_id] += max(seconds, 0.0)
        return dwell

    def popular_stops(self, tour_id: str, top_n: int = 5) -> List[tuple]:
        """Most-visited location_ids for a tour, across all visitors, most popular first."""
        session = self.Session()
        try:
            rows = session.query(VisitLogRecord).filter_by(tour_id=tour_id).all()
        finally:
            session.close()
        counts = Counter(row.location_id for row in rows)
        return counts.most_common(top_n)

    def visitor_route(self, visitor_id: str) -> List[str]:
        """The actual sequence of locations a visitor moved through, in order."""
        session = self.Session()
        try:
            rows = (
                session.query(VisitLogRecord)
                .filter_by(visitor_id=visitor_id)
                .order_by(VisitLogRecord.timestamp)
                .all()
            )
        finally:
            session.close()
        return [row.location_id for row in rows]

    def compare_route_to_recommendation(self, visitor, tour, strategy) -> Dict[str, list]:
        """
        Compares the visitor's actual route (from the log) against what
        the given Strategy would have recommended at each step: for
        each stop the visitor actually visited, what would the
        strategy have suggested given only what they'd seen so far?
        """
        actual_route = self.visitor_route(visitor.visitor_id)
        recommended_route = []
        visited_so_far: List[str] = []

        for actual_location in actual_route:
            snapshot = _VisitedSnapshot(visited_so_far, visitor.preferences)
            suggestion = strategy.recommend_next_stop(tour, snapshot)
            recommended_route.append(suggestion.location_id if suggestion else None)
            visited_so_far.append(actual_location)

        return {"actual": actual_route, "recommended": recommended_route}


class _VisitedSnapshot:
    """
    A minimal stand-in for a Visitor, exposing just enough of the
    interface (visited_locations, preferences) that a
    RecommendationStrategy needs — used to ask "what would you have
    recommended at this earlier point in the tour?" without mutating
    the real Visitor object.
    """

    def __init__(self, visited: List[str], preferences):
        self._visited = visited
        self.preferences = preferences

    @property
    def visited_locations(self) -> List[str]:
        return list(self._visited)
