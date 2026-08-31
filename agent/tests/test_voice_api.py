from fastapi.testclient import TestClient

from shengsheng_agent.asr import StubStreamingAsrProvider
from shengsheng_agent.main import create_app


def session_start() -> dict[str, object]:
    return {
        "type": "session.start",
        "session_id": "voice_session",
        "child_id": "child_demo",
        "learner_profile": {
            "grade": 3,
            "level": 2,
            "confidence": 0.5,
            "target_sentence_words": 5,
            "interests": [],
            "recent_topics": [],
        },
        "audio": {"format": "pcm", "sample_rate": 16000, "bits": 16, "channels": 1},
        "context": [],
    }


def test_voice_websocket_transcribes_and_runs_agent_turn() -> None:
    app = create_app(asr_provider=StubStreamingAsrProvider("I like cats."))
    client = TestClient(app)

    with client.websocket_connect("/v1/agent/voice") as websocket:
        websocket.send_json(session_start())
        assert websocket.receive_json()["type"] == "session.ready"

        websocket.send_json({"type": "input.start"})
        assert websocket.receive_json() == {"type": "input.ready"}
        websocket.send_bytes(b"\x00\x01" * 1600)
        websocket.send_json({"type": "input.commit"})

        events = [websocket.receive_json() for _ in range(4)]

    assert [event["type"] for event in events] == [
        "asr.partial",
        "asr.final",
        "agent.reply",
        "turn.completed",
    ]
    assert events[1]["text"] == "I like cats."
    assert events[2]["transcript"] == "I like cats."
    assert events[2]["turn"]["learner_profile"]["grade"] == 3


def test_voice_websocket_requires_session_start() -> None:
    app = create_app(asr_provider=StubStreamingAsrProvider())
    client = TestClient(app)

    with client.websocket_connect("/v1/agent/voice") as websocket:
        websocket.send_json({"type": "input.start"})
        event = websocket.receive_json()

    assert event["type"] == "error"
    assert event["error"]["code"] == "session_not_started"


def test_voice_websocket_rejects_audio_before_input_start() -> None:
    app = create_app(asr_provider=StubStreamingAsrProvider())
    client = TestClient(app)

    with client.websocket_connect("/v1/agent/voice") as websocket:
        websocket.send_json(session_start())
        assert websocket.receive_json()["type"] == "session.ready"
        websocket.send_bytes(b"audio")
        event = websocket.receive_json()

    assert event["type"] == "error"
    assert event["error"]["code"] == "turn_not_started"


def test_voice_websocket_rejects_non_contract_sample_rate() -> None:
    app = create_app(asr_provider=StubStreamingAsrProvider())
    client = TestClient(app)
    payload = session_start()
    payload["audio"] = {"format": "pcm", "sample_rate": 44100, "bits": 16, "channels": 1}

    with client.websocket_connect("/v1/agent/voice") as websocket:
        websocket.send_json(payload)
        event = websocket.receive_json()

    assert event["type"] == "error"
    assert event["error"]["code"] == "invalid_control"
