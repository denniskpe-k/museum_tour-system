"""
ui/map_widget.py

An interactive floor-plan map for the Kivy UI.

There is no real architectural floor-plan blueprint for this project,
so the background is a generated floor-plan-style image (rooms and
hallways, via services/floorplan_generator.py) rather than blank space
— it's still not a real museum's blueprint, but it reads as a floor
plan instead of an abstract grid of dots.

Each tour stop is plotted at a fixed (x, y) percentage position (see
services/demo_data.FLOOR_PLAN_POSITIONS). The visitor's path is drawn
as a continuous solid line connecting every stop visited so far, in
order, starting from a default starting position — so the map shows
progress accumulating rather than a single marker jumping from stop to
stop. The current stop is highlighted, and a dashed line points to
whichever stop the active RecommendationStrategy suggests next.
"""

import os

from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.uix.label import Label
from kivy.core.image import Image as CoreImage


class MapWidget(Widget):
    """
    Draws the floor plan. Call refresh(tour, positions, visited_location_ids,
    current_location_id, recommended_location_id) whenever the visitor's
    position, path, or recommendation changes.
    """

    def __init__(self, floor_plan_image_path: str = None, **kwargs):
        super().__init__(**kwargs)
        self._labels = []
        self._floor_plan_texture = None
        if floor_plan_image_path and os.path.exists(floor_plan_image_path):
            try:
                self._floor_plan_texture = CoreImage(floor_plan_image_path).texture
            except Exception:
                self._floor_plan_texture = None
        self.bind(pos=self._redraw_placeholder, size=self._redraw_placeholder)
        self._last_state = None

    def _redraw_placeholder(self, *args):
        if self._last_state is not None:
            self.refresh(*self._last_state)

    def refresh(self, tour, positions: dict, visited_location_ids=None,
                current_location_id=None, recommended_location_id=None):
        visited_location_ids = visited_location_ids or (
            [current_location_id] if current_location_id else []
        )
        self._last_state = (tour, positions, visited_location_ids, current_location_id, recommended_location_id)

        # Remove the old stop-name Label widgets FIRST. remove_widget()
        # detaches each label's own canvas from self.canvas cleanly.
        # (Previously canvas.clear() ran first, which wipes the whole
        # canvas tree — including those already-merged-in child label
        # canvases — leaving them in a corrupted, invisible state on
        # every refresh after the first. Only clear our own directly
        # drawn instructions once the children are safely detached.)
        for label in self._labels:
            self.remove_widget(label)
        self._labels = []
        self.canvas.clear()

        with self.canvas:
            # Floor-plan background image, or a plain outline if none loaded.
            if self._floor_plan_texture is not None:
                Color(1, 1, 1, 1)
                Rectangle(texture=self._floor_plan_texture, pos=(self.x, self.y), size=(self.width, self.height))
            else:
                Color(0.85, 0.85, 0.9, 1)
                Line(rectangle=(self.x, self.y, self.width, self.height), width=1.5)

            points_by_location = {}
            for stop in tour.stops:
                if stop.location_id not in positions:
                    continue
                px, py = positions[stop.location_id]
                x = self.x + (px / 100.0) * self.width
                y = self.y + (py / 100.0) * self.height
                points_by_location[stop.location_id] = (x, y)

            # Continuous solid path connecting every stop visited so far,
            # in order — this is what makes the map "continue" from a
            # default starting position instead of just jumping between
            # single points.
            trail_points = [
                points_by_location[loc] for loc in visited_location_ids
                if loc in points_by_location
            ]
            if len(trail_points) >= 2:
                Color(0.15, 0.55, 0.4, 0.85)
                flat_points = [coord for point in trail_points for coord in point]
                Line(points=flat_points, width=3, joint="round")

            # Dashed wayfinding line to the recommended next stop.
            if (
                recommended_location_id
                and current_location_id
                and current_location_id in points_by_location
                and recommended_location_id in points_by_location
            ):
                Color(0.2, 0.6, 1.0, 0.9)
                x1, y1 = points_by_location[current_location_id]
                x2, y2 = points_by_location[recommended_location_id]
                Line(points=[x1, y1, x2, y2], width=2, dash_length=8, dash_offset=4)

            # Stop markers: visited stops filled navy, current stop larger
            # and highlighted, unvisited stops a lighter outline.
            visited_set = set(visited_location_ids)
            for stop in tour.stops:
                if stop.location_id not in points_by_location:
                    continue
                x, y = points_by_location[stop.location_id]
                is_current = stop.location_id == current_location_id
                is_visited = stop.location_id in visited_set
                radius = 13 if is_current else 8
                if is_current:
                    Color(0.95, 0.55, 0.15, 1)
                elif is_visited:
                    Color(0.15, 0.35, 0.55, 1)
                else:
                    Color(0.65, 0.65, 0.7, 0.9)
                Ellipse(pos=(x - radius, y - radius), size=(radius * 2, radius * 2))

        for stop in tour.stops:
            if stop.location_id not in points_by_location:
                continue
            x, y = points_by_location[stop.location_id]
            label = Label(
                text=stop.name, font_size=11, size_hint=(None, None),
                size=(120, 20), pos=(x - 60, y - 28), color=(0.1, 0.1, 0.15, 1),
                bold=stop.location_id == current_location_id,
            )
            self.add_widget(label)
            self._labels.append(label)
