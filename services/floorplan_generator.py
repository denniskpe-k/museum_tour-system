"""
services/floorplan_generator.py

Generates a stylized museum floor-plan background image with PIL. This
project has no real architectural blueprint to work from, so rather
than leaving the map as bare dots on white space, this draws plausible
gallery "rooms" and connecting hallways, laid out around the same
FLOOR_PLAN_POSITIONS coordinates the stop markers use — so the rooms
visually line up with the stops that belong in them.

This is generated once and cached to disk; MapWidget loads the PNG as
a background and draws stop markers/wayfinding lines on top of it.
"""

import os

FLOORPLAN_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "floorplans"
)


def generate_floor_plan(positions: dict, room_labels: dict, width: int = 900, height: int = 620,
                         filename: str = "museum_floor_plan.png") -> str:
    """
    Draws a floor plan PNG sized `width` x `height`, with a room drawn
    around each (x, y) percentage position in `positions`, labeled
    using `room_labels` (location_id -> room name). Returns the path
    to the generated file; regenerates only if missing.
    """
    os.makedirs(FLOORPLAN_DIR, exist_ok=True)
    path = os.path.join(FLOORPLAN_DIR, filename)
    if os.path.exists(path):
        return path

    from PIL import Image, ImageDraw, ImageFont

    bg = (250, 248, 242)
    wall = (60, 70, 90)
    room_fill = (225, 232, 240)
    hall_fill = (238, 233, 220)
    text_color = (40, 48, 64)

    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)

    # Outer building outline.
    margin = 20
    draw.rectangle([margin, margin, width - margin, height - margin], outline=wall, width=4, fill=hall_fill)

    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    room_w, room_h = 130, 95
    for location_id, (px, py) in positions.items():
        cx = margin + (px / 100.0) * (width - 2 * margin)
        cy = height - (margin + (py / 100.0) * (height - 2 * margin))  # flip Y for image coords
        x0, y0 = cx - room_w / 2, cy - room_h / 2
        x1, y1 = cx + room_w / 2, cy + room_h / 2
        draw.rectangle([x0, y0, x1, y1], outline=wall, width=3, fill=room_fill)
        label = room_labels.get(location_id, location_id)
        draw.text((x0 + 10, y0 + 8), label, fill=text_color, font=font)

    img.save(path)
    return path
