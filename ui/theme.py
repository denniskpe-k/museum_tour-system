"""
ui/theme.py

Shared color palette and small Kivy widget helpers used across every
screen and popup, so app.py and media_widget.py (and anything else)
can share one consistent look without importing from each other.
"""

import os

from kivy.graphics import Color, Rectangle
from kivy.uix.button import Button
from kivy.core.image import Image as CoreImage

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_BACKGROUND_IMAGE = os.path.join(PROJECT_ROOT, "assets", "images", "gallery_hall_bg.jpg")

# ---- Color theme -----------------------------------------------------
NAVY = (0.10, 0.16, 0.30, 1)
GOLD = (0.85, 0.65, 0.13, 1)
CREAM = (0.97, 0.95, 0.90, 1)
TEAL = (0.11, 0.45, 0.45, 1)
TEAL_DARK = (0.08, 0.35, 0.35, 1)
PLUM = (0.42, 0.20, 0.45, 1)
CRIMSON = (0.55, 0.16, 0.16, 1)
WHITE = (1, 1, 1, 1)

# Overlay washes for add_background_image(): LIGHT keeps this app's
# dark-navy-text-on-light-background scheme intact on main screens
# (the photo shows through only faintly); DARK suits a popup whose
# content already sits on its own solid white cards.
LIGHT_PHOTO_OVERLAY = (*CREAM[:3], 0.85)
DARK_PHOTO_OVERLAY = (0, 0, 0, 0.55)


def add_background(widget, rgba):
    with widget.canvas.before:
        Color(*rgba)
        rect = Rectangle(pos=widget.pos, size=widget.size)

    def _update(instance, _value):
        rect.pos = instance.pos
        rect.size = instance.size

    widget.bind(pos=_update, size=_update)


def add_background_image(widget, image_path, overlay_rgba=None):
    """Paints `image_path` stretched to cover `widget`, behind its
    other children. `overlay_rgba` (an (r, g, b, a) tuple) layers a
    translucent wash on top of the photo so existing text/button
    colors stay readable against a busy background image — e.g. a
    light, mostly-opaque CREAM wash keeps this app's dark-navy-text-
    on-light-background scheme intact almost everywhere, while a
    darker wash suits a popup whose content already sits on its own
    solid white cards. None (default) leaves the photo untouched.
    Falls back silently to no background if the image can't be loaded
    (e.g. a bad path), so a missing asset never crashes the screen.
    """
    try:
        texture = CoreImage(image_path).texture
    except Exception:
        return
    with widget.canvas.before:
        Color(1, 1, 1, 1)
        rect = Rectangle(pos=widget.pos, size=widget.size, texture=texture)
        if overlay_rgba is not None:
            Color(*overlay_rgba)
            shade = Rectangle(pos=widget.pos, size=widget.size)

    def _update(instance, _value):
        rect.pos = instance.pos
        rect.size = instance.size
        if overlay_rgba is not None:
            shade.pos = instance.pos
            shade.size = instance.size

    widget.bind(pos=_update, size=_update)


def flat_button(text, rgba, **kwargs):
    btn = Button(
        text=text, background_normal="", background_color=rgba,
        color=WHITE, bold=True, **kwargs,
    )
    return btn
