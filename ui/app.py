"""
ui/app.py

Kivy tablet UI for the Museum Guided Tour System.

Screens (managed by a ScreenManager, switched via the top toggle bar
or in-screen buttons):
  - "select"       — Tour Selection: pick a tour and a language before
                      starting.
  - "visitor"       — the guided tour experience: interactive floor-plan
                      map with a continuous visited-path trail, stop
                      buttons, a "Take Quiz" button, photo capture,
                      comments, a Share button, and a language toggle.
  - "admin_login"    — a PIN gate in front of the Admin CMS.
  - "admin"           — the Admin CMS (see ui/admin_screen.py) for staff
                      to build new tours.

All of the business logic this file calls into (models/, patterns/,
services/) works completely independently of Kivy, which is why the
pytest suite does not need Kivy installed to pass.
"""

import os
import subprocess
import tempfile
import webbrowser
from urllib.parse import quote

from kivy.app import App
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
from kivy.utils import platform as kivy_platform
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.image import Image

from patterns.factory import TourFactory, VisitorFactory
from patterns.mediator import TourMediator
from patterns.observer import ContentTriggerObserver, BadgeObserver, AnalyticsObserver, QuizObserver
from patterns.strategy import PersonalizedStrategy
from services.location_simulator import BeaconSimulator
from services.database import OfflineTourStore
from services.analytics import AnalyticsService
from services.camera_service import CameraService
from services.admin_auth import AdminAuthService
from services.floorplan_generator import generate_floor_plan
from services.demo_data import (
    TREASURES_TOUR_SPEC, ALL_QUIZZES, FLOOR_PLAN_POSITIONS, FLOOR_PLAN_ROOM_LABELS,
    BUILTIN_TOURS, available_tour_summaries,
)
from services.i18n import tr
from models.social import Comment, build_share_text

try:
    from plyer import email as plyer_email  # optional; degrades gracefully if unavailable
except Exception:
    plyer_email = None
from models.content import ModelGuide
from ui.map_widget import MapWidget
from ui.admin_screen import AdminScreen
from ui.video_widget import VideoPlayerWidget
from ui.model3d_widget import Model3DWidget
from ui.media_widget import open_media_popup
from ui.gallery_widget import open_comments_popup, open_photos_popup

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from ui.theme import (
    NAVY, GOLD, CREAM, TEAL, TEAL_DARK, PLUM, CRIMSON, WHITE,
    add_background, add_background_image, flat_button, APP_BACKGROUND_IMAGE,
    LIGHT_PHOTO_OVERLAY,
)

Window.clearcolor = CREAM


def tour_floor_plan_path(tour) -> str:
    """Generate (or reuse the cached) floor-plan image for this specific
    tour's stops only, so rooms never overlap across tours."""
    stop_ids = [s.location_id for s in tour.stops]
    positions = {k: v for k, v in FLOOR_PLAN_POSITIONS.items() if k in stop_ids}
    labels = {k: v for k, v in FLOOR_PLAN_ROOM_LABELS.items() if k in stop_ids}
    return generate_floor_plan(positions, labels, filename=f"{tour.tour_id}.png")


# ============================================================
# Tour Selection Screen
# ============================================================

