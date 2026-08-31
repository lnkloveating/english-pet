import asyncio
import json
import logging
from collections.abc import AsyncIterator
from typing import Literal

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from shengsheng_contracts import AgentTurnRequest, AudioMetadata, LearnerProfile

from .asr import AsrAudioConfig, AsrProviderError, StreamingAsrProvider
from .service import AgentService

logger = logging.getLogger(__name__)


class VoiceMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")


class VoiceAudioConfig(VoiceMessage):
    format: Literal["pcm"] = "pcm"
    sample_rate: Literal[16000] = 16000
    bits: Literal[16] = 16
    channels: Literal[1] = 1

    def to_asr_config(self) -> AsrAudioConfig:
        return AsrAudioConfig(
            format=self.format,
            sample_rate=self.sample_rate,
            bits=self.bits,
            channels=self.channels,
        )


class VoiceContextMessage(VoiceMessage):
    role: Literal["child", "pet"]
    text: str = Field(min_length=1, max_length=1000)


class SessionStart(VoiceMessage):
    type: Literal["session.start"]
    session_id: str = Field(min_length=1, max_length=200)
    child_id: str = Field(min_length=1, max_length=200)
    learner_profile: LearnerProfile
    audio: VoiceAudioConfig = Field(default_factory=VoiceAudioConfig)
    context: list[VoiceContextMessage] = Field(default_factory=list, max_length=10)


class InputStart(VoiceMessage):
    type: Literal["input.start"]


class InputCommit(VoiceMessage):
    type: Literal["input.commit"]


class InputCancel(VoiceMessage):
    type: Literal["input.cancel"]


class SessionClose(VoiceMessage):
    type: Literal["session.close"]


ClientControlMessage = SessionStart | InputStart | InputCommit | InputCancel | SessionClose


def parse_control_message(raw: str) -> ClientControlMessage:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("Control message must be valid JSON") from exc
    if not isinstance(payload, dict):
        raise TypeError("Control message must be a JSON object")

    message_type = payload.get("type")
    model_by_type: dict[str, type[VoiceMessage]] = {
        "session.start": SessionStart,
        "input.start": InputStart,
        "input.commit": InputCommit,
        "input.cancel": InputCancel,
        "session.close": SessionClose,
    }
    model = model_by_type.get(message_type)
    if model is None:
        raise ValueError("Unsupported control message type")
    try:
        return model.model_validate(payload)
    except ValidationError as exc:
        raise ValueError("Control message payload is invalid") from exc


