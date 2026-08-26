"""
ui/gallery_widget.py

Two small popups opened from the visitor screen:
  - open_comments_popup: every comment left on this tour so far
    (persisted via OfflineTourStore, so it survives a restart).
  - open_photos_popup: every photo this visitor has taken this
    session, newest first.

Both use the real museum gallery photo (assets/images/gallery_hall_bg.jpg)
as a dimmed background so they feel like part of the museum rather than
a bare system dialog.
"""

import os

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

from ui.theme import (
    NAVY, WHITE, CRIMSON, add_background, add_background_image, flat_button,
    APP_BACKGROUND_IMAGE, DARK_PHOTO_OVERLAY,
)
from services.i18n import tr

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GALLERY_BG = APP_BACKGROUND_IMAGE


def _popup_root() -> BoxLayout:
    root = BoxLayout(orientation="vertical", spacing=8, padding=10)
    add_background_image(root, GALLERY_BG, overlay_rgba=DARK_PHOTO_OVERLAY)
    return root


def open_comments_popup(comments, lang: str) -> None:
    """comments: list of models.social.Comment, any order."""
    root = _popup_root()

    scroll = ScrollView()
    list_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=8, padding=4)
    list_box.bind(minimum_height=list_box.setter("height"))

    ordered = sorted(comments, key=lambda c: c.posted_at)
    if not ordered:
        list_box.add_widget(Label(text=tr("no_comments", lang), color=WHITE,
                                   size_hint_y=None, height=40))
    else:
        for comment in reversed(ordered):
            card = BoxLayout(orientation="vertical", size_hint_y=None, padding=8, spacing=2)
            add_background(card, WHITE)
            when = comment.posted_at.strftime("%b %d, %H:%M")
            header = Label(
                text=f"[b]{comment.location_id}[/b]  \u00b7  {when}", markup=True,
                color=NAVY, size_hint_y=None, height=22, halign="left", valign="middle",
                font_size=12,
            )
            header.bind(size=lambda inst, _sz: setattr(inst, "text_size", (inst.width, None)))
            body = Label(
                text=comment.text, color=NAVY, size_hint_y=None,
                halign="left", valign="top",
            )
            body.bind(width=lambda inst, w: setattr(inst, "text_size", (w, None)))
            body.bind(texture_size=lambda inst, ts: setattr(inst, "height", ts[1]))
            card.add_widget(header)
            card.add_widget(body)
            card.bind(minimum_height=card.setter("height"))
            list_box.add_widget(card)

    scroll.add_widget(list_box)
    root.add_widget(scroll)

    close_btn = flat_button(tr("close", lang), CRIMSON, size_hint_y=None, height=48)
    root.add_widget(close_btn)

    popup = Popup(title=tr("comments_title", lang), content=root, size_hint=(0.92, 0.85))
    close_btn.bind(on_release=lambda _b: popup.dismiss())
    popup.open()


def open_photos_popup(photos, lang: str) -> None:
    """photos: list of models.social.Photo, any order."""
    root = _popup_root()

    scroll = ScrollView()
    grid = GridLayout(cols=2, size_hint_y=None, spacing=8, padding=4)
    grid.bind(minimum_height=grid.setter("height"))

    ordered = list(reversed(photos))
    if not ordered:
        grid.cols = 1
        grid.add_widget(Label(text=tr("no_photos_taken", lang), color=WHITE,
                               size_hint_y=None, height=40))
    else:
        for photo in ordered:
            cell = BoxLayout(orientation="vertical", size_hint_y=None, height=200, padding=4, spacing=4)
            add_background(cell, WHITE)
            path = photo.image_path if os.path.isabs(photo.image_path) else os.path.join(PROJECT_ROOT, photo.image_path)
            if os.path.exists(path):
                cell.add_widget(Image(source=path, allow_stretch=True, keep_ratio=True))
            else:
                cell.add_widget(Label(text=tr("no_photos_taken", lang), color=NAVY))
            caption = Label(
                text=photo.exhibit_title, color=NAVY, size_hint_y=None, height=22,
                font_size=12, shorten=True,
            )
            cell.add_widget(caption)
            grid.add_widget(cell)

    scroll.add_widget(grid)
    root.add_widget(scroll)

    close_btn = flat_button(tr("close", lang), CRIMSON, size_hint_y=None, height=48)
    root.add_widget(close_btn)

    popup = Popup(title=tr("photos_title", lang), content=root, size_hint=(0.92, 0.85))
    close_btn.bind(on_release=lambda _b: popup.dismiss())
    popup.open()
