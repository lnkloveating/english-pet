import asyncio
import logging
from collections.abc import AsyncIterable, AsyncIterator
from typing import Protocol
from uuid import uuid4

import websockets

from ..config import Settings
from .models import AsrAudioConfig, AsrTranscript
from .protocol import (
    DoubaoProtocolError,
    decode_server_packet,
    encode_audio_chunk,
    encode_client_config,
    transcript_from_packet,
)

logger = logging.getLogger(__name__)


class AsrProviderError(RuntimeError):
    """A safe provider failure that may be mapped to a client-facing error code."""


class AsrConfigurationError(AsrProviderError):
    pass


class StreamingAsrProvider(Protocol):
    def transcribe(
        self,
        audio_chunks: AsyncIterable[bytes],
        *,
        audio: AsrAudioConfig,
        user_id: str,
    ) -> AsyncIterator[AsrTranscript]: ...


class StubStreamingAsrProvider:
    def __init__(self, transcript: str = "I like cats.") -> None:
        self.transcript = transcript

    async def transcribe(
        self,
        audio_chunks: AsyncIterable[bytes],
        *,
        audio: AsrAudioConfig,
        user_id: str,
    ) -> AsyncIterator[AsrTranscript]:
        _ = (audio, user_id)
        received_audio = False
        async for chunk in audio_chunks:
            if chunk and not received_audio:
                received_audio = True
                yield AsrTranscript(text=self.transcript[: max(1, len(self.transcript) // 2)], is_final=False)
        if received_audio:
            yield AsrTranscript(text=self.transcript, is_final=True, detected_language="en")


class DoubaoStreamingAsrProvider:
    def __init__(
        self,
        *,
        api_key: str | None,
        app_key: str | None,
        access_token: str | None,
        resource_id: str,
        websocket_url: str,
        timeout_seconds: float = 30,
    ) -> None:
        self.api_key = api_key
        self.app_key = app_key
        self.access_token = access_token
        self.resource_id = resource_id
        self.websocket_url = websocket_url
        self.timeout_seconds = timeout_seconds

    def _headers(self, connection_id: str) -> dict[str, str]:
        headers = {
            "X-Api-Resource-Id": self.resource_id,
            "X-Api-Connect-Id": connection_id,
            "X-Api-Request-Id": connection_id,
            "X-Api-Sequence": "-1",
        }
        if self.api_key:
            headers["X-Api-Key"] = self.api_key
            return headers
        if self.app_key and self.access_token:
            headers["X-Api-App-Key"] = self.app_key
            headers["X-Api-Access-Key"] = self.access_token
            return headers
        raise AsrConfigurationError(
            "Doubao ASR credentials are not configured; set DOUBAO_ASR_API_KEY or "
            "DOUBAO_ASR_APP_KEY with DOUBAO_ASR_ACCESS_TOKEN"
        )

    def _client_config(self, audio: AsrAudioConfig, user_id: str) -> dict[str, object]:
        return {
            "user": {"uid": user_id},
            "audio": {
                "format": audio.format,
                "rate": audio.sample_rate,
                "bits": audio.bits,
                "channel": audio.channels,
            },
            "request": {
                "model_name": "bigmodel",
                "enable_itn": True,
                "enable_punc": True,
                "enable_ddc": True,
                "show_utterances": True,
                "result_type": "single",
            },
        }

    async def transcribe(
        self,
        audio_chunks: AsyncIterable[bytes],
        *,
        audio: AsrAudioConfig,
        user_id: str,
    ) -> AsyncIterator[AsrTranscript]:
        connection_id = str(uuid4())
        headers = self._headers(connection_id)

        try:
            async with websockets.connect(
                self.websocket_url,
                additional_headers=headers,
                open_timeout=self.timeout_seconds,
                close_timeout=5,
                max_size=2**20,
            ) as upstream:
                await upstream.send(encode_client_config(self._client_config(audio, user_id)))

                sender_done = asyncio.Event()

                async def send_audio() -> None:
                    try:
                        async for chunk in audio_chunks:
                            if chunk:
                                await upstream.send(encode_audio_chunk(chunk))
                        await upstream.send(encode_audio_chunk(b"", is_last=True))
                    finally:
                        sender_done.set()

                sender = asyncio.create_task(send_audio())
                last_text = ""
                final_sent = False
                try:
                    while True:
                        raw = await asyncio.wait_for(upstream.recv(), timeout=self.timeout_seconds)
                        if not isinstance(raw, bytes):
                            continue
                        packet = decode_server_packet(raw)
                        transcript = transcript_from_packet(packet)
                        if transcript is not None:
                            text, is_final, confidence, language = transcript
                            if text != last_text or is_final:
                                final_sent = final_sent or is_final
                                last_text = text
                                yield AsrTranscript(
                                    text=text,
                                    is_final=is_final,
                                    confidence=confidence,
                                    detected_language=language,
                                )
                        if packet.is_last and sender_done.is_set():
                            break
                    if last_text and not final_sent:
                        yield AsrTranscript(text=last_text, is_final=True)
                finally:
                    if not sender.done():
                        sender.cancel()
                    await asyncio.gather(sender, return_exceptions=True)
        except AsrConfigurationError:
            raise
        except DoubaoProtocolError as exc:
            logger.warning("Doubao ASR protocol failure code=%s", exc.code)
            raise AsrProviderError("Doubao ASR returned an invalid response") from exc
        except TimeoutError as exc:
            raise AsrProviderError("Doubao ASR timed out") from exc
        except websockets.WebSocketException as exc:
            logger.warning("Doubao ASR websocket failure type=%s", type(exc).__name__)
            raise AsrProviderError("Doubao ASR is unavailable") from exc


def build_asr_provider(settings: Settings) -> StreamingAsrProvider:
    if settings.asr_provider == "stub":
        return StubStreamingAsrProvider()
    if settings.asr_provider == "doubao_streaming":
        return DoubaoStreamingAsrProvider(
            api_key=settings.doubao_asr_api_key,
            app_key=settings.doubao_asr_app_key,
            access_token=settings.doubao_asr_access_token,
            resource_id=settings.doubao_asr_resource_id,
            websocket_url=settings.doubao_asr_ws_url,
            timeout_seconds=settings.doubao_asr_timeout_seconds,
        )
    raise AsrConfigurationError(f"Unsupported ASR_PROVIDER: {settings.asr_provider}")
