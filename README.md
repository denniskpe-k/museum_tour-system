# Museum Guided Tour System

Project 3 — a Python OOP group project. A tablet-app simulation that gives
museum visitors interactive guided tours: a Tour Selection screen, multimedia
exhibit content that is genuinely playable — real spoken audio narration
(offline text-to-speech), a real animated video clip (Ken Burns-style
pan/zoom with captions), and a real interactive 3D wireframe viewer you can
drag to rotate — alongside images and text, all with real English/French
translations, a real generated floor-plan map with a continuous
visited-path trail and wayfinding, location-triggered playback (via
simulated beacons/GPS, since no real hardware is available), 5-question
per-stop quizzes with instant right/wrong feedback, a final score summary,
and a quit-anytime option, plus badges/collectibles, social features (photo
capture with real webcam + simulated fallback, comments, and a Share
action), visitor analytics, accessibility options, offline mode, and a
PIN-gated Admin CMS for staff to build new tours.

See the accompanying PDF guides for a full explanation of the design and
a line-by-line walkthrough of the code. See **MEDIA_GUIDE.md** for how
to add real photos, video, and audio for every tour stop — each stop
now has a "Media" button that opens a closeable viewer for them.

## Requirements

```
pip install -r requirements.txt
```

`kivy` is only needed to run the graphical UI. `opencv-python` is optional —
it enables real webcam photo capture on a machine that has one; without it
(or without a camera), the app automatically falls back to a generated
placeholder photo. Everything else (models, patterns, services, tests)
runs with just `SQLAlchemy`, `Pillow`, and `pytest`.

## Running it

```bash
# Graphical Kivy UI (default — visitor view + Admin CMS toggle)
python main.py

# Core console demo (no GUI needed) — 4-stop tour, all 5 design patterns
python main.py --console

# Extended console demo — 6-stop "Treasures Through Time" tour with real
# exhibit photos, a 3D-model stop, quizzes, social features, and analytics
python main.py --extended
```

## Running the tests

```bash
pytest -v
```

55 tests covering the domain models, all five design patterns, the
offline database, and every extended feature (including quiz scoring
for full completion, partial/early-quit completion, mixed
correct/wrong answers, and real audio/video/3D asset generation).

## Admin CMS access

The Admin CMS is PIN-gated. Default staff PIN: **MUSEUM2026** (set in
`services/admin_auth.py` — change it there for your own deployment).

## Project layout

```
museum_tour_system/
├── assets/
│   ├── images/       # Real exhibit photographs, shown in the Media popup's Photos tab
│   ├── audio/          # Real narration/audio files, played in the Media popup's Audio tab
│   ├── video/            # Real .mp4 files, played in the Media popup's Video tab
│   ├── video_frames/       # Generated animated frame sequences (fallback video preview)
│   ├── models/               # (empty) placeholder folder for real .glb/.obj files
│   ├── floorplans/             # Generated floor-plan background images (auto-created)
│   └── photos/                   # Visitor photos are written here at runtime
├── models/            # Core domain classes
│   ├── content.py      # Abstract TourContent + Audio/Video/Text/Image/Model/Accessibility
│   │                     (+ translations support, + real asset paths for audio/video/3D)
│   ├── tour.py          # Tour, TourStop (composition) — now also carries a stop's brief
│   │                      description and its StopMedia (photos/video/audio) bundle
│   ├── media.py           # StopMedia — a stop's photo gallery + one video + one audio file,
│   │                        independent of which TourContent type drives the stop
│   ├── visitor.py        # Visitor, VisitorPreferences (encapsulation)
│   ├── social.py          # Photo, Comment, build_share_text()
│   └── quiz.py             # QuizQuestion, Quiz, Collectible
├── patterns/          # The five required design patterns
│   ├── factory.py
│   ├── strategy.py
│   ├── observer.py     # + AnalyticsObserver, QuizObserver
│   ├── state.py
│   └── mediator.py
├── services/          # Supporting infrastructure
│   ├── location_simulator.py   # mock beacon/GPS signals
│   ├── database.py             # SQLAlchemy/SQLite offline storage (JSON content_extra)
│   ├── analytics.py             # dwell time, popular stops, route analysis
│   ├── camera_service.py         # real webcam capture w/ simulated fallback
│   ├── admin_auth.py              # PIN gate for the Admin CMS
│   ├── floorplan_generator.py      # generates a real floor-plan-style map image
│   ├── audio_generator.py           # offline TTS narration generator (espeak-ng)
│   ├── video_generator.py            # Ken Burns-style animated frame generator
│   ├── model3d_geometry.py            # pure 3D math for the wireframe viewer (no Kivy)
│   └── demo_data.py                     # sample tours, quizzes, floor-plan positions,
│                                           tour registry, French translations
├── ui/
│   ├── app.py           # Kivy tablet UI: Tour Selection, visitor screen,
│   │                       admin login gate, Admin CMS toggle, brief per-stop
│   │                       description + "Media" button, 3D model playback
│   ├── theme.py           # Shared colors and small widget helpers (used by app.py
│   │                        and media_widget.py so they don't import each other)
│   ├── media_widget.py     # The "Media" popup: closeable Photos/Video/Audio viewer
│   │                        for one stop; never shows a file path
│   ├── map_widget.py         # Interactive floor-plan map: real background image,
│   │                          continuous visited-path trail, wayfinding
│   ├── video_widget.py         # Frame-cycling fallback "video" preview (no codec
│   │                            backend needed) — used only when no real .mp4 exists
│   ├── model3d_widget.py         # Interactive draggable 3D wireframe viewer
│   └── admin_screen.py             # Admin CMS: staff tour builder
├── tests/
│   └── test_museum_system.py
├── main.py             # Entry point (GUI by default; --console / --extended)
├── MEDIA_GUIDE.md      # How to source, name, and place real photos/video/audio
└── requirements.txt
```
