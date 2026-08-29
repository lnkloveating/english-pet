from dataclasses import dataclass


@dataclass(frozen=True)
class GradePolicy:
    """Conversation defaults for one primary-school grade.

    These values are product targets used to build the realtime model prompt.
    They are not measurements reported by the speech provider.
    """

    grade: int
    target_wpm: int
    max_sentence_words: int
    vocabulary_level: str
    question_type: str
    topics: tuple[str, ...]


GRADE_POLICIES: dict[int, GradePolicy] = {
    1: GradePolicy(
        grade=1,
        target_wpm=70,
        max_sentence_words=6,
        vocabulary_level="Pre-A1",
        question_type="yes/no or simple choice",
        topics=("colors", "numbers", "animals", "toys"),
    ),
    2: GradePolicy(
        grade=2,
        target_wpm=80,
        max_sentence_words=8,
        vocabulary_level="Pre-A1",
        question_type="simple choice",
        topics=("family", "food", "school", "simple actions"),
    ),
    3: GradePolicy(
        grade=3,
        target_wpm=90,
        max_sentence_words=10,
        vocabulary_level="A1 beginner",
        question_type="simple who, what, or where",
        topics=("daily routines", "hobbies", "friends", "places"),
    ),
    4: GradePolicy(
        grade=4,
        target_wpm=100,
        max_sentence_words=12,
        vocabulary_level="A1",
        question_type="simple open",
        topics=("experiences", "weekends", "stories", "reasons"),
    ),
    5: GradePolicy(
        grade=5,
        target_wpm=110,
        max_sentence_words=15,
        vocabulary_level="A1+",
        question_type="simple opinion or comparison",
        topics=("opinions", "comparisons", "plans", "short stories"),
    ),
    6: GradePolicy(
        grade=6,
        target_wpm=120,
        max_sentence_words=18,
        vocabulary_level="A2 beginner",
        question_type="simple reason, plan, or opinion",
        topics=("reasons", "future plans", "choices", "simple discussions"),
    ),
}


def get_grade_policy(grade: int) -> GradePolicy:
    """Return the configured policy for grades 1-6."""

    try:
        return GRADE_POLICIES[grade]
    except KeyError as exc:
        raise ValueError("grade must be between 1 and 6") from exc
