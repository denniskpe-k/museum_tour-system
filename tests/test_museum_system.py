"""
tests/test_museum_system.py

Pytest suite covering the domain models and every design pattern.
Run with:  pytest -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from models.content import AudioGuide, VideoGuide, TextGuide, AccessibilityContent, TourContent
from models.tour import Tour, TourStop
from models.visitor import Visitor, VisitorPreferences
from patterns.factory import TourFactory, VisitorFactory, ContentFactory
from patterns.strategy import SequentialStrategy, PopularityStrategy, PersonalizedStrategy
from patterns.observer import LocationSubject, ContentTriggerObserver, BadgeObserver
from patterns.state import ExploringState, AtStopState, InGalleryState
from patterns.mediator import TourMediator
from services.database import OfflineTourStore
from services.demo_data import SAMPLE_TOUR_SPEC


# ---------------------------------------------------------------------
# Domain model tests
# ---------------------------------------------------------------------

def test_tour_content_is_abstract():
    with pytest.raises(TypeError):
        TourContent("Cannot instantiate me")


def test_audio_guide_presents_itself():
    guide = AudioGuide("Intro", 30, narrator="Ama")
    output = guide.present_content()
    assert "Intro" in output and "Ama" in output


def test_accessibility_content_wraps_base_content():
    base = TextGuide("Painting X", "A description of painting X.")
    wrapped = AccessibilityContent(base, mode="audio_description")
    output = wrapped.present_content()
    assert "Painting X" in output
    assert "audio_description" in output


def test_accessibility_content_rejects_bad_mode():
    base = TextGuide("Painting Y", "Body text")
    with pytest.raises(ValueError):
        AccessibilityContent(base, mode="not_a_real_mode")


def test_tour_stop_composition_and_ordering():
    tour = Tour("T-X", "Test Tour", "general")
    tour.add_stop(TourStop("B", "loc-b", TextGuide("B", "b"), order=2))
    tour.add_stop(TourStop("A", "loc-a", TextGuide("A", "a"), order=1))
    assert [s.name for s in tour.stops] == ["A", "B"]


def test_tour_finds_stop_by_location():
    tour = Tour("T-X", "Test Tour", "general")
    stop = TourStop("Entrance", "loc-1", TextGuide("Welcome", "hi"), order=1)
    tour.add_stop(stop)
    assert tour.stop_at_location("loc-1") is stop
    assert tour.stop_at_location("does-not-exist") is None


def test_visitor_encapsulation_prevents_duplicate_path_entries():
    visitor = Visitor("V-1", "Kojo")
    visitor.record_visit("loc-1")
    visitor.record_visit("loc-1")  # duplicate, immediately repeated
    assert visitor.visited_locations == ["loc-1"]


def test_visitor_path_is_read_only_copy():
    visitor = Visitor("V-1", "Kojo")
    visitor.record_visit("loc-1")
    path = visitor.visited_locations
    path.append("hacked-in")
    # Mutating the returned list must not affect the visitor's real state.
    assert visitor.visited_locations == ["loc-1"]


def test_visitor_preferences_accessibility_modes():
    prefs = VisitorPreferences(needs_audio_description=True, needs_sign_language=True)
    assert set(prefs.accessibility_modes()) == {"audio_description", "sign_language"}


# ---------------------------------------------------------------------
# Factory pattern
# ---------------------------------------------------------------------

def test_content_factory_creates_correct_types():
    audio = ContentFactory.create_content("audio", title="A", duration_seconds=10, narrator="N")
    video = ContentFactory.create_content("video", title="V", duration_seconds=20)
    text = ContentFactory.create_content("text", title="T", body="hello world")
    assert isinstance(audio, AudioGuide)
    assert isinstance(video, VideoGuide)
    assert isinstance(text, TextGuide)


def test_tour_factory_builds_full_tour_from_spec():
    tour = TourFactory.create_tour(SAMPLE_TOUR_SPEC)
    assert tour.title == SAMPLE_TOUR_SPEC["title"]
    assert len(tour.stops) == len(SAMPLE_TOUR_SPEC["stops"])


def test_visitor_factory_applies_preferences():
    visitor = VisitorFactory.create_visitor("V-9", "Test", needs_sign_language=True)
    assert visitor.preferences.needs_sign_language is True


# ---------------------------------------------------------------------
# Strategy pattern
# ---------------------------------------------------------------------

def test_sequential_strategy_returns_first_unvisited():
    tour = TourFactory.create_tour(SAMPLE_TOUR_SPEC)
    visitor = VisitorFactory.create_visitor("V-1", "Test")
    first_stop = SequentialStrategy().recommend_next_stop(tour, visitor)
    assert first_stop.order == 1
    visitor.record_visit(first_stop.location_id)
    second_stop = SequentialStrategy().recommend_next_stop(tour, visitor)
    assert second_stop.order == 2


def test_popularity_strategy_picks_shortest_content():
    tour = TourFactory.create_tour(SAMPLE_TOUR_SPEC)
    visitor = VisitorFactory.create_visitor("V-1", "Test")
    stop = PopularityStrategy().recommend_next_stop(tour, visitor)
    shortest = min(tour.stops, key=lambda s: s.content.duration_seconds)
    assert stop.location_id == shortest.location_id


def test_personalized_strategy_falls_back_when_no_match():
    tour = TourFactory.create_tour(SAMPLE_TOUR_SPEC)
    visitor = VisitorFactory.create_visitor("V-1", "Test")  # no special needs
    stop = PersonalizedStrategy().recommend_next_stop(tour, visitor)
    assert stop is not None


# ---------------------------------------------------------------------
# Observer pattern
# ---------------------------------------------------------------------

def test_location_subject_notifies_all_observers():
    tour = TourFactory.create_tour(SAMPLE_TOUR_SPEC)
    visitor = VisitorFactory.create_visitor("V-1", "Test")
    subject = LocationSubject()

    received = []
    badge_observer = BadgeObserver(visitor, tour)
    content_observer = ContentTriggerObserver(tour, on_deliver=lambda v, s, m: received.append(m))

    subject.subscribe(badge_observer)
    subject.subscribe(content_observer)
    subject.notify(visitor.visitor_id, tour.stops[0].location_id)

    assert visitor.points == 10
    assert len(received) == 1


def test_badge_observer_awards_completion_badge():
    tour = TourFactory.create_tour(SAMPLE_TOUR_SPEC)
    visitor = VisitorFactory.create_visitor("V-1", "Test")
    subject = LocationSubject()
    subject.subscribe(BadgeObserver(visitor, tour))

    for stop in tour.stops:
        subject.notify(visitor.visitor_id, stop.location_id)

    assert any("Completed" in badge for badge in visitor.badges)


# ---------------------------------------------------------------------
# State pattern
# ---------------------------------------------------------------------

def test_exploring_state_transitions_to_at_stop():
    tour = TourFactory.create_tour(SAMPLE_TOUR_SPEC)
    visitor = VisitorFactory.create_visitor("V-1", "Test")
    ExploringState().enter(visitor)

    new_state = visitor.state.handle_arrival(visitor, tour.stops[0].location_id, tour)
    assert isinstance(new_state, AtStopState)


def test_at_stop_state_returns_to_exploring_when_no_stop():
    tour = TourFactory.create_tour(SAMPLE_TOUR_SPEC)
    visitor = VisitorFactory.create_visitor("V-1", "Test")
    AtStopState().enter(visitor)

    new_state = visitor.state.handle_arrival(visitor, "some-random-hallway", tour)
    assert isinstance(new_state, ExploringState)


# ---------------------------------------------------------------------
# Mediator pattern (integration test tying everything together)
# ---------------------------------------------------------------------

def test_mediator_updates_state_and_notifies_observers():
    tour = TourFactory.create_tour(SAMPLE_TOUR_SPEC)
    visitor = VisitorFactory.create_visitor("V-1", "Test")

    mediator = TourMediator(tour)
    mediator.register_visitor(visitor)
    mediator.add_observer(BadgeObserver(visitor, tour))

    first_stop = tour.stops[0]
    mediator.handle_beacon_signal(visitor.visitor_id, first_stop.location_id)

    assert visitor.state.name == "at_stop"
    assert visitor.points == 10
    assert first_stop.location_id in visitor.visited_locations


# ---------------------------------------------------------------------
# Offline SQLite persistence
# ---------------------------------------------------------------------

def test_offline_store_round_trips_a_tour(tmp_path):
    db_path = tmp_path / "test_tours.db"
    store = OfflineTourStore(db_path=str(db_path))

    original = TourFactory.create_tour(SAMPLE_TOUR_SPEC)
    store.save_tour(original)

    reloaded = store.load_tour(original.tour_id)
    assert reloaded.title == original.title
    assert len(reloaded.stops) == len(original.stops)
    assert [s.location_id for s in reloaded.stops] == [s.location_id for s in original.stops]


def test_offline_store_lists_downloaded_tours(tmp_path):
    db_path = tmp_path / "test_tours2.db"
    store = OfflineTourStore(db_path=str(db_path))
    tour = TourFactory.create_tour(SAMPLE_TOUR_SPEC)
    store.save_tour(tour)
    assert tour.tour_id in store.list_downloaded_tours()


# ---------------------------------------------------------------------
# Extended features: image/model content, social, quiz, analytics
# ---------------------------------------------------------------------

from models.content import ImageGuide, ModelGuide
from models.social import Photo, Comment
from models.quiz import QuizQuestion, Quiz, Collectible
from services.demo_data import TREASURES_TOUR_SPEC, TREASURES_QUIZZES
from services.camera_service import CameraService
from services.analytics import AnalyticsService
from patterns.observer import AnalyticsObserver, QuizObserver


def test_image_guide_presents_itself():
    img = ImageGuide("Vase", "assets/images/vase.jpg", caption="A jar")
    output = img.present_content()
    assert "Vase" in output and "vase.jpg" in output


def test_model_guide_presents_itself():
    model = ModelGuide("Bust", "assets/models/bust.glb")
    output = model.present_content()
    assert "3D Model" in output and "bust.glb" in output


def test_treasures_tour_builds_with_image_and_model_content():
    tour = TourFactory.create_tour(TREASURES_TOUR_SPEC)
    types = {type(stop.content).__name__ for stop in tour.stops}
    assert "ImageGuide" in types
    assert "ModelGuide" in types


def test_visitor_encapsulates_photos_and_comments():
    visitor = VisitorFactory.create_visitor("V-1", "Test")
    photo = Photo("V-1", "T-01", "Vase", "assets/images/vase.jpg")
    comment = Comment("V-1", "T-01", "Lovely!")
    visitor.add_photo(photo)
    visitor.add_comment(comment)
    assert visitor.photos == [photo]
    assert visitor.comments == [comment]
    # returned lists must be copies, not the live internal ones
    visitor.photos.append("hacked")
    assert len(visitor.photos) == 1


def test_camera_service_falls_back_to_simulated_photo(tmp_path):
    camera = CameraService(photos_dir=str(tmp_path))
    photo = camera.capture_photo("V-1", "T-01", "Test Exhibit")
    assert os.path.exists(photo.image_path)
    # No real webcam in the CI/sandbox environment, so this must be simulated.
    assert photo.is_simulated is True


def test_quiz_scores_correct_and_incorrect_answers():
    question = QuizQuestion("2 + 2?", ["3", "4", "5"], correct_index=1)
    quiz = Quiz("Q-1", "T-01", [question], collectible=Collectible("C-1", "Math Badge"))
    assert quiz.score([1]) == Quiz.POINTS_PER_CORRECT_ANSWER
    assert quiz.score([0]) == 0
    assert quiz.is_perfect([1]) is True
    assert quiz.is_perfect([0]) is False


def test_quiz_observer_triggers_on_matching_location():
    triggered = []
    quizzes = {"T-01": TREASURES_QUIZZES["T-01"]}
    observer = QuizObserver(quizzes, on_quiz_triggered=lambda vid, q: triggered.append((vid, q)))
    observer.on_location_update("V-1", "T-01")
    observer.on_location_update("V-1", "T-99")  # no quiz here
    assert len(triggered) == 1
    assert triggered[0][0] == "V-1"


def test_analytics_service_logs_and_reports_popular_stops(tmp_path):
    db_path = tmp_path / "analytics_test.db"
    analytics = AnalyticsService(db_path=str(db_path))
    analytics.log_visit("V-1", "T-001", "B-01")
    analytics.log_visit("V-2", "T-001", "B-01")
    analytics.log_visit("V-1", "T-001", "B-02")

    popular = analytics.popular_stops("T-001")
    assert popular[0] == ("B-01", 2)


def test_analytics_dwell_times_and_route(tmp_path):
    db_path = tmp_path / "analytics_test2.db"
    analytics = AnalyticsService(db_path=str(db_path))
    analytics.log_visit("V-1", "T-001", "B-01")
    analytics.log_visit("V-1", "T-001", "B-02")

    route = analytics.visitor_route("V-1")
    assert route == ["B-01", "B-02"]
    dwell = analytics.dwell_times("V-1")
    assert "B-01" in dwell
    assert dwell["B-01"] >= 0


def test_analytics_observer_logs_via_mediator(tmp_path):
    db_path = tmp_path / "analytics_test3.db"
    analytics = AnalyticsService(db_path=str(db_path))
    tour = TourFactory.create_tour(SAMPLE_TOUR_SPEC)
    visitor = VisitorFactory.create_visitor("V-1", "Test")

    mediator = TourMediator(tour)
    mediator.register_visitor(visitor)
    mediator.add_observer(AnalyticsObserver(analytics, tour.tour_id))

    mediator.handle_beacon_signal(visitor.visitor_id, tour.stops[0].location_id)
    assert analytics.visitor_route(visitor.visitor_id) == [tour.stops[0].location_id]


# ---------------------------------------------------------------------
# New features: translations, tour selection, admin auth, sharing, map trail
# ---------------------------------------------------------------------

from services.admin_auth import AdminAuthService
from services.demo_data import BUILTIN_TOURS, available_tour_summaries
from models.social import build_share_text, Photo, Comment as SocialComment


def test_text_guide_returns_translated_content_when_available():
    content = ContentFactory.create_content(
        "text", title="Hello", body="Hello world",
        translations={"fr": {"title": "Bonjour", "body": "Bonjour le monde"}},
    )
    visitor_en = VisitorFactory.create_visitor("V-1", "Test")
    visitor_fr = VisitorFactory.create_visitor("V-2", "Test", language="fr")
    assert "Hello world" in content.present_content(visitor_en)
    assert "Bonjour le monde" in content.present_content(visitor_fr)


def test_text_guide_falls_back_to_default_for_untranslated_language():
    content = ContentFactory.create_content(
        "text", title="Hello", body="Hello world", translations={"fr": {"body": "Bonjour"}},
    )
    visitor_de = VisitorFactory.create_visitor("V-1", "Test", language="de")
    assert "Hello world" in content.present_content(visitor_de)


def test_image_guide_translates_title_and_caption():
    content = ContentFactory.create_content(
        "image", title="Vase", image_path="x.jpg", caption="A jar",
        translations={"fr": {"title": "Vase", "caption": "Un pot"}},
    )
    visitor_fr = VisitorFactory.create_visitor("V-1", "Test", language="fr")
    assert "Un pot" in content.present_content(visitor_fr)


def test_builtin_tours_registry_has_both_demo_tours():
    assert "T-001" in BUILTIN_TOURS
    assert "T-002" in BUILTIN_TOURS


def test_available_tour_summaries_lists_builtin_tours():
    summaries = available_tour_summaries()
    tour_ids = {s[0] for s in summaries}
    assert "T-001" in tour_ids
    assert "T-002" in tour_ids


def test_admin_auth_rejects_wrong_pin_and_accepts_correct_pin():
    auth = AdminAuthService(pin="1234")
    assert auth.is_unlocked is False
    assert auth.check_pin("0000") is False
    assert auth.is_unlocked is False
    assert auth.check_pin("1234") is True
    assert auth.is_unlocked is True


def test_admin_auth_lock_resets_session():
    auth = AdminAuthService(pin="1234")
    auth.check_pin("1234")
    assert auth.is_unlocked is True
    auth.lock()
    assert auth.is_unlocked is False


def test_build_share_text_includes_photo_and_comment():
    photo = Photo("V-1", "T-01", "Vase", "assets/images/vase.jpg", is_simulated=True)
    comment = SocialComment("V-1", "T-01", "Beautiful!")
    text = build_share_text("Vase", photo=photo, comment=comment)
    assert "Vase" in text
    assert "vase.jpg" in text
    assert "Beautiful!" in text


def test_build_share_text_without_photo_or_comment():
    text = build_share_text("Vase")
    assert "Vase" in text
    assert "shared from the Museum Guided Tour System" in text


def test_floor_plan_generator_creates_file(tmp_path):
    from services import floorplan_generator
    original_dir = floorplan_generator.FLOORPLAN_DIR
    floorplan_generator.FLOORPLAN_DIR = str(tmp_path)
    try:
        positions = {"A": (10, 10), "B": (80, 80)}
        labels = {"A": "Room A", "B": "Room B"}
        path = floorplan_generator.generate_floor_plan(positions, labels, filename="test_plan.png")
        assert os.path.exists(path)
    finally:
        floorplan_generator.FLOORPLAN_DIR = original_dir


def test_quiz_partial_completion_gives_partial_credit_but_no_collectible():
    """Simulates a visitor quitting a 5-question quiz after answering 2,
    both correctly — they should still get credit for those 2, but the
    collectible (which requires a full perfect score) must NOT unlock."""
    quiz = TREASURES_QUIZZES["T-01"]
    partial_answers = [quiz.questions[0].correct_index, quiz.questions[1].correct_index]
    assert quiz.score(partial_answers) == 2 * Quiz.POINTS_PER_CORRECT_ANSWER
    assert quiz.is_perfect(partial_answers) is False


def test_all_treasures_quizzes_have_five_questions():
    for location_id, quiz in TREASURES_QUIZZES.items():
        assert len(quiz.questions) == 5, f"{location_id} quiz should have 5 questions"


def test_quiz_mixed_correct_and_wrong_answers_scores_only_correct_ones():
    quiz = TREASURES_QUIZZES["T-03"]
    # Deliberately get every answer wrong by picking a different index.
    wrong_answers = [
        (q.correct_index + 1) % len(q.choices) for q in quiz.questions
    ]
    assert quiz.score(wrong_answers) == 0
    assert quiz.is_perfect(wrong_answers) is False


# ---------------------------------------------------------------------
# Real audio, video, and 3D content
# ---------------------------------------------------------------------

from models.content import AudioGuide, VideoGuide, ModelGuide
from services.demo_data import SAMPLE_TOUR_SPEC


def test_audio_guide_reports_real_audio_path_when_present():
    guide = AudioGuide("Welcome", 16, "Ama", script="Hello.", audio_path="assets/audio/welcome.wav")
    output = guide.present_content()
    assert "assets/audio/welcome.wav" in output


def test_audio_guide_without_audio_path_has_no_file_reference():
    guide = AudioGuide("Welcome", 16, "Ama")
    assert guide.audio_path is None
    assert "assets/audio" not in guide.present_content()


def test_sample_tour_audio_stops_have_real_generated_audio_files():
    tour = TourFactory.create_tour(SAMPLE_TOUR_SPEC)
    audio_stops = [s for s in tour.stops if isinstance(s.content, AudioGuide)]
    assert len(audio_stops) == 2
    for stop in audio_stops:
        assert stop.content.audio_path is not None
        full_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), stop.content.audio_path
        )
        assert os.path.exists(full_path), f"missing generated audio file: {full_path}"


def test_video_guide_reports_frames_dir_when_present():
    guide = VideoGuide("Clip", 10, frames_dir="assets/video_frames/x", frame_count=20)
    output = guide.present_content()
    assert "assets/video_frames/x" in output
    assert "20 frames" in output


def test_sample_tour_video_stop_has_real_generated_frames():
    tour = TourFactory.create_tour(SAMPLE_TOUR_SPEC)
    video_stops = [s for s in tour.stops if isinstance(s.content, VideoGuide)]
    assert len(video_stops) == 1
    content = video_stops[0].content
    assert content.frames_dir is not None
    full_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), content.frames_dir
    )
    frame_files = [f for f in os.listdir(full_dir) if f.startswith("frame_")]
    assert len(frame_files) == content.frame_count


def test_model_guide_defaults_to_vase_shape():
    guide = ModelGuide("Vase Scan", "assets/models/x.glb")
    assert guide.shape == "vase"
    assert "vase" in guide.present_content()


def test_model3d_widget_ring_geometry_is_pure_and_importable():
    from services.model3d_geometry import build_rings, VASE_PROFILE
    rings = build_rings(VASE_PROFILE, segments=12)
    assert len(rings) == len(VASE_PROFILE)
    assert all(len(ring) == 12 for ring in rings)
    # Every point should be a real 3D coordinate.
    for ring in rings:
        for x, y, z in ring:
            assert isinstance(x, float) and isinstance(y, float) and isinstance(z, float)


def test_model3d_projection_is_deterministic_pure_math():
    from services.model3d_geometry import project_point
    point = (0.5, 0.3, 0.2)
    result1 = project_point(point, angle_y=0.4, angle_x=0.15, center_x=100, base_y=0, width=200, height=200)
    result2 = project_point(point, angle_y=0.4, angle_x=0.15, center_x=100, base_y=0, width=200, height=200)
    assert result1 == result2
    x, y, z = result1
    assert isinstance(x, float) and isinstance(y, float) and isinstance(z, float)


def test_video_generator_produces_requested_frame_count(tmp_path):
    from services.video_generator import generate_cubism_style_artwork, generate_video_frames
    artwork = str(tmp_path / "art.jpg")
    generate_cubism_style_artwork(artwork)
    assert os.path.exists(artwork)

    import services.video_generator as vg
    original_root = vg.FRAMES_ROOT
    vg.FRAMES_ROOT = str(tmp_path / "frames")
    try:
        frames_dir, count = generate_video_frames(artwork, "test_stop", caption="Test", num_frames=6)
        assert count == 6
        assert len(os.listdir(frames_dir)) == 6
    finally:
        vg.FRAMES_ROOT = original_root


def test_audio_generator_reuses_existing_file(tmp_path):
    from services import audio_generator as ag
    original_dir = ag.AUDIO_DIR
    ag.AUDIO_DIR = str(tmp_path)
    try:
        if not ag.espeak_available():
            import pytest as _pytest
            _pytest.skip("espeak-ng not available in this environment")
        path1 = ag.generate_narration_audio("Hello there.", "greet.wav")
        assert os.path.exists(path1)
        mtime1 = os.path.getmtime(path1)
        path2 = ag.generate_narration_audio("Different text entirely.", "greet.wav")
        # Same filename -> cached file reused, not regenerated.
        assert path1 == path2
        assert os.path.getmtime(path2) == mtime1
    finally:
        ag.AUDIO_DIR = original_dir
