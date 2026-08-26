"""
services/location_simulator.py

Simulates indoor beacon proximity signals and outdoor GPS coordinates
so the whole system is demonstrable without owning any real hardware
(zero-budget constraint). A real deployment would swap this module for
actual Bluetooth beacon scanning / a GPS receiver, without touching
any other file, because everything else only talks to the
TourMediator's handle_beacon_signal / handle_gps_signal methods.
"""

import random
import time
from typing import List


class BeaconSimulator:
    """
    Pretends to be a set of Bluetooth beacons placed around the
    museum. Each beacon has a fixed location_id. Calling walk_route()
    fires a signal for each location in turn, as if the visitor
    physically walked past each beacon.
    """

    def __init__(self, mediator, delay_seconds: float = 0.0):
        self.mediator = mediator
        self.delay_seconds = delay_seconds

    def walk_route(self, visitor_id: str, location_ids: List[str]) -> None:
        for location_id in location_ids:
            self.mediator.handle_beacon_signal(visitor_id, location_id)
            if self.delay_seconds:
                time.sleep(self.delay_seconds)

    def fire_signal(self, visitor_id: str, location_id: str) -> None:
        self.mediator.handle_beacon_signal(visitor_id, location_id)


class GPSSimulator:
    """
    Pretends to be a GPS receiver for outdoor courtyards / sculpture
    gardens where beacons don't make sense. Generates a random walk of
    (lat, lon) coordinates and resolves them to the nearest known
    location_id from a lookup table.
    """

    def __init__(self, mediator, known_points: dict):
        """
        known_points: {location_id: (lat, lon)}
        """
        self.mediator = mediator
        self.known_points = known_points

    def _nearest_location(self, lat: float, lon: float) -> str:
        def dist(point):
            plat, plon = point[1]
            return (plat - lat) ** 2 + (plon - lon) ** 2

        nearest = min(self.known_points.items(), key=dist)
        return nearest[0]

    def emit_random_position(self, visitor_id: str) -> None:
        base_lat, base_lon = next(iter(self.known_points.values()))
        lat = base_lat + random.uniform(-0.0005, 0.0005)
        lon = base_lon + random.uniform(-0.0005, 0.0005)
        location_id = self._nearest_location(lat, lon)
        self.mediator.handle_gps_signal(visitor_id, location_id)