class TourSelectScreen(Screen):
    """Lets the visitor pick a tour and a language before starting."""

    def __init__(self, on_start_tour, **kwargs):
        super().__init__(**kwargs)
        self._on_start_tour = on_start_tour
        self._selected_language = "en"
        self.store = OfflineTourStore()

        root = BoxLayout(orientation="vertical", padding=16, spacing=12)
        add_background_image(root, APP_BACKGROUND_IMAGE, overlay_rgba=LIGHT_PHOTO_OVERLAY)
        self.add_widget(root)

        title_bar = BoxLayout(size_hint_y=None, height=54, padding=(12, 8))
        add_background(title_bar, NAVY)
        self.title_label = Label(text=f"[b]{tr('choose_a_tour', self._selected_language)}[/b]",
                                  markup=True, color=WHITE, font_size=20)
        title_bar.add_widget(self.title_label)
        root.add_widget(title_bar)

        lang_row = BoxLayout(size_hint_y=None, height=44, spacing=8)
        self.lang_label = Label(text=tr("language_label", self._selected_language), color=NAVY,
                                 bold=True, size_hint_x=None, width=90)
        lang_row.add_widget(self.lang_label)
        self.en_btn = flat_button("English", TEAL, size_hint_x=None, width=140,
                                   on_release=lambda _b: self._set_language("en"))
        self.fr_btn = flat_button("Français", GOLD, size_hint_x=None, width=140,
                                   on_release=lambda _b: self._set_language("fr"))
        lang_row.add_widget(self.en_btn)
        lang_row.add_widget(self.fr_btn)
        lang_row.add_widget(Widget())  # spacer so the buttons don't stretch to fill the row
        root.add_widget(lang_row)
        self._update_language_buttons()

        scroll = ScrollView()
        tour_list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=10)
        tour_list.bind(minimum_height=tour_list.setter("height"))

        self._tour_cards = []  # (subtitle_label, start_btn, theme, stop_count)
        for tour_id, title, theme, stop_count in available_tour_summaries(self.store):
            card = BoxLayout(orientation="vertical", size_hint_y=None, padding=10, spacing=6)
            card.bind(minimum_height=card.setter("height"))
            add_background(card, WHITE)
            title_label = Label(
                text=f"[b]{title}[/b]", markup=True, color=NAVY, size_hint_y=None,
                height=30, halign="left", valign="middle", shorten=False,
            )
            title_label.bind(size=lambda inst, _sz: setattr(inst, "text_size", (inst.width, None)))
            card.add_widget(title_label)
            subtitle = Label(text=f"{theme}  \u00b7  {stop_count} {tr('stops_suffix', self._selected_language)}",
                              color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=22)
            card.add_widget(subtitle)
            start_btn = flat_button(
                tr("start_tour", self._selected_language), TEAL_DARK, size_hint_y=None, height=40,
                on_release=lambda _b, tid=tour_id: self._start(tid),
            )
            card.add_widget(start_btn)
            tour_list.add_widget(card)
            self._tour_cards.append((subtitle, start_btn, theme, stop_count))

        scroll.add_widget(tour_list)
        root.add_widget(scroll)

    def _set_language(self, lang: str) -> None:
        self._selected_language = lang
        self._update_language_buttons()
        self.title_label.text = f"[b]{tr('choose_a_tour', lang)}[/b]"
        self.lang_label.text = tr("language_label", lang)
        for subtitle, start_btn, theme, stop_count in self._tour_cards:
            subtitle.text = f"{theme}  \u00b7  {stop_count} {tr('stops_suffix', lang)}"
            start_btn.text = tr("start_tour", lang)

    def _update_language_buttons(self) -> None:
        self.en_btn.background_color = TEAL if self._selected_language == "en" else (0.7, 0.7, 0.7, 1)
        self.fr_btn.background_color = GOLD if self._selected_language == "fr" else (0.7, 0.7, 0.7, 1)

    def _start(self, tour_id: str) -> None:
        tour_spec = BUILTIN_TOURS.get(tour_id)
        if tour_spec is not None:
            tour = TourFactory.create_tour(tour_spec)
        else:
            tour = self.store.load_tour(tour_id)  # a tour created via Admin CMS
        self._on_start_tour(tour, self._selected_language)


# ============================================================
# Visitor Screen
# ============================================================

