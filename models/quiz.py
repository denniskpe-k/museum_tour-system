"""
models/quiz.py

Quiz and Collectible models for the gamification requirement (beyond
the points/badges already in Visitor). A Quiz is attached to a tour
stop; answering it correctly awards bonus points and can unlock a
Collectible (a themed digital souvenir tied to that exhibit).
"""

from typing import List, Optional


class QuizQuestion:
    """A single multiple-choice question."""

    def __init__(self, prompt: str, choices: List[str], correct_index: int):
        if not (0 <= correct_index < len(choices)):
            raise ValueError("correct_index out of range for choices")
        self.prompt = prompt
        self.choices = choices
        self.correct_index = correct_index

    def is_correct(self, chosen_index: int) -> bool:
        return chosen_index == self.correct_index


class Collectible:
    """A themed digital souvenir awarded for completing a stop's quiz."""

    def __init__(self, collectible_id: str, name: str, description: str = ""):
        self.collectible_id = collectible_id
        self.name = name
        self.description = description

    def __repr__(self) -> str:
        return f"Collectible({self.name!r})"


class Quiz:
    """
    A short quiz attached to a tour stop. Scoring a quiz awards points
    and, on a perfect score, unlocks the attached Collectible (if any).
    """

    POINTS_PER_CORRECT_ANSWER = 5

    def __init__(self, quiz_id: str, location_id: str, questions: List[QuizQuestion],
                 collectible: Optional[Collectible] = None):
        self.quiz_id = quiz_id
        self.location_id = location_id
        self.questions = questions
        self.collectible = collectible

    def score(self, answers: List[int]) -> int:
        """Given a list of chosen indices (one per question), return points earned."""
        correct = sum(
            1 for question, answer in zip(self.questions, answers)
            if question.is_correct(answer)
        )
        return correct * self.POINTS_PER_CORRECT_ANSWER

    def is_perfect(self, answers: List[int]) -> bool:
        return len(answers) == len(self.questions) and all(
            q.is_correct(a) for q, a in zip(self.questions, answers)
        )
