from shengsheng_contracts import AgentTurnRequest, AudioMetadata, LearnerProfile

from shengsheng_agent.policies import CorrectionPolicy, RewardPolicy, SafetyPolicy


def request_for(text: str) -> AgentTurnRequest:
    return AgentTurnRequest(
        session_id="session_test",
        child_id="child_test",
        transcript=text,
        learner_profile=LearnerProfile(level=2, confidence=0.5, target_sentence_words=4),
        audio_metadata=AudioMetadata(detected_language="en", is_human_voice=True),
    )


def test_any_meaningful_english_attempt_gets_base_reward() -> None:
    reward = RewardPolicy().evaluate(request_for("Cat."))
    assert reward.valid_speaking_attempt is True
    assert reward.base_voice_fruit == 1


def test_pronunciation_confidence_does_not_cancel_base_reward() -> None:
    request = request_for("I like cats.")
    request.audio_metadata.asr_confidence = 0.25
    reward = RewardPolicy().evaluate(request)
    assert reward.base_voice_fruit == 1


def test_recast_is_implicit() -> None:
    assert CorrectionPolicy().recast("Yesterday I go to park") == "Yesterday I went to park."


def test_high_risk_content_routes_to_adult() -> None:
    result = SafetyPolicy().evaluate("I want to hurt myself")
    assert result.action == "trusted_adult"
