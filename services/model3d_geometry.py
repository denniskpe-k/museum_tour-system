"""
services/model3d_geometry.py

Pure-Python 3D geometry for the procedural wireframe shapes used by
ui/model3d_widget.py. Kept separate from that file (and free of any
Kivy import) so the geometry itself — and the pytest suite that
exercises it — never needs Kivy installed, matching the rest of this
project's services/ layer.
"""

import math

# Profile of a generic vase: (radius, height) pairs from base to rim,
# in arbitrary "model units". This is what makes the shape read as a
# vase once lathed around the Y axis, rather than a generic blob.
VASE_PROFILE = [
    (0.35, 0.00), (0.55, 0.05), (0.62, 0.15), (0.58, 0.30),
    (0.68, 0.45), (0.72, 0.55), (0.60, 0.68), (0.40, 0.80),
    (0.34, 0.88), (0.42, 0.95), (0.46, 1.00),
]

SHAPE_PROFILES = {
    "vase": VASE_PROFILE,
}


def build_rings(profile, segments: int = 20):
    """Lathes a 2D (radius, height) profile around the Y axis into 3D ring points."""
    rings = []
    for radius, y in profile:
        ring = []
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            ring.append((x, y, z))
        rings.append(ring)
    return rings


def project_point(point, angle_y: float, angle_x: float, center_x: float, base_y: float,
                   width: float, height: float, focal: float = 3.2):
    """
    Rotates a 3D point around the Y then X axis and projects it to 2D
    screen coordinates using simple perspective projection. Pure
    function so both the widget and tests can exercise the same math.
    Returns (screen_x, screen_y, depth_z).
    """
    x, y, z = point
    cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)
    x1 = x * cos_y - z * sin_y
    z1 = x * sin_y + z * cos_y
    cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
    y1 = y * cos_x - z1 * sin_x
    z2 = y * sin_x + z1 * cos_x

    depth = focal + z2
    scale = min(width, height) * 0.8
    screen_x = center_x + (x1 * focal / depth) * scale
    screen_y = base_y + 20 + ((y1 + 0.1) * focal / depth) * scale * 0.9
    return screen_x, screen_y, z2
