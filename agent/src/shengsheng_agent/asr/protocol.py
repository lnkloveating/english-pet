import gzip
import json
import struct
from dataclasses import dataclass
from typing import Any

FULL_CLIENT_REQUEST = 0x1
AUDIO_ONLY_REQUEST = 0x2
FULL_SERVER_RESPONSE = 0x9
SERVER_ACK = 0xB
SERVER_ERROR_RESPONSE = 0xF

JSON_SERIALIZATION = 0x1
GZIP_COMPRESSION = 0x1
LAST_PACKET_FLAG = 0x2
SEQUENCE_FLAG = 0x1


class DoubaoProtocolError(RuntimeError):
    def __init__(self, message: str, *, code: int | None = None) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class ServerPacket:
    message_type: int
    flags: int
    payload: dict[str, Any] | bytes | None
    is_last: bool
    sequence: int | None = None


def _header(message_type: int, flags: int, serialization: int, compression: int) -> bytes:
    return bytes(
        [
            0x11,
            ((message_type & 0xF) << 4) | (flags & 0xF),
            ((serialization & 0xF) << 4) | (compression & 0xF),
            0x00,
        ]
    )


def _packet(header: bytes, payload: bytes) -> bytes:
    return header + struct.pack(">I", len(payload)) + payload


def encode_client_config(payload: dict[str, Any]) -> bytes:
    compressed = gzip.compress(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    return _packet(
        _header(FULL_CLIENT_REQUEST, 0, JSON_SERIALIZATION, GZIP_COMPRESSION),
        compressed,
    )


def encode_audio_chunk(audio: bytes, *, is_last: bool = False) -> bytes:
    compressed = gzip.compress(audio)
    flags = LAST_PACKET_FLAG if is_last else 0
    return _packet(
        _header(AUDIO_ONLY_REQUEST, flags, 0, GZIP_COMPRESSION),
        compressed,
    )


def decode_server_packet(frame: bytes) -> ServerPacket:
    if len(frame) < 4:
        raise DoubaoProtocolError("ASR response header is incomplete")

    header_size = (frame[0] & 0x0F) * 4
    if header_size < 4 or len(frame) < header_size:
        raise DoubaoProtocolError("ASR response header size is invalid")

    message_type = frame[1] >> 4
    flags = frame[1] & 0x0F
    serialization = frame[2] >> 4
    compression = frame[2] & 0x0F
    offset = header_size

    if message_type == SERVER_ERROR_RESPONSE:
        if len(frame) < offset + 8:
            raise DoubaoProtocolError("ASR error response is incomplete")
        code = struct.unpack_from(">I", frame, offset)[0]
        payload_size = struct.unpack_from(">I", frame, offset + 4)[0]
        raw_message = frame[offset + 8 : offset + 8 + payload_size]
        message = raw_message.decode("utf-8", errors="replace")
        try:
            decoded = json.loads(message)
            message = decoded.get("message") or decoded.get("error") or message
        except json.JSONDecodeError:
            pass
        raise DoubaoProtocolError(str(message), code=code)

    sequence = None
    if flags & SEQUENCE_FLAG:
        if len(frame) < offset + 4:
            raise DoubaoProtocolError("ASR response sequence is incomplete")
        sequence = struct.unpack_from(">i", frame, offset)[0]
        offset += 4

    if message_type == SERVER_ACK and len(frame) == offset:
        return ServerPacket(message_type, flags, None, bool(flags & LAST_PACKET_FLAG), sequence)

    if len(frame) < offset + 4:
        raise DoubaoProtocolError("ASR response payload size is missing")
    payload_size = struct.unpack_from(">I", frame, offset)[0]
    offset += 4
    if len(frame) < offset + payload_size:
        raise DoubaoProtocolError("ASR response payload is incomplete")

    raw_payload = frame[offset : offset + payload_size]
    if compression == GZIP_COMPRESSION:
        try:
            raw_payload = gzip.decompress(raw_payload)
        except gzip.BadGzipFile as exc:
            raise DoubaoProtocolError("ASR response gzip payload is invalid") from exc

    payload: dict[str, Any] | bytes | None = raw_payload
    if serialization == JSON_SERIALIZATION and raw_payload:
        try:
            decoded_payload = json.loads(raw_payload)
        except json.JSONDecodeError as exc:
            raise DoubaoProtocolError("ASR response JSON is invalid") from exc
        if not isinstance(decoded_payload, dict):
            raise DoubaoProtocolError("ASR response JSON must be an object")
        payload = decoded_payload
    elif not raw_payload:
        payload = None

    return ServerPacket(
        message_type=message_type,
        flags=flags,
        payload=payload,
        is_last=bool(flags & LAST_PACKET_FLAG) or (sequence is not None and sequence < 0),
        sequence=sequence,
    )


def transcript_from_packet(packet: ServerPacket) -> tuple[str, bool, float | None, str | None] | None:
    if packet.message_type != FULL_SERVER_RESPONSE or not isinstance(packet.payload, dict):
        return None

    result = packet.payload.get("result")
    if not isinstance(result, dict):
        return None
    text = result.get("text")
    if not isinstance(text, str) or not text.strip():
        return None

    utterances = result.get("utterances")
    utterance_final = False
    if isinstance(utterances, list) and utterances:
        last_utterance = utterances[-1]
        if isinstance(last_utterance, dict):
            utterance_final = bool(last_utterance.get("definite"))

    confidence = result.get("confidence")
    normalized_confidence = float(confidence) if isinstance(confidence, (int, float)) else None
    language = result.get("language")
    normalized_language = language if isinstance(language, str) else None
    return text.strip(), packet.is_last or utterance_final, normalized_confidence, normalized_language