class TourVisitorScreen(Screen):
    """Visitor-facing screen for one specific tour + language."""

    def __init__(self, tour, language, on_back_to_tours, **kwargs):
        super().__init__(**kwargs)
        self._on_back_to_tours = on_back_to_tours

        outer_scroll = ScrollView(do_scroll_x=False)
        add_background_image(self, APP_BACKGROUND_IMAGE, overlay_rgba=LIGHT_PHOTO_OVERLAY)
        self.add_widget(outer_scroll)

        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=14, spacing=10)
        content.bind(minimum_height=content.setter("height"))
        outer_scroll.add_widget(content)

        self.tour = tour
        self.visitor = VisitorFactory.create_visitor("V-100", "Guest Visitor", language=language)
        self.strategy = PersonalizedStrategy()
        self._available_quiz = None
        # Visual-only path trail, starting from the tour's first stop by
        # default, so the map "continues" instead of resetting each time.
        self._visited_trail = [self.tour.stops[0].location_id]

        self.store = OfflineTourStore()
        self.store.save_tour(self.tour)
        # Preload comments other visitors (or this one, in an earlier
        # session) already left on this tour, so the Comments viewer
        # shows the full history rather than just this session's posts.
        for saved_comment in self.store.list_comments(self.tour.tour_id):
            self.visitor.add_comment(saved_comment)
        self.analytics = AnalyticsService()
        self.camera = CameraService()

        self.mediator = TourMediator(self.tour)
        self.mediator.register_visitor(self.visitor)
        self.mediator.add_observer(
            ContentTriggerObserver(self.tour, on_deliver=self._on_content_delivered)
        )
        self.mediator.add_observer(BadgeObserver(self.visitor, self.tour))
        self.mediator.add_observer(AnalyticsObserver(self.analytics, self.tour.tour_id))
        self.mediator.add_observer(
            QuizObserver(ALL_QUIZZES, on_quiz_triggered=self._on_quiz_available)
        )
        self.beacon_sim = BeaconSimulator(self.mediator)

        # ---- Title + back button ----
        title_bar = BoxLayout(size_hint_y=None, height=54, padding=(12, 8), spacing=8)
        add_background(title_bar, NAVY)
        self.back_btn = flat_button(tr("back_to_tours", language), TEAL, size_hint_x=None, width=90,
                                     on_release=lambda _b: self._on_back_to_tours())
        title_bar.add_widget(self.back_btn)
        title_bar.add_widget(Label(text=f"[b]{self.tour.title}[/b]", markup=True, color=WHITE, font_size=18))
        self.lang_toggle_btn = flat_button(
            "FR" if language == "en" else "EN", GOLD, size_hint_x=None, width=60,
            on_release=lambda _b: self._toggle_language(),
        )
        title_bar.add_widget(self.lang_toggle_btn)
        content.add_widget(title_bar)

        status_bar = BoxLayout(size_hint_y=None, height=44, padding=(12, 6))
        add_background(status_bar, GOLD)
        self.status_label = Label(text=self._status_text(), color=NAVY, bold=True, font_size=13)
        status_bar.add_widget(self.status_label)
        content.add_widget(status_bar)

        # ---- Map (real floor-plan background image, per this tour) ----
        floor_plan_path = tour_floor_plan_path(self.tour)
        map_panel = BoxLayout(size_hint_y=None, height=230, padding=4)
        add_background(map_panel, WHITE)
        self.map_widget = MapWidget(floor_plan_image_path=floor_plan_path)
        map_panel.add_widget(self.map_widget)
        content.add_widget(map_panel)

        # Show the default starting position (and the empty trail) immediately.
        self._refresh_map(current_location_id=self._visited_trail[0])
        self._active_stop = None

        # ---- Content display: a brief, plain-language description of
        # whichever stop the visitor is currently at. Never shows a
        # file path or other technical detail. ----
        content_panel = BoxLayout(orientation="vertical", size_hint_y=None, height=100, padding=10)
        add_background(content_panel, WHITE)
        self.content_label = Label(
            text=tr("tap_a_stop", language),
            color=NAVY, size_hint_y=None, height=90, halign="left", valign="top",
        )
        self.content_label.bind(size=self._resize_content_label)
        content_panel.add_widget(self.content_label)
        content.add_widget(content_panel)

        # ---- Media button: opens a closeable viewer with this stop's
        # photos, video, and audio (see ui/media_widget.py). ----
        self.media_button = flat_button(
            tr("media_button", language), GOLD, size_hint_y=None, height=48, disabled=True,
        )
        self.media_button.color = NAVY
        self.media_button.bind(on_release=lambda _b: self._open_media())
        content.add_widget(self.media_button)

        # ---- 3D model viewer (only shown for the one stop that has an
        # interactive 3D model) ----
        self.model3d_widget = Model3DWidget(size_hint_y=None, height=0, opacity=0)
        content.add_widget(self.model3d_widget)
        self.model3d_hint = Label(
            text=tr("drag_to_rotate", language), color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None, height=0, opacity=0, font_size=12,
        )
        content.add_widget(self.model3d_hint)

        # ---- Quiz button ----
        self._quiz_state = "none"  # "none" | "available" | "completed" — tracked so
        # the button text can be re-applied correctly after a language toggle.
        self.quiz_button = flat_button(
            tr("no_quiz", language), PLUM, size_hint_y=None, height=48, disabled=True,
        )
        self.quiz_button.bind(on_release=lambda _b: self._open_quiz())
        content.add_widget(self.quiz_button)

        # ---- Photo / comment / share actions ----
        action_row = BoxLayout(size_hint_y=None, height=48, spacing=8)
        self.photo_btn = flat_button(tr("take_photo", language), TEAL, on_release=lambda _b: self._take_photo())
        self.share_btn = flat_button(tr("share", language), CRIMSON, size_hint_x=None, width=90,
                                      on_release=lambda _b: self._share_current())
        action_row.add_widget(self.photo_btn)
        action_row.add_widget(self.share_btn)
        content.add_widget(action_row)

        comment_row = BoxLayout(size_hint_y=None, height=48, spacing=8)
        self.comment_input = TextInput(hint_text=tr("leave_comment", language), multiline=False)
        self.comment_btn = flat_button(tr("post", language), TEAL_DARK, size_hint_x=None, width=90,
                                        on_release=lambda _b: self._post_comment(self.comment_input))
        comment_row.add_widget(self.comment_input)
        comment_row.add_widget(self.comment_btn)
        content.add_widget(comment_row)

        # ---- Places to view what's been posted so far: every comment
        # left on this tour, and every photo this visitor has taken. ----
        gallery_row = BoxLayout(size_hint_y=None, height=48, spacing=8)
        self.view_comments_btn = flat_button(
            tr("view_comments", language), PLUM, on_release=lambda _b: self._view_comments(),
        )
        self.view_photos_btn = flat_button(
            tr("view_photos", language), PLUM, on_release=lambda _b: self._view_photos(),
        )
        gallery_row.add_widget(self.view_comments_btn)
        gallery_row.add_widget(self.view_photos_btn)
        content.add_widget(gallery_row)

        # ---- Stop buttons ----
        self.walk_to_a_stop_label = Label(
            text=f"[b]{tr('walk_to_a_stop', language)}[/b]", markup=True, color=NAVY,
            size_hint_y=None, height=28, halign="left",
        )
        content.add_widget(self.walk_to_a_stop_label)
        self._stop_buttons = []
        for i, stop in enumerate(self.tour.stops):
            color = TEAL if i % 2 == 0 else TEAL_DARK
            btn = flat_button(
                f"{tr('walk_to', language)}{stop.name}", color, size_hint_y=None, height=52,
                on_release=lambda _btn, s=stop: self._simulate_arrival(s),
            )
            content.add_widget(btn)
            self._stop_buttons.append((btn, stop))

    # -- Event handlers -------------------------------------------------

    def _toggle_language(self) -> None:
        new_lang = "fr" if self.visitor.preferences.language == "en" else "en"
        self.visitor.update_preferences(language=new_lang)
        self.lang_toggle_btn.text = "FR" if new_lang == "en" else "EN"
        self._apply_ui_language(new_lang)
        current_stop = self._current_stop()
        if current_stop is not None:
            self._on_content_delivered(self.visitor.visitor_id, current_stop, current_stop.deliver(self.visitor))

    def _apply_ui_language(self, lang: str) -> None:
        """Re-applies every static UI string (buttons, labels, hints —
        not per-exhibit content, which is refreshed separately via
        _on_content_delivered) in the given language."""
        self.back_btn.text = tr("back_to_tours", lang)
        self.model3d_hint.text = tr("drag_to_rotate", lang)
        self.photo_btn.text = tr("take_photo", lang)
        self.share_btn.text = tr("share", lang)
        self.comment_input.hint_text = tr("leave_comment", lang)
        self.comment_btn.text = tr("post", lang)
        self.view_comments_btn.text = tr("view_comments", lang)
        self.view_photos_btn.text = tr("view_photos", lang)
        self.walk_to_a_stop_label.text = f"[b]{tr('walk_to_a_stop', lang)}[/b]"
        for btn, stop in self._stop_buttons:
            btn.text = f"{tr('walk_to', lang)}{stop.name}"
        self.status_label.text = self._status_text()

        # Media button: keep enabled/disabled state consistent, but no
        # text needs re-applying (it's an icon + fixed label).

        # Quiz button: re-apply text for whichever of the three states
        # it's currently in.
        if self._quiz_state == "available":
            self.quiz_button.text = tr("quiz_available", lang)
        elif self._quiz_state == "completed":
            self.quiz_button.text = tr("quiz_completed", lang)
        else:
            self.quiz_button.text = tr("no_quiz", lang)

    def _lang(self) -> str:
        return self.visitor.preferences.language

    def _simulate_arrival(self, stop) -> None:
        self._available_quiz = None
        self._quiz_state = "none"
        self.quiz_button.disabled = True
        self.quiz_button.text = tr("no_quiz", self._lang())

        self.beacon_sim.fire_signal(self.visitor.visitor_id, stop.location_id)
        self.status_label.text = self._status_text()
        self._refresh_map(current_location_id=stop.location_id)

    def _resize_content_label(self, instance, _size) -> None:
        instance.text_size = (instance.width, None)

    def _on_content_delivered(self, visitor_id, stop, message) -> None:
        self._active_stop = stop
        self.content_label.text = f"[b]{stop.name}[/b]\n{stop.localized_description(self.visitor)}"
        self.content_label.markup = True
        self._hide_all_media()

        # The Media button always opens this stop's photos/video/audio,
        # regardless of which content type drives the main narration.
        self.media_button.disabled = not stop.media.has_any()

        content = stop.content
        if isinstance(content, ModelGuide):
            self.model3d_widget.set_shape(content.shape)
            self.model3d_widget.height = 220
            self.model3d_widget.opacity = 1
            self.model3d_hint.height = 20
            self.model3d_hint.opacity = 1

    def _hide_all_media(self) -> None:
        self.model3d_widget.height = 0
        self.model3d_widget.opacity = 0
        self.model3d_hint.height = 0
        self.model3d_hint.opacity = 0

    def _open_media(self) -> None:
        if self._active_stop is None:
            return
        content = self._active_stop.content
        frames_dir = getattr(content, "frames_dir", None)
        frame_count = getattr(content, "frame_count", 0)
        open_media_popup(self._active_stop, self._lang(), frames_dir=frames_dir, frame_count=frame_count)

    def _on_quiz_available(self, visitor_id, quiz) -> None:
        if visitor_id != self.visitor.visitor_id:
            return
        self._available_quiz = quiz
        self._quiz_state = "available"
        self.quiz_button.disabled = False
        self.quiz_button.text = tr("quiz_available", self._lang())

    def _open_quiz(self) -> None:
        if self._available_quiz is not None:
            self._show_quiz_popup(self._available_quiz)

    def _take_photo(self) -> None:
        current_stop = self._current_stop()
        title = current_stop.content.title if current_stop else "Museum Visit"
        location_id = current_stop.location_id if current_stop else "unknown"
        photo = self.camera.capture_photo(self.visitor.visitor_id, location_id, title)
        self.visitor.add_photo(photo)
        self.content_label.text = tr("photo_captured", self._lang())

    def _post_comment(self, comment_input):
        text = comment_input.text.strip()
        if not text:
            return
        current_stop = self._current_stop()
        location_id = current_stop.location_id if current_stop else "general"
        stop_name = current_stop.name if current_stop else tr("choose_a_tour", self._lang())
        comment = Comment(self.visitor.visitor_id, location_id, text)
        self.visitor.add_comment(comment)
        self.store.save_comment(self.tour.tour_id, comment)
        comment_input.text = ""
        self.content_label.text = tr("comment_posted", self._lang()).format(stop=stop_name, text=text)

    def _view_comments(self) -> None:
        open_comments_popup(self.visitor.comments, self._lang())

    def _view_photos(self) -> None:
        open_photos_popup(self.visitor.photos, self._lang())

    def _share_current(self) -> None:
        """
        Opens a "Share via..." popup with real, working actions rather
        than silently copying to the clipboard. Note on scope: a single
        unified OS share sheet (the thing that lists Bluetooth, WhatsApp,
        every installed app at once) is an Android/iOS feature — desktop
        Windows/Mac/Linux apps don't get one from the OS, so each option
        below launches the real, closest equivalent for this platform
        instead of faking a picker that wouldn't actually work.
        """
        lang = self._lang()
        current_stop = self._current_stop()
        exhibit_title = current_stop.content.title if current_stop else self.tour.title
        last_photo = self.visitor.photos[-1] if self.visitor.photos else None
        last_comment = self.visitor.comments[-1] if self.visitor.comments else None
        text = build_share_text(exhibit_title, photo=last_photo, comment=last_comment)

        box = BoxLayout(orientation="vertical", spacing=8, padding=12)
        add_background(box, CREAM)
        popup = Popup(title=tr("share_via_title", lang), content=box, size_hint=(0.8, 0.55),
                       title_color=WHITE, separator_color=GOLD, auto_dismiss=True)

        def close_and(fn):
            def _handler(_b):
                popup.dismiss()
                fn()
            return _handler

        box.add_widget(flat_button(tr("share_whatsapp", lang), TEAL, size_hint_y=None, height=48,
                                    on_release=close_and(lambda: self._share_via_whatsapp(text))))
        box.add_widget(flat_button(tr("share_email", lang), TEAL_DARK, size_hint_y=None, height=48,
                                    on_release=close_and(lambda: self._share_via_email(exhibit_title, text))))
        box.add_widget(flat_button(tr("share_bluetooth", lang), PLUM, size_hint_y=None, height=48,
                                    on_release=close_and(lambda: self._share_via_bluetooth(text))))
        box.add_widget(flat_button(tr("share_copy", lang), CRIMSON, size_hint_y=None, height=48,
                                    on_release=close_and(lambda: self._share_via_clipboard(text))))
        box.add_widget(flat_button(tr("share_cancel", lang), (0.5, 0.5, 0.5, 1), size_hint_y=None, height=40,
                                    on_release=lambda _b: popup.dismiss()))
        popup.open()

    def _share_via_whatsapp(self, text: str) -> None:
        # wa.me is WhatsApp's own deep-link scheme: on a phone with
        # WhatsApp installed it opens straight into the app's share
        # composer; on desktop it opens WhatsApp Web/desktop via the
        # browser. This is the real, standard way apps hand text to
        # WhatsApp without a native OS share sheet.
        url = f"https://wa.me/?text={quote(text)}"
        webbrowser.open(url)
        self.content_label.text = tr("share_whatsapp_opened", self._lang())

    def _share_via_email(self, subject: str, text: str) -> None:
        if plyer_email is not None:
            try:
                plyer_email.send(subject=subject, text=text)
                self.content_label.text = tr("share_email_opened", self._lang())
                return
            except NotImplementedError:
                pass
            except Exception:
                pass
        # Fallback: a mailto: link, which every desktop OS routes to
        # whatever the user's default mail client is.
        url = f"mailto:?subject={quote(subject)}&body={quote(text)}"
        webbrowser.open(url)
        self.content_label.text = tr("share_email_opened", self._lang())

    def _share_via_bluetooth(self, text: str) -> None:
        # There is no cross-platform API for sending arbitrary text over
        # Bluetooth from a desktop app. On Windows, the closest real
        # equivalent is the built-in Bluetooth File Transfer wizard
        # (fsquirt.exe), which can send a file to a paired device — so
        # write the share text to a temp file and hand it to that. Any
        # other platform (or a Windows machine without fsquirt) falls
        # back honestly to copying the text instead of pretending it sent.
        if kivy_platform == "win":
            try:
                fd, path = tempfile.mkstemp(suffix=".txt", prefix="museum_share_")
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    f.write(text)
                subprocess.Popen(["fsquirt.exe", "/send", path])
                self.content_label.text = tr("share_bluetooth_opened", self._lang())
                return
            except Exception:
                pass
        self._share_via_clipboard(text, bluetooth_fallback=True)

    def _share_via_clipboard(self, text: str, bluetooth_fallback: bool = False) -> None:
        try:
            Clipboard.copy(text)
            self.content_label.text = (
                tr("share_bluetooth_unavailable", self._lang()) if bluetooth_fallback
                else tr("share_copied", self._lang())
            )
        except Exception:
            self.content_label.text = text

    def _show_quiz_popup(self, quiz) -> None:
        """
        Walks the visitor through every question in the quiz, one at a
        time: shows the question, reveals whether the chosen answer was
        correct or wrong immediately, lets them continue to the next
        question or quit early, and finishes with a final score summary.
        """
        lang = self._lang()
        state = {"index": 0, "answers": [], "quit": False}
        box = BoxLayout(orientation="vertical", spacing=8, padding=12)
        add_background(box, CREAM)
        popup = Popup(title=tr("quiz_time_title", lang), content=box, size_hint=(0.88, 0.6),
                       title_color=WHITE, separator_color=GOLD, auto_dismiss=False)

        def clear_box():
            box.clear_widgets()

        def render_question():
            clear_box()
            i = state["index"]
            question = quiz.questions[i]
            box.add_widget(Label(
                text=tr("question_of", lang).format(i=i + 1, n=len(quiz.questions)),
                color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=22, font_size=12,
            ))
            box.add_widget(Label(text=question.prompt, color=NAVY, bold=True))
            for choice_index, choice in enumerate(question.choices):
                box.add_widget(flat_button(
                    choice, TEAL, on_release=lambda _b, ci=choice_index: submit_answer(ci),
                ))
            quit_btn = flat_button(tr("quit_quiz", lang), CRIMSON, size_hint_y=None, height=40,
                                    on_release=lambda _b: quit_quiz())
            box.add_widget(quit_btn)

        def submit_answer(chosen_index):
            question = quiz.questions[state["index"]]
            state["answers"].append(chosen_index)
            is_correct = question.is_correct(chosen_index)

            clear_box()
            if is_correct:
                feedback = Label(text=tr("correct", lang), color=(0.15, 0.5, 0.2, 1), bold=True, font_size=18)
            else:
                correct_text = question.choices[question.correct_index]
                feedback = Label(
                    text=f"{tr('wrong_prefix', lang)} {correct_text}",
                    color=CRIMSON, bold=True,
                )
            box.add_widget(feedback)

            is_last = state["index"] == len(quiz.questions) - 1
            next_label = tr("see_final_score", lang) if is_last else tr("next_question", lang)
            box.add_widget(flat_button(next_label, TEAL_DARK, size_hint_y=None, height=44,
                                        on_release=lambda _b: advance()))
            box.add_widget(flat_button(tr("quit_quiz", lang), CRIMSON, size_hint_y=None, height=40,
                                        on_release=lambda _b: quit_quiz()))

        def advance():
            if state["index"] == len(quiz.questions) - 1:
                show_final_score()
            else:
                state["index"] += 1
                render_question()

        def quit_quiz():
            state["quit"] = True
            finish(early=True)

        def show_final_score():
            finish(early=False)

        def finish(early: bool) -> None:
            answers = state["answers"]
            correct_count = sum(
                1 for q, a in zip(quiz.questions, answers) if q.is_correct(a)
            )
            points = quiz.score(answers)
            self.visitor.award_points(points)
            unlocked_collectible = quiz.is_perfect(answers) and quiz.collectible is not None
            if unlocked_collectible:
                self.visitor.award_collectible(quiz.collectible)

            clear_box()
            title_text = tr("quiz_ended_early", lang) if early else tr("quiz_complete", lang)
            box.add_widget(Label(text=title_text, color=NAVY, bold=True, font_size=18,
                                  size_hint_y=None, height=34))
            box.add_widget(Label(
                text=tr("score_label", lang).format(c=correct_count, n=len(quiz.questions)),
                color=NAVY, bold=True, size_hint_y=None, height=28,
            ))
            box.add_widget(Label(
                text=tr("points_earned", lang).format(p=points), color=(0.3, 0.3, 0.3, 1),
                size_hint_y=None, height=24,
            ))
            if unlocked_collectible:
                box.add_widget(Label(
                    text=tr("collectible_unlocked", lang).format(name=quiz.collectible.name),
                    color=GOLD, bold=True, size_hint_y=None, height=26,
                ))
            elif quiz.collectible is not None and not early:
                box.add_widget(Label(
                    text=tr("unlock_hint", lang),
                    color=(0.4, 0.4, 0.4, 1), size_hint_y=None, height=40,
                ))
            box.add_widget(flat_button(tr("close", lang), NAVY, size_hint_y=None, height=44,
                                        on_release=lambda _b: popup.dismiss()))

            self.status_label.text = self._status_text()
            self._quiz_state = "completed"
            self.quiz_button.disabled = True
            self.quiz_button.text = tr("quiz_completed", lang)

        render_question()
        popup.open()

    # -- Helpers ----------------------------------------------------------

    def _current_stop(self):
        if not self.visitor.visited_locations:
            return None
        return self.tour.stop_at_location(self.visitor.visited_locations[-1])

    def _refresh_map(self, current_location_id=None) -> None:
        if current_location_id and (not self._visited_trail or self._visited_trail[-1] != current_location_id):
            self._visited_trail.append(current_location_id)
        recommendation = self.strategy.recommend_next_stop(self.tour, self.visitor)
        self.map_widget.refresh(
            self.tour, FLOOR_PLAN_POSITIONS,
            visited_location_ids=self._visited_trail,
            current_location_id=current_location_id or self._visited_trail[-1],
            recommended_location_id=recommendation.location_id if recommendation else None,
        )

    def _status_text(self) -> str:
        lang = self._lang()
        state_name = self.visitor.state.name if self.visitor.state else tr("status_exploring", lang)
        return (
            f"{tr('status_state', lang)} {state_name}  |  "
            f"{tr('status_points', lang)} {self.visitor.points}  |  "
            f"{tr('status_visited', lang)} {len(self.visitor.visited_locations)}/{len(self.tour.stops)}  |  "
            f"{tr('status_collectibles', lang)} {len(self.visitor.collectibles)}"
        )


