from fastapi.testclient import TestClient
from shengsheng_contracts import (
    AgentTurnResponse,
    LearnerProfile,
    RewardDecision,
    SafetyResult,
)

from shengsheng_app_api import main
from shengsheng_app_api.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "app-api"}


def test_session_path_is_source_of_truth(monkeypatch) -> None:
    async def fake_turn(request):
        assert request.session_id == "path_session"
        return AgentTurnResponse(
            turn_id="turn_test",
            reply_text="I hear you! Do you like it?",
            teaching_action="encourage",
            reward=RewardDecision(
                valid_speaking_attempt=True,
                base_voice_fruit=1,
                bonus_voice_fruit=0,
                reasons=["meaningful_english_attempt"],
            ),
            learner_profile=LearnerProfile(),
            safety=SafetyResult(action="allow", reason_code="none"),
        )

    monkeypatch.setattr(main.service_client, "create_agent_turn", fake_turn)
    response = client.post(
        "/v1/sessions/path_session/turns",
        json={
            "session_id": "body_session",
            "child_id": "child_test",
            "transcript": "Cat.",
            "learner_profile": {
                "level": 1,
                "confidence": 0.5,
                "target_sentence_words": 4,
            },
        },
    )
    assert response.status_code == 200
    assert response.json()["reward"]["base_voice_fruit"] == 1
