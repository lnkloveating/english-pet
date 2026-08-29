import pytest

from shengsheng_agent.learning.grade_policy import get_grade_policy
from shengsheng_agent.prompts.prompt_builder import build_prompt


@pytest.mark.parametrize("grade", range(1, 7))
def test_all_primary_school_grades_have_a_policy(grade: int) -> None:
    policy = get_grade_policy(grade)

    assert policy.grade == grade
    assert policy.target_wpm > 0
    assert policy.max_sentence_words > 0
    assert policy.topics


@pytest.mark.parametrize("grade", [0, 7, -1])
def test_invalid_grade_is_rejected(grade: int) -> None:
    with pytest.raises(ValueError, match="between 1 and 6"):
        get_grade_policy(grade)


def test_grade_one_is_simpler_and_slower_than_grade_six() -> None:
    grade_one = get_grade_policy(1)
    grade_six = get_grade_policy(6)

    assert grade_one.target_wpm < grade_six.target_wpm
    assert grade_one.max_sentence_words < grade_six.max_sentence_words
    assert grade_one.vocabulary_level == "Pre-A1"
    assert grade_six.vocabulary_level == "A2 beginner"


def test_prompt_contains_shared_child_safety_and_teaching_rules() -> None:
    prompt = build_prompt(3)

    assert "Ask at most one" in prompt.system_role
    assert "naturally repeat the correct expression" in prompt.system_role
    assert "Never say that the child is wrong" in prompt.system_role
    assert "Never ask for the child's full name" in prompt.system_role


def test_prompt_uses_grade_specific_limits() -> None:
    grade_one = build_prompt(1)
    grade_six = build_prompt(6)

    assert "no more than 6 words" in grade_one.system_role
    assert "about 70 words per minute" in grade_one.speaking_style
    assert "no more than 18 words" in grade_six.system_role
    assert "about 120 words per minute" in grade_six.speaking_style


def test_character_manifest_combines_both_prompt_sections() -> None:
    prompt = build_prompt(2, pet_name="Lumi")

    assert "You are Lumi" in prompt.character_manifest
    assert prompt.system_role in prompt.character_manifest
    assert prompt.speaking_style in prompt.character_manifest
