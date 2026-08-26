"""
ui/media_widget.py

The "Media" popup: a single closeable viewer for a tour stop's
photos, video, and audio, opened by the "Media" button on the
visitor screen. Visitors can close it whenever they like (a Close
button, or tapping outside the popup). No file path or other
technical detail is ever shown — only titles/captions, or a friendly
"hasn't been added yet" message when a file is missing.
"""

import os

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.core.audio import SoundLoader

from ui.theme import NAVY, TEAL, TEAL_DARK, PLUM, CRIMSON, GOLD, add_background, flat_button
from ui.video_widget import VideoPlayerWidget
from services.i18n import tr

try:
    from kivy.uix.video import Video
    _VIDEO_AVAILABLE = True
except Exception:  # pragma: no cover - depends on optional codec backend
    Video = None
    _VIDEO_AVAILABLE = False

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def open_media_popup(stop, lang, frames_dir=None, frame_count=0):
    """Build and open the Media popup for one tour stop."""
    media = stop.media

    root = BoxLayout(orientation="vertical", spacing=8, padding=10)

    tab_row = BoxLayout(size_hint_y=None, height=44, spacing=6)
    root.add_widget(tab_row)

    body = BoxLayout(orientation="vertical")
    root.add_widget(body)

    close_btn = flat_button(tr("close", lang), CRIMSON, size_hint_y=None, height=48)
    root.add_widget(close_btn)

    popup = Popup(title=stop.name, content=root, size_hint=(0.92, 0.85), auto_dismiss=True)
    close_btn.bind(on_release=lambda _b: popup.dismiss())

    # audio_lang starts out matching the app's current language, but can be
    # switched independently from inside the Audio tab (see render_audio)
    # so a visitor can flip between the English and French narration
    # without leaving the popup or changing the whole app's language.
    state = {"sound": None, "video_widget": None, "frame_widget": None, "audio_lang": lang}

    def stop_playback():
        if state["sound"] is not None:
            state["sound"].stop()
            state["sound"] = None
        if state["video_widget"] is not None:
            try:
                state["video_widget"].state = "stop"
            except Exception:
                pass
        if state["frame_widget"] is not None:
            state["frame_widget"].stop()

    def clear_body():
        stop_playback()
        body.clear_widgets()

    # ---- Photos ----
    photo_state = {"index": 0}

    def render_photos(_b=None):
        clear_body()
        images = media.existing_images(PROJECT_ROOT)
        if not images:
            body.add_widget(Label(text=tr("media_no_photos", lang), color=NAVY))
            return
        idx = photo_state["index"] % len(images)
        info = images[idx]
        col = BoxLayout(orientation="vertical", spacing=6)
        col.add_widget(Image(
            source=os.path.join(PROJECT_ROOT, info["path"]),
            allow_stretch=True, keep_ratio=True,
        ))
        caption = info.get("caption", "")
        if caption:
            col.add_widget(Label(text=caption, color=NAVY, size_hint_y=None, height=26))
        if len(images) > 1:
            nav_row = BoxLayout(size_hint_y=None, height=40, spacing=6)
            prev_btn = flat_button(tr("media_prev", lang), TEAL_DARK)
            count_lbl = Label(
                text=tr("media_photo_count", lang).format(i=idx + 1, n=len(images)), color=NAVY,
            )
            next_btn = flat_button(tr("media_next", lang), TEAL_DARK)

            def go_prev(_btn):
                photo_state["index"] = (photo_state["index"] - 1) % len(images)
                render_photos()

            def go_next(_btn):
                photo_state["index"] = (photo_state["index"] + 1) % len(images)
                render_photos()

            prev_btn.bind(on_release=go_prev)
            next_btn.bind(on_release=go_next)
            nav_row.add_widget(prev_btn)
            nav_row.add_widget(count_lbl)
            nav_row.add_widget(next_btn)
            col.add_widget(nav_row)
        body.add_widget(col)

    # ---- Video ----
    def render_video(_b=None):
        clear_body()

        def show_frame_fallback():
            if frames_dir and os.path.exists(os.path.join(PROJECT_ROOT, frames_dir)):
                # Fallback preview (generated pan/zoom animation) for stops
                # that don't have a real video file supplied yet, or for
                # machines where no real video codec backend is available.
                frame_widget = VideoPlayerWidget()
                frame_widget.load(os.path.join(PROJECT_ROOT, frames_dir), frame_count)
                frame_widget.play()
                state["frame_widget"] = frame_widget
                body.add_widget(frame_widget)
                return True
            return False

        if media.video_exists(PROJECT_ROOT) and _VIDEO_AVAILABLE:
            full_path = os.path.join(PROJECT_ROOT, media.video_path)
            try:
                video = Video(source=full_path, state="play", options={"eos": "stop"})
            except Exception:
                # No working video codec backend (e.g. ffpyplayer/gstreamer
                # isn't installed) — fall back to the frame preview instead
                # of leaving a blank Video tab.
                video = None
            if video is not None:
                state["video_widget"] = video
                body.add_widget(video)

                controls = BoxLayout(size_hint_y=None, height=40, spacing=6)
                toggle_btn = flat_button(tr("media_pause_video", lang), TEAL_DARK)

                def toggle(_btn):
                    if video.state == "play":
                        video.state = "pause"
                        toggle_btn.text = tr("media_play_video", lang)
                    else:
                        video.state = "play"
                        toggle_btn.text = tr("media_pause_video", lang)

                toggle_btn.bind(on_release=toggle)
                controls.add_widget(toggle_btn)
                body.add_widget(controls)
                return

        if not show_frame_fallback():
            body.add_widget(Label(text=tr("media_no_video", lang), color=NAVY))

    # ---- Audio ----
    def render_audio(_b=None):
        stop_playback()
        body.clear_widgets()
        audio_lang = state["audio_lang"]

        col = BoxLayout(orientation="vertical", spacing=10, padding=(0, 20))
        col.add_widget(Label(text=stop.name, color=NAVY, bold=True))

        # Language switch: lets the visitor pick which recorded narration
        # (English or French) to hear here, independent of the app's
        # overall UI language.
        lang_row = BoxLayout(size_hint_y=None, height=40, spacing=6, padding=(40, 0))
        en_audio_btn = flat_button(
            "English", TEAL if audio_lang == "en" else (0.7, 0.7, 0.7, 1),
        )
        fr_audio_btn = flat_button(
            "Français", GOLD if audio_lang == "fr" else (0.7, 0.7, 0.7, 1),
        )

        def switch_audio_lang(new_lang):
            if state["audio_lang"] == new_lang:
                return
            state["audio_lang"] = new_lang
            render_audio()

        en_audio_btn.bind(on_release=lambda _b: switch_audio_lang("en"))
        fr_audio_btn.bind(on_release=lambda _b: switch_audio_lang("fr"))
        lang_row.add_widget(en_audio_btn)
        lang_row.add_widget(fr_audio_btn)
        col.add_widget(lang_row)

        if not media.audio_exists_for(PROJECT_ROOT, audio_lang):
            col.add_widget(Label(text=tr("media_no_audio", lang), color=NAVY))
            body.add_widget(col)
            return

        play_btn = flat_button(tr("media_play_audio", lang), TEAL, size_hint_y=None, height=48)

        def toggle_audio(_btn):
            if state["sound"] is not None:
                state["sound"].stop()
                state["sound"] = None
                play_btn.text = tr("media_play_audio", lang)
                return
            full_path = os.path.join(PROJECT_ROOT, media.audio_path_for(state["audio_lang"]))
            sound = SoundLoader.load(full_path)
            if sound is None:
                return
            state["sound"] = sound

            def on_stop(*_a):
                state["sound"] = None
                play_btn.text = tr("media_play_audio", lang)

            sound.bind(on_stop=on_stop)
            sound.play()
            play_btn.text = tr("media_pause_audio", lang)

        play_btn.bind(on_release=toggle_audio)
        col.add_widget(play_btn)
        body.add_widget(col)

    for key, render_fn in (
        ("media_tab_photos", render_photos),
        ("media_tab_video", render_video),
        ("media_tab_audio", render_audio),
    ):
        btn = flat_button(tr(key, lang), PLUM)
        btn.bind(on_release=render_fn)
        tab_row.add_widget(btn)

    popup.bind(on_dismiss=lambda *_a: stop_playback())

    render_photos()
    popup.open()
    return popup