# ============================================================
# Admin Login + CMS Screens
# ============================================================

class AdminLoginScreen(Screen):
    def __init__(self, auth_service, on_success, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = auth_service
        self._on_success = on_success

        root = BoxLayout(orientation="vertical", padding=24, spacing=14)
        add_background_image(root, APP_BACKGROUND_IMAGE, overlay_rgba=LIGHT_PHOTO_OVERLAY)
        self.add_widget(root)

        root.add_widget(Label(text="[b]Staff Login[/b]", markup=True, color=NAVY,
                               font_size=20, size_hint_y=None, height=40))
        root.add_widget(Label(text="Enter the staff PIN to access the Admin CMS.",
                               color=(0.3, 0.3, 0.3, 1), size_hint_y=None, height=30))

        self.pin_input = TextInput(hint_text="Staff PIN", multiline=False, password=True,
                                    size_hint_y=None, height=44)
        root.add_widget(self.pin_input)

        self.error_label = Label(text="", color=CRIMSON, size_hint_y=None, height=24)
        root.add_widget(self.error_label)

        login_btn = flat_button("Unlock Admin CMS", NAVY, size_hint_y=None, height=48,
                                 on_release=lambda _b: self._attempt_login())
        root.add_widget(login_btn)
        root.add_widget(Label(text="", size_hint_y=1))

    def _attempt_login(self) -> None:
        if self.auth_service.check_pin(self.pin_input.text.strip()):
            self.error_label.text = ""
            self.pin_input.text = ""
            self._on_success()
        else:
            self.error_label.text = "Incorrect PIN. Try again."


class AdminCMSScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(AdminScreen())


# ============================================================
# Root layout + App
# ============================================================

class RootLayout(BoxLayout):
    """Top-level layout: a toggle bar plus a ScreenManager underneath."""

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.manager = ScreenManager()
        self.admin_auth = AdminAuthService()

        self.manager.add_widget(TourSelectScreen(on_start_tour=self._start_tour, name="select"))
        self.manager.add_widget(
            AdminLoginScreen(self.admin_auth, on_success=self._enter_admin, name="admin_login")
        )
        self.manager.add_widget(AdminCMSScreen(name="admin"))

        toggle_bar = BoxLayout(size_hint_y=None, height=44, spacing=4, padding=4)
        add_background(toggle_bar, NAVY)
        toggle_bar.add_widget(flat_button(
            "Tour Selection", TEAL, on_release=lambda _b: setattr(self.manager, "current", "select"),
        ))
        toggle_bar.add_widget(flat_button(
            "Admin CMS", GOLD, on_release=lambda _b: self._go_to_admin(),
        ))
        self.add_widget(toggle_bar)
        self.add_widget(self.manager)

    def _start_tour(self, tour, language) -> None:
        if self.manager.has_screen("visitor"):
            self.manager.remove_widget(self.manager.get_screen("visitor"))
        visitor_screen = TourVisitorScreen(
            tour, language, on_back_to_tours=self._back_to_tours, name="visitor"
        )
        self.manager.add_widget(visitor_screen)
        self.manager.current = "visitor"

    def _back_to_tours(self) -> None:
        self.manager.current = "select"

    def _go_to_admin(self) -> None:
        self.manager.current = "admin" if self.admin_auth.is_unlocked else "admin_login"

    def _enter_admin(self) -> None:
        self.manager.current = "admin"


class MuseumTourApp(App):
    def build(self):
        return RootLayout()


if __name__ == "__main__":
    MuseumTourApp().run()
