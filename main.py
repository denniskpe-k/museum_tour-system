"""
main.py

Entry point for the Museum Guided Tour System.

Run modes:
  python main.py              -> launches the Kivy tablet UI (default; needs `kivy`)
  python main.py --console    -> original text-based console demo (no Kivy needed)
  python main.py --extended   -> extended text demo: images, quizzes, social, analytics

The console demos exercise the exact same domain/pattern code the
Kivy UI uses, so they double as a quick sanity check that everything
(Factory, Strategy, Observer, State, Mediator, the offline SQLite
store, and the mock beacon/GPS simulators) works together end to end
without needing a graphical display.
"""

import os
import sys

from patterns.factory import TourFactory, VisitorFactory
from patterns.mediator import TourMediator
from patterns.observer import (
    ContentTriggerObserver, BadgeObserver, AnalyticsObserver, QuizObserver,
)
from patterns.strategy import SequentialStrategy, PersonalizedStrategy
from services.location_simulator import BeaconSimulator, GPSSimulator
from services.database import OfflineTourStore
from services.analytics import AnalyticsService
from services.camera_service import CameraService
from services.demo_data import (
    SAMPLE_TOUR_SPEC, GPS_KNOWN_POINTS, TREASURES_TOUR_SPEC, ALL_QUIZZES,
)
from models.social import Comment


def run_console_demo() -> None:
    print("=== Museum Guided Tour System (console demo) ===\n")

    # Factory pattern: build the tour and a visitor.
    tour = TourFactory.create_tour(SAMPLE_TOUR_SPEC)
    visitor = VisitorFactory.create_visitor(
        "V-001", "Kojo", needs_audio_description=True
    )
    print(f"Loaded {tour} for visitor {visitor}\n")

    # Offline mode: "download" the tour into local SQLite, then reload
    # it back out to prove it survives without any network connection.
    store = OfflineTourStore(db_path="museum_tours.db")
    store.save_tour(tour)
    tour = store.load_tour(tour.tour_id)
    print("Tour re-loaded from the offline SQLite cache.\n")

    # Mediator + Observer + State wiring.
    mediator = TourMediator(tour)
    mediator.register_visitor(visitor)
    mediator.add_observer(ContentTriggerObserver(tour, on_deliver=_print_delivery))
    mediator.add_observer(BadgeObserver(visitor, tour))

    # Simulated beacon walk through the indoor stops.
    beacon_sim = BeaconSimulator(mediator)
    beacon_sim.walk_route(visitor.visitor_id, ["B-01", "B-02"])

    # Simulated GPS fix for the outdoor sculpture garden stop.
    gps_sim = GPSSimulator(mediator, known_points=GPS_KNOWN_POINTS)
    gps_sim.emit_random_position(visitor.visitor_id)

    beacon_sim.walk_route(visitor.visitor_id, ["B-03"])

    print(f"\nFinal state: {visitor.state.name}")
    print(f"Points earned: {visitor.points}")
    print(f"Badges: {visitor.badges}")

    # Strategy pattern in action: ask two different strategies what a
    # visitor who hasn't moved yet should do next.
    fresh_visitor = VisitorFactory.create_visitor("V-002", "Ama")
    print("\nRecommendations for a brand-new visitor:")
    print(" Sequential ->", SequentialStrategy().recommend_next_stop(tour, fresh_visitor))
    print(" Personalized ->", PersonalizedStrategy().recommend_next_stop(tour, fresh_visitor))


def _print_delivery(visitor_id, stop, message) -> None:
    print(f"  -> {message}")


def run_extended_demo() -> None:
    """
    Demonstrates the extended requirements: images/3D models, an
    interactive-map-ready floor plan, quizzes/collectibles, social
    features (simulated photo capture + comments), and visitor
    analytics (dwell time, popular stops, route comparison).
    """
    print("=== Museum Guided Tour System (extended demo) ===\n")

    tour = TourFactory.create_tour(TREASURES_TOUR_SPEC)
    visitor = VisitorFactory.create_visitor("V-201", "Abena")
    print(f"Loaded {tour}\n")

    analytics = AnalyticsService(db_path="museum_tours.db")
    camera = CameraService()

    mediator = TourMediator(tour)
    mediator.register_visitor(visitor)
    mediator.add_observer(ContentTriggerObserver(tour, on_deliver=_print_delivery))
    mediator.add_observer(BadgeObserver(visitor, tour))
    mediator.add_observer(AnalyticsObserver(analytics, tour.tour_id))

    def on_quiz(visitor_id, quiz):
        # Console demo walks through every question, printing whether
        # each answer is correct or wrong, then a final score summary —
        # mirroring the GUI's quiz flow. Answers correctly here to also
        # demonstrate the collectible-unlock reward path.
        print(f"  [Quiz] {len(quiz.questions)} questions at this stop:")
        answers = []
        for i, question in enumerate(quiz.questions, start=1):
            chosen = question.correct_index  # auto-answer correctly for the demo
            answers.append(chosen)
            result = "Correct!" if question.is_correct(chosen) else (
                f"Wrong. Correct answer: {question.choices[question.correct_index]}"
            )
            print(f"    Q{i}: {question.prompt}")
            print(f"        -> {question.choices[chosen]}  [{result}]")

        correct_count = sum(1 for q, a in zip(quiz.questions, answers) if q.is_correct(a))
        points = quiz.score(answers)
        visitor.award_points(points)
        unlocked = quiz.is_perfect(answers) and quiz.collectible is not None
        if unlocked:
            visitor.award_collectible(quiz.collectible)
        print(f"  [Quiz] Final score: {correct_count}/{len(quiz.questions)} correct, "
              f"+{points} points, "
              f"collectible: {quiz.collectible.name if unlocked else 'none'}")

    mediator.add_observer(QuizObserver(ALL_QUIZZES, on_quiz_triggered=on_quiz))

    beacon_sim = BeaconSimulator(mediator, delay_seconds=0.01)
    beacon_sim.walk_route(visitor.visitor_id, [s.location_id for s in tour.stops])

    # Social features: simulated photo capture (no webcam in this sandbox)
    # and a comment, both attached to the visitor.
    photo = camera.capture_photo(visitor.visitor_id, tour.stops[0].location_id, tour.stops[0].content.title)
    visitor.add_photo(photo)
    visitor.add_comment(Comment(visitor.visitor_id, tour.stops[0].location_id, "Beautiful piece!"))
    print(f"\nPhoto captured: {photo}")
    print(f"Comments posted: {visitor.comments}")

    print(f"\nFinal points: {visitor.points}")
    print(f"Badges: {visitor.badges}")
    print(f"Collectibles: {[c.name for c in visitor.collectibles]}")

    # Visitor analytics.
    print("\n-- Analytics --")
    print("Dwell time per stop (seconds):", analytics.dwell_times(visitor.visitor_id))
    print("Popular stops for this tour:", analytics.popular_stops(tour.tour_id))
    comparison = analytics.compare_route_to_recommendation(visitor, tour, PersonalizedStrategy())
    print("Actual route:     ", comparison["actual"])
    print("Recommended route:", comparison["recommended"])


if __name__ == "__main__":
    if "--console" in sys.argv:
        run_console_demo()
    elif "--extended" in sys.argv:
        run_extended_demo()
    else:
        # Default (no flags, or explicit --gui): launch the graphical UI.
        os.environ["KIVY_NO_ARGS"] = "1"
        from ui.app import MuseumTourApp

        MuseumTourApp().run()
