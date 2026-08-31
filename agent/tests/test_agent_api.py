import pytest
from fastapi.testclient import TestClient

from shengsheng_agent.main import app

client = TestClient(app)


def test_agent_turn_contract() -> None:
    response = client.post(
        "/v1/agent/turn",
        json={
            "session_id": "session_demo",
            "child_id": "child_demo",
            "transcript": "Yesterday I go to park.",
            "learner_profile": {
                "level": 2,
                "confidence": 0.5,
                "target_sentence_words": 5,
                "interests": [],
                "recent_topics": [],
            },
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["teaching_action"] == "recast"
    assert body["reward"]["base_voice_fruit"] == 1
    assert body["learner_profile"]["grade"] == 1


@pytest.mark.parametrize("grade", [1, 6])
def test_agent_turn_accepts_primary_school_grades(grade: int) -> None:
    response = client.post(
        "/v1/agent/turn",
        json={
            "session_id": "session_grade",
            "child_id": "child_demo",
            "transcript": "I like cats.",
            "learner_profile": {
                "grade": grade,
                "level": 2,
                "confidence": 0.5,
                "target_sentence_words": 5,
                "interests": [],
                "recent_topics": [],
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["learner_profile"]["grade"] == grade


def test_agent_reply_changes_for_younger_and_older_grades() -> None:
    def post_turn(grade: int):
        return client.post(
            "/v1/agent/turn",
            json={
                "session_id": f"session_grade_{grade}",
                "child_id": "child_demo",
                "transcript": "I like cats.",
                "learner_profile": {
                    "grade": grade,
                    "level": 2,
                    "confidence": 0.5,
                    "target_sentence_words": 5,
                    "interests": [],
                    "recent_topics": [],
                },
            },
        )

    grade_one = post_turn(1)
    grade_six = post_turn(6)

    assert grade_one.status_code == 200
    assert grade_six.status_code == 200
    assert grade_one.json()["reply_text"].endswith("Do you like it?")
    assert grade_six.json()["reply_text"].endswith("Why do you think so?")


@pytest.mark.parametrize("grade", [0, 7])
def test_agent_turn_rejects_invalid_grades(grade: int) -> None:
    response = client.post(
        "/v1/agent/turn",
        json={
            "session_id": "session_invalid_grade",
            "child_id": "child_demo",
            "transcript": "Cat.",
            "learner_profile": {
                "grade": grade,
                "level": 2,
                "confidence": 0.5,
                "target_sentence_words": 5,
                "interests": [],
                "recent_topics": [],
            },
        },
    )

    assert response.status_code == 422
