"""
ui/admin_screen.py

A minimal Admin CMS: lets museum staff build a Tour by adding stops
one at a time through a form, then save it to the offline SQLite
store via OfflineTourStore — the same store the visitor-facing app
reads from. This satisfies the "Admin CMS for tour creation and
content management" deliverable without needing a separate backend
or web server: it's just another screen in the same Kivy app.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView

from patterns.factory import ContentFactory
from models.tour import Tour, TourStop
from services.database import OfflineTourStore
from ui.theme import (
    NAVY, WHITE, TEAL, TEAL_DARK, CRIMSON, add_background, add_background_image,
    flat_button, APP_BACKGROUND_IMAGE, LIGHT_PHOTO_OVERLAY,
)

# Every stop added through the Admin CMS is a simple text stop — the
# "Content extra" field becomes its body copy. Audio/video/image/model
# stops need a real file (a script recording, a video file, an image,
# a 3D model) that a one-line text form can't meaningfully collect, so
# picking a content type here was more confusing than useful; those
# richer stop types are still fully supported, just authored via the
# tour specs in services/demo_data.py rather than this quick-add form.
DEFAULT_CONTENT_TYPE = "text"


def _field_label(text: str) -> Label:
    """A form field label with a color explicitly set — Kivy's Label
    defaults to white text, which disappears against this screen's
    light background if left unset."""
    return Label(text=text, color=NAVY, size_hint_y=None, height=32,
                 halign="left", valign="middle")


def _styled_text_input(**kwargs) -> TextInput:
    return TextInput(
        background_color=WHITE, foreground_color=NAVY,
        cursor_color=NAVY, hint_text_color=(0.5, 0.5, 0.5, 1),
        **kwargs,
    )


class AdminScreen(BoxLayout):
    """Staff-facing tour builder."""

    def __init__(self, on_tour_saved=None, **kwargs):
        # The screen itself is just a header bar + a scrollable body,
        # so the form below can be taller than one screen (e.g. on a
        # small tablet) without any row ever being clipped by the top
        # or bottom edge of the window.
        super().__init__(orientation="vertical", **kwargs)
        add_background_image(self, APP_BACKGROUND_IMAGE, overlay_rgba=LIGHT_PHOTO_OVERLAY)
        self._on_tour_saved = on_tour_saved
        self._pending_stops = []
        self.store = OfflineTourStore()

        # ---- Header bar (fixed, always fully visible) ----
        title_bar = BoxLayout(size_hint_y=None, height=54, padding=(16, 8))
        add_background(title_bar, NAVY)
        title_bar.add_widget(Label(
            text="[b]Admin CMS \u2014 Create a Tour[/b]", markup=True,
            color=WHITE, font_size=18, halign="left", valign="middle",
        ))
        self.add_widget(title_bar)

        # ---- Scrollable form body ----
        scroll = ScrollView()
        self.add_widget(scroll)
        body = BoxLayout(orientation="vertical", size_hint_y=None, padding=16, spacing=10)
        body.bind(minimum_height=body.setter("height"))
        scroll.add_widget(body)

        form = GridLayout(cols=2, size_hint_y=None, spacing=6)
        form.bind(minimum_height=form.setter("height"))

        self.tour_id_input = _styled_text_input(text="T-ADMIN-1", multiline=False)
        self.title_input = _styled_text_input(text="New Tour", multiline=False)
        self.theme_input = _styled_text_input(text="general", multiline=False)

        for label_text, widget in [
            ("Tour ID", self.tour_id_input),
            ("Tour Title", self.title_input),
            ("Theme", self.theme_input),
        ]:
            form.add_widget(_field_label(label_text))
            widget.size_hint_y = None
            widget.height = 32
            form.add_widget(widget)

        body.add_widget(form)

        body.add_widget(Label(text="[b]Add a stop:[/b]", markup=True, color=NAVY,
                               size_hint_y=None, height=24, halign="left", valign="middle"))
        stop_form = GridLayout(cols=2, size_hint_y=None, spacing=6)
        stop_form.bind(minimum_height=stop_form.setter("height"))

        self.stop_name_input = _styled_text_input(text="", hint_text="Stop name", multiline=False,
                                                    size_hint_y=None, height=32)
        self.location_id_input = _styled_text_input(text="", hint_text="Location/beacon ID", multiline=False,
                                                      size_hint_y=None, height=32)
        self.content_title_input = _styled_text_input(text="", hint_text="Content title", multiline=False,
                                                        size_hint_y=None, height=32)
        self.content_extra_input = _styled_text_input(
            text="", hint_text="Description / body text for this stop",
            multiline=False, size_hint_y=None, height=32,
        )

        for label_text, widget in [
            ("Stop name", self.stop_name_input),
            ("Location ID", self.location_id_input),
            ("Content title", self.content_title_input),
            ("Content extra", self.content_extra_input),
        ]:
            stop_form.add_widget(_field_label(label_text))
            stop_form.add_widget(widget)

        body.add_widget(stop_form)

        add_stop_btn = flat_button("Add Stop", TEAL, size_hint_y=None, height=40,
                                    on_release=lambda _b: self._add_stop())
        body.add_widget(add_stop_btn)

        self.stops_label = Label(text="No stops added yet.", color=NAVY, size_hint_y=None,
                                  height=80, halign="left", valign="top")
        self.stops_label.bind(size=lambda inst, _sz: setattr(inst, "text_size", (inst.width, None)))
        stops_panel = BoxLayout(size_hint_y=None, height=100, padding=6)
        add_background(stops_panel, WHITE)
        stops_scroll = ScrollView(size_hint_y=None, height=100)
        stops_scroll.add_widget(self.stops_label)
        stops_panel.add_widget(stops_scroll)
        body.add_widget(stops_panel)

        save_btn = flat_button("Save Tour to Offline Store", TEAL_DARK, size_hint_y=None, height=44,
                                on_release=lambda _b: self._save_tour())
        body.add_widget(save_btn)

        self.status_label = Label(text="", color=NAVY, bold=True, size_hint_y=None,
                                   height=32, halign="left", valign="middle")
        self.status_label.bind(size=lambda inst, _sz: setattr(inst, "text_size", (inst.width, None)))
        body.add_widget(self.status_label)

    def _add_stop(self) -> None:
        name = self.stop_name_input.text.strip()
        location_id = self.location_id_input.text.strip()
        content_title = self.content_title_input.text.strip()
        extra = self.content_extra_input.text.strip()

        if not (name and location_id and content_title):
            self._set_status("Stop name, location ID, and content title are required.", error=True)
            return

        kwargs = {"title": content_title, "body": extra}

        self._pending_stops.append({
            "name": name, "location_id": location_id,
            "content_type": DEFAULT_CONTENT_TYPE, "content_kwargs": kwargs,
            "order": len(self._pending_stops) + 1,
        })
        self._refresh_stops_label()
        self.stop_name_input.text = ""
        self.location_id_input.text = ""
        self.content_title_input.text = ""
        self.content_extra_input.text = ""
        self._set_status(f"Added stop: {name}")

    def _refresh_stops_label(self) -> None:
        if not self._pending_stops:
            self.stops_label.text = "No stops added yet."
            return
        lines = [f"{s['order']}. {s['name']}" for s in self._pending_stops]
        self.stops_label.text = "\n".join(lines)

    def _set_status(self, text: str, error: bool = False) -> None:
        self.status_label.text = text
        self.status_label.color = CRIMSON if error else NAVY

    def _save_tour(self) -> None:
        if not self._pending_stops:
            self._set_status("Add at least one stop before saving.", error=True)
            return

        tour = Tour(
            tour_id=self.tour_id_input.text.strip() or "T-ADMIN-1",
            title=self.title_input.text.strip() or "Untitled Tour",
            theme=self.theme_input.text.strip() or "general",
        )
        for stop_spec in self._pending_stops:
            content = ContentFactory.create_content(stop_spec["content_type"], **stop_spec["content_kwargs"])
            tour.add_stop(TourStop(
                name=stop_spec["name"], location_id=stop_spec["location_id"],
                content=content, order=stop_spec["order"],
            ))

        self.store.save_tour(tour)
        self._set_status(f"Saved '{tour.title}' with {len(tour.stops)} stop(s) to offline store.")
        if self._on_tour_saved:
            self._on_tour_saved(tour)
