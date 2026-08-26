"""
services/video_generator.py

Generates a real, playable "video" as a sequence of animated frames
(a slow pan/zoom over a source image, with captions) rather than a
claim of pre-recorded museum footage, since no real video crew or
footage exists for this project.

Frames are cycled by ui/video_widget.py using Kivy's Image widget and
a Clock timer, rather than relying on Kivy's optional Video widget
(which needs an extra codec backend like gstreamer or ffpyplayer that
may not install cleanly on every machine) — this guarantees the
"video" plays using only the base Kivy install already required.
"""

import os

FRAMES_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "video_frames"
)


def generate_cubism_style_artwork(path: str, width: int = 640, height: int = 480) -> str:
    """
    Generates an illustrative abstract geometric image in a cubism-
    inspired style, since no real photograph of a cubist artwork is
    available. This is clearly a generated stand-in, not a claim of a
    real painting.
    """
    if os.path.exists(path):
        return path

    import random
    from PIL import Image, ImageDraw

    random.seed(42)  # deterministic output between runs
    palette = [
        (196, 92, 68), (222, 165, 85), (94, 116, 140), (61, 79, 94),
        (216, 196, 150), (139, 62, 60), (74, 98, 84),
    ]
    img = Image.new("RGB", (width, height), (232, 224, 208))
    draw = ImageDraw.Draw(img, "RGBA")

    for _ in range(22):
        color = random.choice(palette) + (200,)
        cx, cy = random.randint(0, width), random.randint(0, height)
        size = random.randint(60, 220)
        points = []
        num_sides = random.choice([3, 4, 5])
        for i in range(num_sides):
            angle = (2 * 3.14159 * i / num_sides) + random.uniform(-0.4, 0.4)
            r = size * random.uniform(0.6, 1.0)
            points.append((cx + r * _cos(angle), cy + r * _sin(angle)))
        draw.polygon(points, fill=color)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    return path


def _cos(angle):
    import math
    return math.cos(angle)


def _sin(angle):
    import math
    return math.sin(angle)


def generate_video_frames(source_image_path: str, stop_key: str, caption: str = "",
                           num_frames: int = 20, out_size=(640, 480)) -> tuple:
    """
    Generates a Ken Burns-style pan/zoom animation: `num_frames` PNG
    frames, each a slightly different crop of the source image, zooming
    in slowly over the sequence, with the caption burned into the
    bottom of each frame. Returns (frames_dir, frame_count). Cached —
    regenerates only if the frame directory doesn't already exist.
    """
    frames_dir = os.path.join(FRAMES_ROOT, stop_key)
    if os.path.isdir(frames_dir) and len(os.listdir(frames_dir)) >= num_frames:
        return frames_dir, num_frames

    from PIL import Image, ImageDraw, ImageFont

    os.makedirs(frames_dir, exist_ok=True)
    source = Image.open(source_image_path).convert("RGB")
    sw, sh = source.size

    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    for i in range(num_frames):
        progress = i / max(num_frames - 1, 1)
        # Zoom from showing 100% of the image down to ~72%, panning
        # slightly toward the center-right as it zooms, for a simple
        # but genuine motion effect.
        zoom = 1.0 - 0.28 * progress
        crop_w, crop_h = int(sw * zoom), int(sh * zoom)
        max_x = sw - crop_w
        max_y = sh - crop_h
        x0 = int(max_x * (0.3 + 0.4 * progress))
        y0 = int(max_y * 0.3)
        cropped = source.crop((x0, y0, x0 + crop_w, y0 + crop_h)).resize(out_size)

        frame = cropped.copy()
        draw = ImageDraw.Draw(frame, "RGBA")
        if caption:
            bar_h = 46
            draw.rectangle([0, out_size[1] - bar_h, out_size[0], out_size[1]], fill=(10, 15, 25, 190))
            draw.text((14, out_size[1] - bar_h + 14), caption, fill=(255, 255, 255, 255), font=font)

        frame.save(os.path.join(frames_dir, f"frame_{i:03d}.png"))

    return frames_dir, num_frames