class VoiceConnection:
    max_audio_bytes = 2_000_000
    max_chunk_bytes = 64_000

    def __init__(
        self,
        websocket: WebSocket,
        *,
        agent_service: AgentService,
        asr_provider: StreamingAsrProvider,
    ) -> None:
        self.websocket = websocket
        self.agent_service = agent_service
        self.asr_provider = asr_provider
        self.session: SessionStart | None = None
        self.audio_queue: asyncio.Queue[bytes | None] | None = None
        self.turn_task: asyncio.Task[None] | None = None
        self.audio_bytes = 0
        self.send_lock = asyncio.Lock()

    async def run(self) -> None:
        await self.websocket.accept()
        try:
            while True:
                await self._reap_finished_turn()
                message = await self.websocket.receive()
                if message["type"] == "websocket.disconnect":
                    break
                if message.get("bytes") is not None:
                    await self._accept_audio(message["bytes"])
                    continue
                text = message.get("text")
                if text is None:
                    await self._send_error("invalid_message", "Expected a JSON control or binary audio frame")
                    continue
                try:
                    control = parse_control_message(text)
                except (TypeError, ValueError) as exc:
                    await self._send_error("invalid_control", str(exc))
                    continue
                should_close = await self._accept_control(control)
                if should_close:
                    break
        except WebSocketDisconnect:
            pass
        finally:
            await self._cancel_turn()

    async def _accept_control(self, control: ClientControlMessage) -> bool:
        if isinstance(control, SessionStart):
            if self.session is not None:
                await self._send_error("session_already_started", "Session has already started")
                return False
            self.session = control
            await self._send(
                {
                    "type": "session.ready",
                    "session_id": control.session_id,
                    "audio": control.audio.model_dump(mode="json"),
                }
            )
            return False

        if self.session is None:
            await self._send_error("session_not_started", "Send session.start first")
            return False

        if isinstance(control, InputStart):
            if self.turn_task is not None:
                await self._send_error("turn_in_progress", "The current voice turn is still active")
                return False
            self.audio_queue = asyncio.Queue(maxsize=64)
            self.audio_bytes = 0
            self.turn_task = asyncio.create_task(self._process_turn(self.audio_queue))
            await self._send({"type": "input.ready"})
            return False

        if isinstance(control, InputCommit):
            if self.audio_queue is None or self.turn_task is None:
                await self._send_error("turn_not_started", "Send input.start before committing audio")
                return False
            await self.audio_queue.put(None)
            await self.turn_task
            self.audio_queue = None
            self.turn_task = None
            self.audio_bytes = 0
            return False

        if isinstance(control, InputCancel):
            await self._cancel_turn()
            await self._send({"type": "input.cancelled"})
            return False

        if isinstance(control, SessionClose):
            await self._send({"type": "session.closed"})
            await self.websocket.close(code=1000)
            return True

        return False

    async def _accept_audio(self, chunk: bytes) -> None:
        if self.audio_queue is None or self.turn_task is None:
            await self._send_error("turn_not_started", "Send input.start before audio")
            return
        if not chunk:
            return
        if len(chunk) > self.max_chunk_bytes:
            await self._send_error("audio_chunk_too_large", "Audio chunks must be at most 64000 bytes")
            return
        if self.audio_bytes + len(chunk) > self.max_audio_bytes:
            await self._send_error("audio_too_long", "Voice turns are limited to about 60 seconds")
            await self._cancel_turn()
            return
        self.audio_bytes += len(chunk)
        await self.audio_queue.put(chunk)

    async def _process_turn(self, queue: asyncio.Queue[bytes | None]) -> None:
        if self.session is None:
            return

        latest_text = ""
        final_text = ""
        confidence = None
        language = None

        async def audio_chunks() -> AsyncIterator[bytes]:
            while True:
                item = await queue.get()
                if item is None:
                    break
                yield item

        try:
            async for transcript in self.asr_provider.transcribe(
                audio_chunks(),
                audio=self.session.audio.to_asr_config(),
                user_id=self.session.child_id,
            ):
                latest_text = transcript.text
                confidence = transcript.confidence
                language = transcript.detected_language
                event_type = "asr.final" if transcript.is_final else "asr.partial"
                await self._send({"type": event_type, "text": transcript.text})
                if transcript.is_final:
                    final_text = transcript.text
        except AsrProviderError:
            await self._send_error(
                "asr_unavailable",
                "Speech recognition is temporarily unavailable",
                retryable=True,
            )
            return

        transcript_text = (final_text or latest_text).strip()
        if not transcript_text:
            await self._send_error("no_speech", "No speech was recognized", retryable=True)
            return

        bytes_per_second = (
            self.session.audio.sample_rate
            * self.session.audio.channels
            * (self.session.audio.bits // 8)
        )
        duration_ms = round(self.audio_bytes / bytes_per_second * 1000)
        request = AgentTurnRequest(
            session_id=self.session.session_id,
            child_id=self.session.child_id,
            transcript=transcript_text,
            learner_profile=self.session.learner_profile,
            audio_metadata=AudioMetadata(
                duration_ms=duration_ms,
                asr_confidence=confidence,
                detected_language=language,
                is_human_voice=True,
            ),
            context=[item.model_dump() for item in self.session.context],
        )
        try:
            response = await self.agent_service.handle_turn(request)
        except Exception as exc:  # noqa: BLE001 -- WebSocket boundary must return a safe error.
            logger.error("Agent voice turn failed type=%s", type(exc).__name__)
            await self._send_error(
                "agent_unavailable",
                "The speaking companion is temporarily unavailable",
                retryable=True,
            )
            return
        self.session.learner_profile = response.learner_profile
        next_context = [*self.session.context]
        next_context.append(VoiceContextMessage(role="child", text=transcript_text))
        next_context.append(VoiceContextMessage(role="pet", text=response.reply_text))
        self.session.context = next_context[-10:]
        await self._send(
            {
                "type": "agent.reply",
                "transcript": transcript_text,
                "turn": response.model_dump(mode="json"),
            }
        )
        await self._send({"type": "turn.completed", "turn_id": response.turn_id})

    async def _reap_finished_turn(self) -> None:
        if self.turn_task is None or not self.turn_task.done():
            return
        await asyncio.gather(self.turn_task, return_exceptions=True)
        self.turn_task = None
        self.audio_queue = None
        self.audio_bytes = 0

    async def _cancel_turn(self) -> None:
        if self.turn_task is not None and not self.turn_task.done():
            self.turn_task.cancel()
            await asyncio.gather(self.turn_task, return_exceptions=True)
        self.turn_task = None
        self.audio_queue = None
        self.audio_bytes = 0

    async def _send(self, payload: dict[str, object]) -> None:
        async with self.send_lock:
            await self.websocket.send_json(payload)

    async def _send_error(self, code: str, message: str, *, retryable: bool = False) -> None:
        await self._send(
            {
                "type": "error",
                "error": {"code": code, "message": message, "retryable": retryable},
            }
        )
