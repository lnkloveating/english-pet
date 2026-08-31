import gzip
import json
import struct

import pytest

from shengsheng_agent.asr.protocol import (
    DoubaoProtocolError,
    decode_server_packet,
    encode_audio_chunk,
    encode_client_config,
    transcript_from_packet,
)
from shengsheng_agent.asr.providers import DoubaoStreamingAsrProvider


def test_client_config_uses_json_and_gzip() -> None:
    frame = encode_client_config({"request": {"model_name": "bigmodel"}})

    assert frame[:4] == bytes([0x11, 0x10, 0x11, 0x00])
    payload_size = struct.unpack_from(">I", frame, 4)[0]
    payload = json.loads(gzip.decompress(frame[8 : 8 + payload_size]))
    assert payload["request"]["model_name"] == "bigmodel"


def test_last_audio_chunk_sets_last_packet_flag() -> None:
    frame = encode_audio_chunk(b"pcm", is_last=True)

    assert frame[:4] == bytes([0x11, 0x22, 0x01, 0x00])
    assert gzip.decompress(frame[8:]) == b"pcm"


def test_server_response_parses_optional_sequence_and_final_utterance() -> None:
    response = {
        "result": {
            "text": "I like cats.",
            "utterances": [{"text": "I like cats.", "definite": True}],
            "language": "en",
        }
    }
    compressed = gzip.compress(json.dumps(response).encode())
    frame = (
        bytes([0x11, 0x91, 0x11, 0x00])
        + struct.pack(">i", 3)
        + struct.pack(">I", len(compressed))
        + compressed
    )

    packet = decode_server_packet(frame)

    assert packet.sequence == 3
    assert transcript_from_packet(packet) == ("I like cats.", True, None, "en")


def test_server_error_does_not_require_json() -> None:
    message = b"requested resource not granted"
    frame = bytes([0x11, 0xF0, 0x00, 0x00]) + struct.pack(">II", 403, len(message)) + message

    with pytest.raises(DoubaoProtocolError) as error:
        decode_server_packet(frame)

    assert error.value.code == 403


def test_new_console_api_key_header() -> None:
    provider = DoubaoStreamingAsrProvider(
        api_key="secret",
        app_key=None,
        access_token=None,
        resource_id="volc.seedasr.sauc.duration",
        websocket_url="wss://example.test/asr",
    )

    headers = provider._headers("request-id")

    assert headers["X-Api-Key"] == "secret"
    assert "X-Api-App-Key" not in headers
    assert headers["X-Api-Resource-Id"] == "volc.seedasr.sauc.duration"


def test_legacy_app_and_access_key_headers() -> None:
    provider = DoubaoStreamingAsrProvider(
        api_key=None,
        app_key="app-key",
        access_token="access-token",
        resource_id="volc.seedasr.sauc.duration",
        websocket_url="wss://example.test/asr",
    )

    headers = provider._headers("request-id")

    assert headers["X-Api-App-Key"] == "app-key"
    assert headers["X-Api-Access-Key"] == "access-token"
    assert "X-Api-Key" not in headers
