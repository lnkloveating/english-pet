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
