"""
ui/model3d_widget.py

A real, interactive 3D viewer, implemented as a procedurally generated
wireframe (e.g. a vase-shaped surface of revolution) rendered with
genuine 3D rotation and projection math, drawn using Kivy's ordinary
2D line-drawing primitives.

This deliberately avoids Kivy's OpenGL 3D mesh APIs and any external
3D file format loader — those add real fragility (extra native
dependencies, GPU driver quirks) for a feature whose actual content
here is a generated shape, not a real artifact scan. The result is a
model the visitor can genuinely drag to rotate, auto-rotates when left
alone, and needs nothing beyond base Kivy to work on any machine.
"""

import math

from kivy.uix.widget import Widget
from kivy.graphics import Color, Line
from kivy.clock import Clock

from services.model3d_geometry import build_rings, project_point, SHAPE_PROFILES, VASE_PROFILE


class Model3DWidget(Widget):
    """
    Renders a rotating wireframe shape. Call set_shape(name) to choose
    which procedural shape to display (see SHAPE_PROFILES). Drag with
    the mouse/finger to rotate manually; it auto-rotates slowly when
    not being dragged.
    """

    def __init__(self, shape: str = "vase", segments: int = 20, **kwargs):
        super().__init__(**kwargs)
        self.segments = segments
        self._rings = build_rings(SHAPE_PROFILES.get(shape, VASE_PROFILE), segments)
        self._angle_y = 0.4  # radians, current rotation around vertical axis
        self._angle_x = 0.15  # slight tilt for a more three-dimensional look
        self._auto_rotate = True
        self._drag_last = None

        self.bind(pos=self._redraw, size=self._redraw)
        self._clock_event = Clock.schedule_interval(self._tick, 1 / 30.0)

    def set_shape(self, shape: str) -> None:
        self._rings = build_rings(SHAPE_PROFILES.get(shape, VASE_PROFILE), self.segments)
        self._redraw()

    def stop(self) -> None:
        if self._clock_event is not None:
            self._clock_event.cancel()
            self._clock_event = None

    # -- Interaction ------------------------------------------------

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._auto_rotate = False
            self._drag_last = touch.pos
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._drag_last is not None and self.collide_point(*touch.pos):
            dx = touch.pos[0] - self._drag_last[0]
            dy = touch.pos[1] - self._drag_last[1]
            self._angle_y += dx * 0.01
            self._angle_x = max(-1.2, min(1.2, self._angle_x - dy * 0.01))
            self._drag_last = touch.pos
            self._redraw()
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        self._drag_last = None
        self._auto_rotate = True
        return super().on_touch_up(touch)

    # -- Animation / drawing ------------------------------------------

    def _tick(self, dt):
        if self._auto_rotate:
            self._angle_y += dt * 0.5
        self._redraw()

    def _project(self, point):
        return project_point(
            point, self._angle_y, self._angle_x,
            self.center_x, self.y, self.width, self.height,
        )

    def _redraw(self, *args):
        if self.width <= 0 or self.height <= 0:
            return
        self.canvas.clear()
        with self.canvas:
            Color(0.93, 0.93, 0.95, 1)
            projected_rings = [[self._project(p) for p in ring] for ring in self._rings]

            # Horizontal rings.
            for ring in projected_rings:
                depth_avg = sum(p[2] for p in ring) / len(ring)
                shade = max(0.25, min(0.85, 0.55 - depth_avg * 0.15))
                Color(0.15 + shade * 0.1, 0.35 + shade * 0.2, 0.5 + shade * 0.2, 1)
                points = []
                for x, y, _ in ring:
                    points.extend([x, y])
                points.extend([ring[0][0], ring[0][1]])
                Line(points=points, width=1.3)

            # A handful of vertical "rib" lines connecting corresponding
            # points across every ring, for a genuine 3D wireframe look.
            rib_step = max(1, self.segments // 8)
            Color(0.55, 0.4, 0.15, 1)
            for i in range(0, self.segments, rib_step):
                points = []
                for ring in projected_rings:
                    x, y, _ = ring[i]
                    points.extend([x, y])
                Line(points=points, width=1.1)
